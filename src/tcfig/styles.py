"""Matplotlib style construction."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from .config import JournalProfile, get_profile, get_tokens


def rc_params(profile: str | JournalProfile = "house") -> dict[str, Any]:
    """Build rcParams without modifying global Matplotlib state."""

    publication = get_profile(profile) if isinstance(profile, str) else profile
    tokens = get_tokens()
    typography = tokens["typography"]
    line = tokens["line"]
    marker = tokens["marker"]
    colors = tokens["color"]
    foreground = colors["semantic"]["foreground"]
    bright = colors["palettes"]["tol_bright"]

    return {
        "font.family": "sans-serif",
        "font.sans-serif": list(typography["families"]),
        "font.size": publication.base_font_pt,
        "mathtext.fontset": typography["math_family"],
        "axes.labelsize": publication.base_font_pt,
        "axes.titlesize": publication.base_font_pt,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.linewidth": line["axis_pt"],
        "axes.edgecolor": foreground,
        "axes.labelcolor": foreground,
        "axes.facecolor": colors["semantic"]["background"],
        "axes.grid": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.prop_cycle": _cycler(bright),
        "xtick.labelsize": publication.base_font_pt,
        "ytick.labelsize": publication.base_font_pt,
        "xtick.color": foreground,
        "ytick.color": foreground,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": line["axis_pt"],
        "ytick.major.width": line["axis_pt"],
        "xtick.minor.width": line["axis_pt"],
        "ytick.minor.width": line["axis_pt"],
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "lines.linewidth": line["data_pt"],
        "lines.markersize": marker["size_pt"],
        "lines.markeredgewidth": marker["edge_pt"],
        "patch.linewidth": line["axis_pt"],
        "legend.fontsize": publication.base_font_pt,
        "legend.frameon": False,
        "legend.handlelength": 1.8,
        "legend.handletextpad": 0.5,
        "legend.borderaxespad": 0.2,
        "text.color": foreground,
        "figure.facecolor": colors["semantic"]["background"],
        "figure.edgecolor": colors["semantic"]["background"],
        "savefig.facecolor": colors["semantic"]["background"],
        "savefig.edgecolor": colors["semantic"]["background"],
        "savefig.bbox": None,
        "savefig.pad_inches": 0.0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }


def _cycler(colors: list[str]):
    try:
        from cycler import cycler
    except ImportError as exc:  # pragma: no cover - Matplotlib depends on cycler.
        raise RuntimeError("Matplotlib's cycler dependency is unavailable.") from exc
    return cycler(color=colors)


@contextmanager
def style_context(profile: str | JournalProfile = "house") -> Iterator[JournalProfile]:
    """Temporarily activate the profile while a plot is constructed."""

    try:
        import matplotlib as mpl
    except ImportError as exc:
        raise RuntimeError("tcfig plotting requires Matplotlib. Install the project first.") from exc

    publication = get_profile(profile) if isinstance(profile, str) else profile
    with mpl.rc_context(rc=rc_params(publication)):
        yield publication
