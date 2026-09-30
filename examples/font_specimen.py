"""Font and math specimen for every typesetting option.

Run: python examples/font_specimen.py [VARIANT ...]
Writes examples/output/font-specimen-<variant>.pdf. The two "compare-*" variants
are not tcfig options; they show Matplotlib's built-in math font sets next to the
default for judging how mixed glyphs look. LaTeX variants need LuaLaTeX.
"""

from pathlib import Path
import sys

import matplotlib as mpl
import numpy as np

mpl.use("Agg")

import matplotlib.pyplot as plt

import tcfig

OUTPUT = Path(__file__).with_name("output")
SEP = r" $\quad$ "  # LaTeX collapses repeated spaces; \quad works in both engines
LINES = [
    ("Text", r"Ca$^{2+}$ coordination at 0.25 nm, $-1.5 \pm 0.2$, 10$^{-3}$ s"),
    ("Axis labels", SEP.join([r"Distance, $r$ (nm)", r"$c_\mathrm{eq}$ (mM)", r"$N_\mathrm{coord}$",
                              r"$\Delta G$ (kJ mol$^{-1}$)"])),
    ("Greek", r"$\alpha\ \beta\ \gamma\ \theta\ \phi\ \chi^2\ \sigma\ \tau_\mathrm{int}\ \Omega$"),
    ("Brackets, roots", SEP.join([r"$\langle N \rangle \pm \sigma$", r"$\sqrt{\langle x^2 \rangle}$",
                                  r"$|q_i|$", r"$(a+b)^2$"])),
    ("Calculus", SEP.join([r"$\partial F / \partial \theta$", r"$\nabla U$", r"$\sum_i q_i$",
                           r"$\int_0^{r_c} g(r)\,4\pi r^2\,\mathrm{d}r$"])),
    ("Relations", SEP.join([r"$a \leq b$", r"$x \approx 0.3$", r"$y \propto x^{-1}$", r"$t \to \infty$",
                            r"$A \neq B$"])),
    ("Ions", SEP.join([r"HPO$_4^{2-}$", r"Mg$^{2+}$", r"Na$^{+}$", r"Cl$^{-}$"])),
]
COMPARE = {"compare-stixsans": {"mathtext.fontset": "stixsans"},
           "compare-dejavusans": {"mathtext.fontset": "dejavusans"}}


def draw(fig, ax, title):
    r = np.linspace(0.15, 0.8, 400)
    ax.plot(r, 1 + 6 * np.exp(-((r - 0.25) / 0.02) ** 2) + 0.4 * np.exp(-((r - 0.45) / 0.05) ** 2))
    ax.set_xlabel(r"Distance, $r$ (nm)")
    ax.set_ylabel(r"$g(r)$")
    fig.text(0.42, 0.93, title, fontweight="bold", va="top")
    for i, (label, text) in enumerate(LINES):
        y = 0.80 - i * 0.105
        fig.text(0.42, y, label, color=tcfig.semantic_color("group_label"), va="center")
        fig.text(0.56, y, text, va="center")


def specimen(variant):
    OUTPUT.mkdir(exist_ok=True)
    target = OUTPUT / f"font-specimen-{variant}"
    typesetting = "mathtext" if variant in COMPARE else variant
    with tcfig.canvas(profile="jcp", width="double", height=75, layout=None,
                      typesetting=typesetting) as (fig, ax):
        # Matplotlib fixes a text's math font set when the text is created.
        with mpl.rc_context(COMPARE.get(variant, {})):
            fig.subplots_adjust(left=0.07, right=0.34, bottom=0.2, top=0.9)
            draw(fig, ax, variant)
    if variant in COMPARE:
        # Not a tcfig option: override only the math font set, save directly.
        with tcfig.style_context("jcp"), mpl.rc_context(COMPARE[variant]):
            fig.savefig(target.with_suffix(".pdf"))
    else:
        tcfig.export(fig, target, formats=("pdf",), profile="jcp", fail_on_error=False)
    plt.close(fig)
    print(target.with_suffix(".pdf"))


if __name__ == "__main__":
    for name in sys.argv[1:] or [*tcfig.typesetting_options(), *COMPARE]:
        specimen(name)
