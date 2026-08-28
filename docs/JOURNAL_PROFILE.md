# Journal-Profile

Die Profile sind reproduzierbare Arbeitsvorgaben, keine Garantie für Annahme oder Produktion.
Verlage können Anforderungen ändern; vor Einreichung wird das konkrete Journal erneut geprüft.

| Profil | Zieljournale | Breiten (mm) | Basisschrift | Status |
|---|---|---:|---:|---|
| `house` | interner Standard | 85 / 130 / 180 | 8 pt | intern |
| `jctc` | JCTC und verwandte ACS-Zweispaltenjournale | 84.6 / 105.8 / 177.8 | 8 pt | geprüft 2026-08 |
| `jcp` | Journal of Chemical Physics | 85 / 170 | 8 pt | geprüft 2026-08 |
| `pccp` | PCCP | 83 / 171 | 7.5 pt | geprüft 2026-08 |
| `wiley_jcc` | Journal of Computational Chemistry | 80.96 / 169.06 | 10 pt | geprüft 2026-08 |
| `springer_tc` | Theoretical Chemistry Accounts u. ähnliche | 84 / 129 / 174 | 8 pt | Publisherprofil |
| `elsevier_tc` | Chemical Physics, C&TC u. ähnliche | 90 / 140 / 190 | 7 pt | Publisherprofil |
| `nature` | Nature-Härtetest und mögliche Transfers | 89 / 120 / 183 | 6.5 pt | geprüft 2026-08 |
| `taylor_francis_generic` | Molecular Physics/Simulation | 85 / 170 | 8 pt | vor Einreichung verifizieren |

## Journal-Zuordnung

Die folgende Auswahl ist der praktische Zielkorridor für theoretisch-chemische Arbeiten,
in denen Molecular-Dynamics-Ergebnisse ein wesentlicher Bestandteil sind.

| Journal | Geeignet insbesondere für | tcfig-Profil | Priorität als Ausgangspunkt |
|---|---|---|---|
| Journal of Chemical Theory and Computation | neue Methoden, Sampling, freie Energien, Benchmarks | `jctc` | Kernziel |
| The Journal of Chemical Physics | grundlegende Theorie, statistische Mechanik, methodische MD | `jcp` | Kernziel |
| Physical Chemistry Chemical Physics | physikalisch-chemische Anwendungen und Mechanismen | `pccp` | Kernziel |
| Journal of Computational Chemistry | Methoden und belastbare Anwendungen | `wiley_jcc` | Kernziel |
| Molecular Physics | molekulare Theorie, statistische Mechanik und Simulation | `taylor_francis_generic` | passend nach Scope-Prüfung |
| Molecular Simulation | Simulationsmethoden und MD-Anwendungen | `taylor_francis_generic` | sehr direkte MD-Passung |
| Chemical Physics | physikalisch-chemische Mechanismen und Dynamik | `elsevier_tc` | passend nach Scope-Prüfung |
| Computational and Theoretical Chemistry | rechnerische/theoretische Anwendungen | `elsevier_tc` | passend nach Scope-Prüfung |
| Theoretical Chemistry Accounts | Theorie und rechnerische Methodik | `springer_tc` | fallabhängig |
| International Journal of Quantum Chemistry | quantenchemischer Schwerpunkt mit MD-Anteil | `wiley_jcc` | fallabhängig |

Die Priorität ist keine Qualitätsrangfolge. Sie beschreibt, wie unmittelbar das Journaltypische
zum geplanten Paket aus Theorie, Sampling, Konvergenz und MD-Auswertung passt. Vor der Einreichung
werden Scope und aktuelle Artwork-Vorgaben des konkreten Journals erneut geprüft.

## Technische Quellen

- ACS/JCTC: 240 pt einspaltig, 300–504 pt zweispaltig, mindestens 4.5 pt Schrift,
  mindestens 0.5 pt Linien.
- AIP: 8.5/17 cm, mindestens 8 pt Schrift und 0.5 pt Linien.
- RSC/PCCP: 8.3/17.1 cm, höchstens 23.3 cm Höhe.
- Wiley/JCC: 8.096/16.906 cm; Plotbeschriftungen 10–12 pt.
- Springer: 39/84/129/174 mm, meist 8–12 pt.
- Elsevier: 90/140/190 mm; normale Beschriftung 7 pt, Sub-/Superscript mindestens 6 pt.
- Nature: 89/183 mm, maximal 170 mm Höhe und 5–7 pt Schrift.

Die vollständigen Quellenlinks und der Recherchekontext stehen in `docs/RESEARCH_NOTES.md`.
