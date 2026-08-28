"""Named asymmetric multi-panel assemblies."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cache
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
            import matplotlib.pyplot as plt

            plt.close(fig)
