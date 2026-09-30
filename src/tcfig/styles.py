"""Matplotlib style construction."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from .config import JournalProfile, get_profile, get_tokens
from .fonts import register_fonts


def rc_params(profile: str | JournalProfile = "house", typesetting: str = "mathtext") -> dict[str, Any]:
    """Build rcParams without modifying global rcParams.

    ``typesetting`` is "mathtext" (Matplotlib text/math with bundled Liberation
    Sans) or "latex-<set>" for a LaTeX font set from the design tokens; LaTeX
    typesetting applies when a figure is saved through the pgf backend (export()).
    Bundled fonts are registered with Matplotlib's font manager (idempotent).
    """

    register_fonts()
    publication = get_profile(profile) if isinstance(profile, str) else profile
    tokens = get_tokens()
    typography = tokens["typography"]
    line = tokens["line"]
    marker = tokens["marker"]
    colors = tokens["color"]
    foreground = colors["semantic"]["foreground"]
    group_label = colors["semantic"]["group_label"]
    bright = colors["palettes"]["tol_bright"]

    return {
        "font.family": "sans-serif",
        "font.sans-serif": list(typography["families"]),
        "font.size": publication.base_font_pt,
        "mathtext.fontset": typography["math_family"],
        **_math_letters(typography),
        "axes.labelsize": publication.base_font_pt,
        "axes.titlesize": publication.base_font_pt,
        "axes.titlecolor": group_label,
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
        "figure.labelsize": publication.base_font_pt,
        "figure.titlesize": publication.base_font_pt,
        "figure.facecolor": colors["semantic"]["background"],
        "figure.edgecolor": colors["semantic"]["background"],
        "savefig.facecolor": colors["semantic"]["background"],
        "savefig.edgecolor": colors["semantic"]["background"],
        "savefig.bbox": None,
        "savefig.pad_inches": 0.0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        **_latex_params(typography, typesetting),
    }


def _math_letters(typography: dict[str, Any]) -> dict[str, str]:
    """Custom math fonts: letters from the text family, symbols from the fallback set."""

    if typography["math_family"] != "custom":
        return {}
    family = typography["families"][0]
    return {
        "mathtext.rm": family,
        "mathtext.sf": family,
        "mathtext.it": f"{family}:italic",
        "mathtext.bf": f"{family}:bold",
        "mathtext.cal": f"{family}:italic",  # no calligraphic face; avoids a missing-font fallback
        "mathtext.fallback": typography["math_fallback"],
    }


def typesetting_options() -> tuple[str, ...]:
    """Available values for the ``typesetting`` argument."""

    return ("mathtext", *(f"latex-{name}" for name, value in
                          get_tokens()["typography"]["latex"].items() if isinstance(value, dict)))


def _latex_params(typography: dict[str, Any], typesetting: str) -> dict[str, Any]:
    """pgf/LuaLaTeX settings: text and math fonts from one designed font set."""

    if typesetting == "mathtext":
        return {}
    latex = typography["latex"]
    name = typesetting.removeprefix("latex-")
    if not typesetting.startswith("latex-") or not isinstance(latex.get(name), dict):
        raise ValueError(f"Unknown typesetting {typesetting!r}; choose from {typesetting_options()}.")
    fonts = latex[name]
    preamble = "\n".join([
        r"\usepackage{fontspec}",
        r"\usepackage{unicode-math}",
        rf"\setmainfont{{{fonts['text']}}}",
        rf"\setsansfont{{{fonts['text']}}}",
        rf"\setmathfont{{{fonts['math']}}}",
    ])
    return {
        "pgf.texsystem": latex["texsystem"],
        "pgf.rcfonts": False,
        "pgf.preamble": preamble,
    }


def panel_label_size(profile: str | JournalProfile | None = None) -> float:
    """Return the semantic panel-label size for a profile or active style context."""

    if profile is None:
        try:
            import matplotlib as mpl
        except ImportError as exc:
            raise RuntimeError("tcfig plotting requires Matplotlib.") from exc
        base_size = float(mpl.rcParams["font.size"])
    else:
        publication = get_profile(profile) if isinstance(profile, str) else profile
        base_size = float(publication.base_font_pt)
    delta = float(get_tokens()["typography"]["panel_label_delta_pt"])
    return base_size + delta


def _cycler(colors: list[str]):
    try:
        from cycler import cycler
    except ImportError as exc:  # pragma: no cover - Matplotlib depends on cycler.
        raise RuntimeError("Matplotlib's cycler dependency is unavailable.") from exc
    return cycler(color=colors)


@contextmanager
def style_context(
    profile: str | JournalProfile = "house", typesetting: str = "mathtext"
) -> Iterator[JournalProfile]:
    """Temporarily activate the profile while a plot is constructed."""

    try:
        import matplotlib as mpl
    except ImportError as exc:
        raise RuntimeError("tcfig plotting requires Matplotlib. Install the project first.") from exc

    publication = get_profile(profile) if isinstance(profile, str) else profile
    with mpl.rc_context(rc=rc_params(publication, typesetting)):
        yield publication
