"""Named asymmetric multi-panel assemblies."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cache
from math import isclose, isfinite
from typing import Any

from .config import JournalProfile, get_profile, get_tokens
from .figure import MM_PER_INCH, resolve_size_mm
from .styles import style_context


@dataclass(frozen=True)
class AssemblySpec:
    """Declarative layout made from named, possibly spanning panel slots."""

    name: str
    description: str
    mosaic: tuple[str, ...]
    width_ratios: tuple[float, ...]
    height_ratios: tuple[float, ...]
    default_width: str
    default_height: str

    @property
    def panel_names(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys("".join(self.mosaic)))


@dataclass(frozen=True)
class FixedTrack:
    """A GridSpec track with a requested physical extent in millimetres."""

    mm: float

    def __post_init__(self) -> None:
        if not isfinite(self.mm) or self.mm <= 0:
            raise ValueError("A fixed track must have a positive extent.")


def fixed_mm(value: float) -> FixedTrack:
    """Declare a fixed-width or fixed-height GridSpec track in millimetres."""

    return FixedTrack(float(value))


def resolve_track_ratios(
    tracks: Sequence[float | FixedTrack],
    *,
    available_mm: float,
) -> tuple[float, ...]:
    """Resolve relative and fixed physical tracks to GridSpec ratios.

    Numeric entries are relative data-track weights. :func:`fixed_mm` entries
    reserve physical space. ``available_mm`` must describe the GridSpec region,
    excluding outer margins and any separate ``wspace`` or ``hspace``.
    """

    if not tracks:
        raise ValueError("At least one track is required.")
    available = float(available_mm)
    if not isfinite(available) or available <= 0:
        raise ValueError("available_mm must be positive.")

    fixed_total = sum(track.mm for track in tracks if isinstance(track, FixedTrack))
    relative_values = [float(track) for track in tracks if not isinstance(track, FixedTrack)]
    relative_total = sum(relative_values)
    if any(not isfinite(track) or track <= 0 for track in relative_values):
        raise ValueError("Relative track weights must be positive.")
    if relative_total <= 0:
        if not isclose(fixed_total, available):
            raise ValueError("Fixed-only tracks must sum to available_mm.")
        return tuple(track.mm for track in tracks if isinstance(track, FixedTrack))
    if fixed_total >= available:
        raise ValueError("Fixed tracks must leave positive space for relative tracks.")

    relative_scale = (available - fixed_total) / relative_total
    return tuple(
        track.mm if isinstance(track, FixedTrack) else float(track) * relative_scale
        for track in tracks
    )


@cache
def get_assembly(name: str) -> AssemblySpec:
    """Resolve a named asymmetric assembly."""

    assemblies = get_tokens()["layout"]["assemblies"]
    canonical = name.lower().replace("-", "_")
    if canonical not in assemblies:
        choices = ", ".join(sorted(assemblies))
        raise ValueError(f"Unknown assembly '{name}'. Available: {choices}.")
    values = assemblies[canonical]
    return AssemblySpec(
        name=canonical,
        description=str(values["description"]),
        mosaic=tuple(str(row) for row in values["mosaic"]),
        width_ratios=tuple(float(value) for value in values["width_ratios"]),
        height_ratios=tuple(float(value) for value in values["height_ratios"]),
        default_width=str(values["default_width"]),
        default_height=str(values["default_height"]),
    )


def available_assemblies() -> tuple[str, ...]:
    """Return all named assembly patterns."""

    return tuple(sorted(get_tokens()["layout"]["assemblies"]))


@contextmanager
def assembly_canvas(
    name: str,
    *,
    profile: str | JournalProfile = "house",
    width: str | float | None = None,
    height: str | float | None = None,
    close: bool = False,
    **kwargs: Any,
) -> Iterator[tuple[Any, dict[str, Any]]]:
    """Create an exact-size figure using a named asymmetric panel mosaic."""

    publication = get_profile(profile) if isinstance(profile, str) else profile
    spec = get_assembly(name)
    chosen_width = width if width is not None else spec.default_width
    chosen_height = height if height is not None else spec.default_height
    width_mm, height_mm = resolve_size_mm(publication, chosen_width, chosen_height)
    gap_mm = float(get_tokens()["layout"]["panel_gap_mm"])

    with style_context(publication):
        import matplotlib.pyplot as plt

        fig = plt.figure(
            figsize=(width_mm / MM_PER_INCH, height_mm / MM_PER_INCH),
            layout="constrained",
            **kwargs,
        )
        layout_engine = fig.get_layout_engine()
        if layout_engine is not None:
            half_gap_in = gap_mm / (2 * MM_PER_INCH)
            layout_engine.set(w_pad=half_gap_in, h_pad=half_gap_in, wspace=0, hspace=0)
        axes = fig.subplot_mosaic(
            [list(row) for row in spec.mosaic],
            gridspec_kw={
                "width_ratios": spec.width_ratios,
                "height_ratios": spec.height_ratios,
            },
        )
        fig._tcfig_metadata = {  # type: ignore[attr-defined]
            "profile": publication.name,
            "profile_label": publication.label,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "width_slot": chosen_width if isinstance(chosen_width, str) else "custom",
            "height_slot": chosen_height if isinstance(chosen_height, str) else "custom",
            "assembly": spec.name,
            "panel_gap_mm": gap_mm,
        }
        try:
            yield fig, axes
        finally:
            if close:
                plt.close(fig)
