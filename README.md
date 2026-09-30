# tcfig

`tcfig` ist ein persönliches Abbildungs-Designsystem für theoretische Chemie und
Molecular Dynamics. Es verbindet ein verbindliches Regelwerk mit einem dünnen
Python-Wrapper über Matplotlib und passenden Kompositionsrastern für Affinity.

Der wichtigste Grundsatz lautet:

> Eine Abbildung wird in ihrer endgültigen physischen Größe erzeugt und danach
> mit 100 % platziert. Schriftgrößen, Linien und Marker werden nicht durch
> nachträgliches Skalieren verändert.

## Enthalten

- maschinenlesbare Design-Tokens und Journal-Profile
- Profile für JCTC/ACS, JCP/AIP, PCCP/RSC, JCC/Wiley, Springer, Elsevier und Nature
- semantische, farbenblindfreundliche Paletten
- MD-spezifische Plotbausteine für Replikate, Verteilungen, freie Energien und RDFs
- sechs benannte asymmetrische Assemblies für Wide-, Long- und Lead/Detail-Figures
- semantische Panelbuchstaben, konsistente Größen-/Einheitenlabels und feste
  Abstandsspuren in Millimetern
- graue Gruppenüberschriften bei schwarzen Panelbuchstaben
- Export als PDF, SVG und PNG ohne `bbox_inches="tight"`
- Prüfung von Maßen, Schriftgrößen, Linien und problematischen Colormaps
- Affinity-kompatible SVG-Raster und eine ASE-Farbpalette
- Beispielgalerie und Tests

## Schnellstart

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev,scientific-colormaps]'
```

```python
import numpy as np
import tcfig

x = np.linspace(0, 10, 200)

with tcfig.canvas(profile="jctc", width="single", height="standard") as (fig, ax):
    ax.plot(x, np.sin(x), label="Reference")
    ax.set(xlabel="Time (ps)", ylabel="Observable")
    ax.legend()
    tcfig.export(fig, "figure_01", data={"time_ps": x, "observable": np.sin(x)})
```

Asymmetrische Kompositionen verwenden dieselben Profile und Endmaße:

```python
with tcfig.assembly_canvas("lead_right", profile="jctc") as (fig, axes):
    axes["A"].plot(x, y)       # dominante Analyse
    axes["B"].plot(x, detail)  # Diagnose 1
    axes["C"].plot(x, check)   # Diagnose 2
    tcfig.label_panels(axes)
```

Achsenlabels und bewusst asymmetrische GridSpec-Abstände können unabhängig vom
konkreten Journalprofil formuliert werden:

```python
ax.set_xlabel(tcfig.quantity_label("Distance", "$r$", "nm"))
width_ratios = tcfig.resolve_track_ratios(
    (1, 1, tcfig.fixed_mm(5), 1),
    available_mm=170,
)
```

Ausführliche Entscheidungen stehen in [docs/REGELWERK.md](docs/REGELWERK.md).
Journalanforderungen und deren Status stehen in
[docs/JOURNAL_PROFILE.md](docs/JOURNAL_PROFILE.md). Der Affinity-Ablauf ist in
[docs/AFFINITY_WORKFLOW.md](docs/AFFINITY_WORKFLOW.md) beschrieben.

## Repository-Konvention

- `src/tcfig/data/*.toml` ist die technische Quelle der Wahrheit.
- Änderungen an Größen, Typografie oder Farben erhalten eine neue Paketversion.
- Generierte PDFs und PNGs werden nicht automatisch versioniert; Quellcode,
  Tokens, Tests und Affinity-Vorlagen dagegen schon.
- Vor einer Einreichung müssen die aktuellen Hinweise des konkreten Journals
  erneut geprüft werden.

## Fonts and typesetting

tcfig bundles Liberation Sans (SIL OFL, Arial-metric) and registers it with Matplotlib, so
figures look the same on every machine. PDF/PS embed TrueType text and SVG keeps text;
install the files from `tcfig.font_files()` to edit exported text in, e.g., Affinity.
For LaTeX-quality math, pass `typesetting="latex-sans"`, `"latex-serif"` or
`"latex-modern"` to `canvas()`; `export()` then typesets with LuaLaTeX (PDF/PNG only).
See `python examples/font_specimen.py` for a side-by-side specimen.
Recommended: `latex-sans` for publication figures, `latex-modern` for documents set in Latin
Modern, `mathtext` for working figures and SVG (see `docs/REGELWERK.md`, section 3).
