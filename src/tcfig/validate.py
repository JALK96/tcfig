"""Validation of physical dimensions and publication-critical artists."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import JournalProfile, get_profile, get_tokens
from .figure import MM_PER_INCH


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    profile: str
    width_mm: float
    height_mm: float
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    def to_dict(self) -> dict[str, Any]:
        values = asdict(self)
        values["ok"] = self.ok
        return values


def validate_figure(
    fig: Any,
    *,
    profile: str | JournalProfile | None = None,
) -> ValidationReport:
    """Check a Matplotlib figure against its profile.

    Empty internal text artists are ignored. Intentional sub-minimum or hairline
    artists may be tagged with ``artist.set_gid('tcfig-ignore-validation')``.
    """

    metadata = getattr(fig, "_tcfig_metadata", {})
    publication = _resolve_profile(profile, metadata)
    width_in, height_in = fig.get_size_inches()
    width_mm = float(width_in * MM_PER_INCH)
    height_mm = float(height_in * MM_PER_INCH)
    issues: list[ValidationIssue] = []

    expected_width = metadata.get("width_mm")
    expected_height = metadata.get("height_mm")
    tolerance = float(get_tokens()["validation"]["dimension_tolerance_mm"])
    if expected_width is not None and abs(width_mm - float(expected_width)) > tolerance:
        issues.append(
            ValidationIssue(
                "error",
                "dimension-width",
                f"Canvas is {width_mm:.2f} mm wide; expected {float(expected_width):.2f} mm.",
            )
        )
    if expected_height is not None and abs(height_mm - float(expected_height)) > tolerance:
        issues.append(
            ValidationIssue(
                "error",
                "dimension-height",
                f"Canvas is {height_mm:.2f} mm high; expected {float(expected_height):.2f} mm.",
            )
        )
    if height_mm > publication.max_height_mm + tolerance:
        issues.append(
            ValidationIssue(
                "error",
                "height-maximum",
                f"Height {height_mm:.2f} mm exceeds {publication.name} maximum "
                f"{publication.max_height_mm:.2f} mm.",
            )
        )

    issues.extend(_validate_text(fig, publication))
    issues.extend(_validate_lines(fig, publication))
    issues.extend(_validate_colormaps(fig))
    if not publication.verified:
        issues.append(
            ValidationIssue(
                "warning",
                "profile-unverified",
                f"Profile '{publication.name}' is a working profile; verify the target journal.",
            )
        )

    return ValidationReport(
        profile=publication.name,
        width_mm=width_mm,
        height_mm=height_mm,
        issues=tuple(issues),
    )


def _resolve_profile(
    profile: str | JournalProfile | None, metadata: dict[str, Any]
) -> JournalProfile:
    if isinstance(profile, JournalProfile):
        return profile
    if isinstance(profile, str):
        return get_profile(profile)
    return get_profile(metadata.get("profile", "house"))


def _ignored(artist: Any) -> bool:
    return getattr(artist, "get_gid", lambda: None)() == "tcfig-ignore-validation"


def _validate_text(fig: Any, profile: JournalProfile) -> list[ValidationIssue]:
    from matplotlib.text import Text

    issues: list[ValidationIssue] = []
    too_small: list[tuple[str, float]] = []
    too_large: list[tuple[str, float]] = []
    for artist in fig.findobj(match=Text):
        if _ignored(artist) or not artist.get_visible() or not artist.get_text().strip():
            continue
        size = float(artist.get_fontsize())
        label = artist.get_text().strip().replace("\n", " ")[:32]
        if size + 1e-6 < profile.min_font_pt:
            too_small.append((label, size))
        if size - 1e-6 > profile.max_font_pt:
            too_large.append((label, size))
    if too_small:
        examples = ", ".join(f"'{label}' ({size:g} pt)" for label, size in too_small[:3])
        issues.append(
            ValidationIssue(
                "error",
                "font-too-small",
                f"Text below {profile.min_font_pt:g} pt: {examples}.",
            )
        )
    if too_large:
        examples = ", ".join(f"'{label}' ({size:g} pt)" for label, size in too_large[:3])
        issues.append(
            ValidationIssue(
                "warning",
                "font-too-large",
                f"Text above {profile.max_font_pt:g} pt: {examples}.",
            )
        )
    return issues


def _validate_lines(fig: Any, profile: JournalProfile) -> list[ValidationIssue]:
    from matplotlib.lines import Line2D

    thin: list[float] = []
    for artist in fig.findobj(match=Line2D):
        if _ignored(artist) or not artist.get_visible():
            continue
        xdata = artist.get_xdata(orig=False)
        if getattr(xdata, "size", len(xdata) if hasattr(xdata, "__len__") else 0) == 0:
            continue
        width = float(artist.get_linewidth())
        if width and width + 1e-6 < profile.min_line_pt:
            thin.append(width)
    if not thin:
        return []
    return [
        ValidationIssue(
            "warning",
            "line-too-thin",
            f"Found {len(thin)} line(s) below {profile.min_line_pt:g} pt; "
            f"minimum was {min(thin):g} pt.",
        )
    ]


def _validate_colormaps(fig: Any) -> list[ValidationIssue]:
    forbidden = set(get_tokens()["validation"]["forbidden_colormaps"])
    used: set[str] = set()
    for axes in fig.axes:
        mappables = list(axes.images) + list(axes.collections)
        for artist in mappables:
            cmap = getattr(artist, "get_cmap", lambda: None)()
            if cmap is not None and cmap.name in forbidden:
                used.add(cmap.name)
    if not used:
        return []
    return [
        ValidationIssue(
            "error",
            "forbidden-colormap",
            f"Forbidden colormap(s): {', '.join(sorted(used))}.",
        )
    ]

