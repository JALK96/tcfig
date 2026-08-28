"""Semantic palettes, redundant condition styles and scientific colormaps."""

from __future__ import annotations

import warnings
from typing import Any

from .config import get_tokens


def palette(name: str = "tol_bright") -> tuple[str, ...]:
    palettes = get_tokens()["color"]["palettes"]
    if name not in palettes:
        choices = ", ".join(sorted(palettes))
        raise ValueError(f"Unknown palette '{name}'. Available: {choices}.")
    return tuple(palettes[name])


def semantic_color(name: str) -> str:
    colors = get_tokens()["color"]["semantic"]
    if name not in colors:
        choices = ", ".join(sorted(colors))
        raise ValueError(f"Unknown semantic color '{name}'. Available: {choices}.")
    return str(colors[name])


def condition_styles(count: int, name: str = "tol_bright") -> tuple[dict[str, Any], ...]:
    """Return color + marker + line combinations for redundant encoding."""

    if count < 1:
        return ()
    colors = palette(name)
    markers = ("o", "s", "^", "D", "v", "P", "X", "<", ">")
    linestyles = ("-", "--", "-.", ":")
    result = []
    for index in range(count):
        cycle_index = index // len(colors)
        result.append(
            {
                "color": colors[index % len(colors)],
                "marker": markers[index % len(markers)],
                "linestyle": linestyles[cycle_index % len(linestyles)],
            }
        )
    return tuple(result)


def get_cmap(role: str = "scientific_sequential"):
    """Get a role-based colormap, preferring Crameri maps when installed."""

    import matplotlib as mpl
    from matplotlib.colors import LinearSegmentedColormap

    names = get_tokens()["color"]["colormaps"]
    anchors = get_tokens()["color"].get("colormap_anchors", {})
    if role in names:
        requested = str(names[role])
    elif role in anchors:
        requested = role
    else:
        choices = ", ".join(sorted(set(names) | set(anchors)))
        raise ValueError(f"Unknown colormap role '{role}'. Available: {choices}.")

    if requested in anchors:
        return LinearSegmentedColormap.from_list(requested, anchors[requested])
    if requested in mpl.colormaps:
        return mpl.colormaps[requested]

    if requested in {"batlow", "vik", "romaO"}:
        try:
            import cmcrameri.cm as cmc

            return getattr(cmc, requested)
        except (ImportError, AttributeError):
            fallback_role = {
                "batlow": "fallback_sequential",
                "vik": "fallback_diverging",
                "romaO": "fallback_cyclic",
            }[requested]
            fallback = str(names[fallback_role])
            warnings.warn(
                f"Colormap '{requested}' requires cmcrameri; using '{fallback}'.",
                stacklevel=2,
            )
            return mpl.colormaps[fallback]
    return mpl.colormaps[requested]
