"""Deterministic export with validation, metadata and optional data sidecars."""

from __future__ import annotations

import csv
import json
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from . import __version__
from .config import JournalProfile, get_profile, get_tokens
from .styles import style_context
from .validate import ValidationReport, validate_figure


@dataclass(frozen=True)
class ExportResult:
    files: tuple[Path, ...]
    metadata_file: Path
    data_files: tuple[Path, ...]
    validation: ValidationReport


def export(
    fig: Any,
    destination: str | Path,
    *,
    formats: Sequence[str] | None = None,
    profile: str | JournalProfile | None = None,
    dpi: int | None = None,
    transparent: bool | None = None,
    data: Mapping[str, Any] | None = None,
    alt_text: str | None = None,
    source_path: str | Path | None = None,
    fail_on_error: bool = True,
) -> ExportResult:
    """Export exact-size figure files and a machine-readable audit record."""

    base = Path(destination).expanduser()
    base = base.with_suffix("") if base.suffix else base
    base.parent.mkdir(parents=True, exist_ok=True)

    metadata = getattr(fig, "_tcfig_metadata", {})
    publication = _resolve_profile(profile, metadata)
    report = validate_figure(fig, profile=publication)
    if fail_on_error and not report.ok:
        details = "; ".join(issue.message for issue in report.issues if issue.severity == "error")
        raise ValueError(f"Figure validation failed: {details}")

    tokens = get_tokens()
    chosen_formats = tuple(formats or tokens["export"]["formats"])
    invalid = set(chosen_formats) - {"pdf", "svg", "png"}
    if invalid:
        raise ValueError(f"Unsupported export format(s): {', '.join(sorted(invalid))}.")
    chosen_dpi = int(dpi or tokens["export"]["png_dpi"])
    chosen_transparency = (
        bool(tokens["export"]["transparent"]) if transparent is None else transparent
    )

    files: list[Path] = []
    # Save inside the profile style: font embedding (TrueType in PDF/PS, text in
    # SVG) and math fonts are read at save time, not when the figure was built.
    with style_context(publication):
        for format_name in chosen_formats:
            path = base.with_suffix(f".{format_name}")
            save_kwargs: dict[str, Any] = {
                "format": format_name,
                "transparent": chosen_transparency,
            }
            if format_name == "png":
                save_kwargs["dpi"] = chosen_dpi
            fig.savefig(path, **save_kwargs)
            files.append(path)

    data_files = _write_data(base, data) if data else ()
    audit = {
        "created_utc": datetime.now(UTC).isoformat(),
        "tcfig_version": __version__,
        "profile": publication.name,
        "profile_label": publication.label,
        "profile_source": publication.source,
        "profile_verified": publication.verified,
        "dimensions_mm": {"width": report.width_mm, "height": report.height_mm},
        "assembly": metadata.get("assembly"),
        "base_font_pt": publication.base_font_pt,
        "formats": list(chosen_formats),
        "png_dpi": chosen_dpi if "png" in chosen_formats else None,
        "transparent": chosen_transparency,
        "alt_text": alt_text,
        "source_path": str(Path(source_path).resolve()) if source_path else None,
        "git_revision": _git_revision(base.parent),
        "validation": report.to_dict(),
        "files": [path.name for path in files],
        "data_files": [path.name for path in data_files],
    }
    metadata_file = base.with_suffix(".figure.json")
    metadata_file.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    return ExportResult(tuple(files), metadata_file, tuple(data_files), report)


def _resolve_profile(
    profile: str | JournalProfile | None, metadata: dict[str, Any]
) -> JournalProfile:
    if isinstance(profile, JournalProfile):
        return profile
    if isinstance(profile, str):
        return get_profile(profile)
    return get_profile(metadata.get("profile", "house"))


def _write_data(base: Path, data: Mapping[str, Any]) -> tuple[Path, ...]:
    arrays = {name: np.asarray(value) for name, value in data.items()}
    npz_path = base.with_suffix(".data.npz")
    np.savez_compressed(npz_path, **arrays)
    paths: list[Path] = [npz_path]

    lengths = {array.size for array in arrays.values() if array.ndim == 1}
    if arrays and len(lengths) == 1 and all(array.ndim == 1 for array in arrays.values()):
        csv_path = base.with_suffix(".data.csv")
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(arrays)
            writer.writerows(zip(*(array.tolist() for array in arrays.values()), strict=True))
        paths.append(csv_path)
    return tuple(paths)


def _git_revision(start: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=start,
            capture_output=True,
            text=True,
            check=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None
