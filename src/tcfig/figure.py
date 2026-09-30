"""Create exact-size figures and multi-panel canvases."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import Any

from .config import JournalProfile, get_profile, get_tokens
from .styles import panel_label_size, style_context

MM_PER_INCH = 25.4


def resolve_size_mm(
    profile: str | JournalProfile = "house",
    width: str | float = "single",
    height: str | float = "standard",
) -> tuple[float, float]:
    """Resolve semantic or explicit dimensions to millimetres."""

    publication = get_profile(profile) if isinstance(profile, str) else profile
    if isinstance(width, str):
        width_mm = publication.width_mm(width)
        width_slot = width if width in {"single", "intermediate", "double"} else "single"
    else:
        width_mm = float(width)
        width_slot = min(
            ("single", "intermediate", "double"),
            key=lambda name: abs(
                width_mm - publication.widths_mm.get(name, publication.widths_mm["single"])
            ),
        )

    if isinstance(height, str):
        heights = get_tokens()["layout"]["heights_mm"][width_slot]
        if height not in heights:
            choices = ", ".join(sorted(heights))
            raise ValueError(f"Unknown height '{height}'. Available: {choices}.")
        height_mm = float(heights[height])
    else:
        height_mm = float(height)

    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Figure dimensions must be positive.")
    if height_mm > publication.max_height_mm:
        raise ValueError(
            f"Height {height_mm:g} mm exceeds the {publication.name} maximum "
            f"of {publication.max_height_mm:g} mm."
        )
    return width_mm, height_mm


def figure(
    *,
    profile: str | JournalProfile = "house",
    width: str | float = "single",
    height: str | float = "standard",
    nrows: int = 1,
    ncols: int = 1,
    sharex: bool | str = False,
    sharey: bool | str = False,
    layout: str | None = "constrained",
    **kwargs: Any,
):
    """Create a styled Matplotlib figure at exact final dimensions.

    For annotations created after this call, the recommended API is :func:`canvas`,
    which keeps the profile active for the entire plotting block.
    """

    publication = get_profile(profile) if isinstance(profile, str) else profile
    width_mm, height_mm = resolve_size_mm(publication, width, height)
    with style_context(publication):
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(
            nrows=nrows,
            ncols=ncols,
            sharex=sharex,
            sharey=sharey,
            figsize=(width_mm / MM_PER_INCH, height_mm / MM_PER_INCH),
            layout=layout,
            **kwargs,
        )
    fig._tcfig_metadata = {  # type: ignore[attr-defined]
        "profile": publication.name,
        "profile_label": publication.label,
        "width_mm": width_mm,
        "height_mm": height_mm,
        "width_slot": width if isinstance(width, str) else "custom",
        "height_slot": height if isinstance(height, str) else "custom",
    }
    return fig, axes


@contextmanager
def canvas(
    *,
    profile: str | JournalProfile = "house",
    width: str | float = "single",
    height: str | float = "standard",
    nrows: int = 1,
    ncols: int = 1,
    sharex: bool | str = False,
    sharey: bool | str = False,
    layout: str | None = "constrained",
    close: bool = False,
    **kwargs: Any,
) -> Iterator[tuple[Any, Any]]:
    """Recommended context API for constructing a complete figure."""

    publication = get_profile(profile) if isinstance(profile, str) else profile
    with style_context(publication):
        fig, axes = figure(
            profile=publication,
            width=width,
            height=height,
            nrows=nrows,
            ncols=ncols,
            sharex=sharex,
            sharey=sharey,
            layout=layout,
            **kwargs,
        )
        try:
            yield fig, axes
        finally:
            if close:
                import matplotlib.pyplot as plt

                plt.close(fig)


def label_panels(
    axes: Any,
    labels: Sequence[str] | None = None,
    *,
    x: float = -0.16,
    y: float = 1.04,
    fontsize: float | None = None,
) -> list[Any]:
    """Place consistent lower-case panel labels in axes coordinates.

    The default size is the active profile's base font plus the panel-label
    increment defined in the design tokens.
    """

    import numpy as np

    if isinstance(axes, Mapping):
        flat = list(axes.values())
    else:
        flat = list(np.asarray(axes, dtype=object).reshape(-1))
    panel_labels = labels or tuple(chr(ord("a") + index) for index in range(len(flat)))
    if len(panel_labels) != len(flat):
        raise ValueError("The number of panel labels must match the number of axes.")
    resolved_fontsize = panel_label_size() if fontsize is None else float(fontsize)
    panel_color = str(get_tokens()["color"]["semantic"]["foreground"])
    return [
        ax.text(
            x,
            y,
            label,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=resolved_fontsize,
            fontweight="bold",
            color=panel_color,
            clip_on=False,
        )
        for ax, label in zip(flat, panel_labels, strict=True)
    ]
