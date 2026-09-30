"""Bundled fonts: register them with Matplotlib and list files for external editing."""

from __future__ import annotations

from pathlib import Path

FONT_DIR = Path(__file__).with_name("fonts")


def register_fonts() -> list[Path]:
    """Add bundled TrueType fonts to Matplotlib's in-memory font manager.

    This avoids depending on system fonts or on a stale Matplotlib font cache.
    Nothing is written to the user's cache.
    """

    try:
        from matplotlib import font_manager
    except ImportError:  # pragma: no cover - plotting requires Matplotlib.
        return []
    registered = sorted(FONT_DIR.glob("*.ttf"))
    known = {entry.fname for entry in font_manager.fontManager.ttflist}
    for path in registered:
        if str(path) not in known:
            font_manager.fontManager.addfont(str(path))
    return registered


def font_files() -> list[Path]:
    """Font files an exported figure can embed: bundled text fonts plus Matplotlib's STIX math fonts.

    Install these on a machine where exported PDF/SVG text should stay editable.
    """

    import matplotlib

    stix = sorted((Path(matplotlib.get_data_path()) / "fonts" / "ttf").glob("STIX*.ttf"))
    return sorted(FONT_DIR.glob("*.ttf")) + stix
