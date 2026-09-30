"""Bundled fonts resolve without system fonts and export as editable TrueType text."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

import tcfig
from tcfig.fonts import FONT_DIR


def test_bundled_text_font_resolves_from_package():
    tcfig.register_fonts()
    path = Path(font_manager.findfont("Liberation Sans", fallback_to_default=False))
    assert path.parent == FONT_DIR
    assert any(p.name.startswith("STIX") for p in tcfig.font_files())


def test_pdf_export_embeds_truetype_text_and_math(tmp_path):
    with tcfig.canvas(profile="jcp", width="single", height=50, close=False) as (fig, ax):
        ax.plot([0, 1], [0, 1])
        ax.set_xlabel(r"Distance, $r$ (nm)")
        ax.set_ylabel(r"$\langle g(r) \rangle$, $\sqrt{\alpha}$")  # symbols absent from Liberation Sans
    result = tcfig.export(fig, tmp_path / "fonts", formats=("pdf", "svg"), profile="jcp")
    plt.close(fig)
    pdf = (tmp_path / "fonts.pdf").read_bytes()
    assert b"/Type3" not in pdf  # Type 3 glyph drawings are not editable text
    assert b"LiberationSans" in pdf and b"LiberationSans-Italic" in pdf  # text and math letters
    assert b"STIXGeneral" in pdf  # symbols missing from Liberation Sans come from STIX
    svg = (tmp_path / "fonts.svg").read_text()
    assert "Liberation Sans" in svg and "<text" in svg  # SVG keeps text as text
    assert result.validation.ok
