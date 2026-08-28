# Regelwerk für wissenschaftliche Abbildungen

Version 0.1 — Schwerpunkt Theoretical Chemistry und Molecular Dynamics

## 1. Grundprinzipien

1. **Endformat zuerst.** Breite und Höhe werden in Millimetern festgelegt.
2. **Keine nachträgliche Skalierung.** Python-PDFs werden in Affinity mit 100 % platziert.
3. **Eine Aussage pro Figure.** Panels dürfen Teilargumente tragen, aber keine unabhängigen Geschichten.
4. **Daten vor Dekoration.** Schatten, Verläufe, 3D-Effekte und dekorative Rahmen entfallen.
5. **Redundante Kodierung.** Relevante Gruppen unterscheiden sich nicht nur durch Farbe,
   sondern zusätzlich durch Marker, Linienstil, Position oder direkte Beschriftung.
6. **Unsicherheit ist Teil des Ergebnisses.** Replikate, Intervalle und Konvergenz werden sichtbar gemacht.
7. **Quelle und Verarbeitung bleiben nachvollziehbar.** Exportierte Abbildungen erhalten Metadaten
   und auf Wunsch ein Datenpaket.

## 2. Größen und Komposition

Die abstrakten Breiten `single`, `intermediate` und `double` werden vom Journal-Profil
in Millimeter übersetzt. Höhe wird über die Tokens `compact`, `standard`, `tall` oder
explizit in Millimetern angegeben.

Der Hausstandard nutzt 85, 130 und 180 mm. Journal-Profile überschreiben diese Werte.
Der Außenrahmen eines Exports ist verbindlich; in der Produktion wird niemals mit
`bbox_inches="tight"` gespeichert.

Empfohlene Abstände:

- 4 mm zwischen benachbarten Panels
- mindestens 2 mm zwischen Beschriftung und angrenzendem Panel
- gemeinsame Achsen und Plotflächen bei direkten Vergleichen ausrichten
- Panelreihenfolge von links oben nach rechts unten

## 3. Typografie

Die Schriftfamilie ist Arial mit Helvetica, Liberation Sans und DejaVu Sans als Fallback.
Die Basisschrift hängt vom Profil ab. Innerhalb eines Profils verwenden Achsen, Ticks,
Legenden und Annotationen dieselbe Basisschrift. Hierarchie entsteht primär durch Gewicht,
Position und Abstand.

- Satzanfang groß, ansonsten sentence case
- Variablen kursiv, Einheiten aufrecht
- Achsenformat: `Quantity (unit)`
- Unicode-Minus statt Bindestrich, wenn vom Export unterstützt
- keine farbigen Fließtexte oder Legendentexte
- Panelbuchstaben klein, fett und ohne Klammern: **a**, **b**, **c**
- kein Titel im Plot, wenn Caption oder Panelüberschrift dieselbe Information trägt

## 4. Linien, Marker und Achsen

- Datenlinie: 1.0 pt
- hervorgehobene Datenlinie: 1.4 pt
- Achsen und Ticks: 0.5 pt
- Fehlerbalken: 0.6 pt
- Marker: 3.8 pt, Kontur 0.5 pt
- obere und rechte Rahmenlinie standardmäßig aus
- Hintergrundraster standardmäßig aus; nur bei echter Ablesehilfe einsetzen
- Null- und Referenzlinien nur, wenn wissenschaftlich relevant
- keine Legendenbox; direkte Beschriftung bevorzugen, wenn sie stabil möglich ist

## 5. Farbsystem

Farbe wird nach Datentyp gewählt, nicht nach persönlichem Geschmack.

| Datentyp | Standard |
|---|---|
| 2–3 Bedingungen | `tol_high_contrast` |
| 4–7 Kategorien | `tol_bright` |
| bis 9 Kategorien | `tol_muted`, zusätzlich Marker/Facetten |
| geordnete positive Größe | `scientific_sequential` |
| Abweichung um Referenzwert | `scientific_diverging` |
| Winkel oder Phase | `scientific_cyclic` |
| Referenz, fehlende Daten | neutrale Grautöne |

`jet`, `rainbow`, `hsv`, `nipy_spectral` und nicht begründete Rot-Grün-Kombinationen
sind im Validator gesperrt. Continuous Maps müssen eine passende Normierung besitzen.
Bei diverging Maps liegt der Mittelpunkt auf einem wissenschaftlich begründeten Wert.

## 6. Molecular-Dynamics-Grammatik

### Replikate und Zeitreihen

- Bedingungen erhalten Farben; Replikate derselben Bedingung teilen eine Farbe.
- Replikate werden dünn und teiltransparent gezeigt, Ensemble-Statistik stärker.
- Äquilibrierungs- oder ausgeschlossene Zeitbereiche werden markiert.
- Glättung darf Rohdaten nicht ersetzen und muss dokumentiert sein.

### Verteilungen

- ECDF wird für robuste Gruppenvergleiche bevorzugt.
- Histogramm-Binbreiten sind über verglichene Gruppen identisch.
- KDE/Violin nur bei ausreichender Stichprobe und dokumentierter Bandbreite.
- Mittelwertbalken ohne Verteilung oder Einzelwerte sind zu vermeiden.

### Freie Energien

- Gemeinsamer Nullpunkt und gleiche Skala bei Vergleichspanels.
- 1D-Profile zeigen Unsicherheitsintervalle.
- 2D-Flächen verwenden sequenzielle Maps; ungesampelte Bereiche sind maskiert.
- Konturen unterstützen quantitative Ablesbarkeit.

### RDF, MSD und Transport

- RDF enthält die Referenz bei `g(r)=1`.
- MSD-Fitregionen werden sichtbar markiert.
- Fit, Extrapolation und Daten verwenden unterschiedliche visuelle Rollen.
- Unsicherheit stammt aus Blöcken oder unabhängigen Replikaten, nicht aus dekorativer Glättung.

### Strukturen und Trajektorien

- Vergleichspanels verwenden identische Kamera, Orientierung, Zoom und Darstellung.
- CPK-Elementfarben bleiben für Atome erhalten; System- oder Zustandsfarben stammen aus tcfig.
- Hervorhebung wird sparsam eingesetzt; unwichtige Umgebung wird neutralisiert.
- Molekül-Snapshots ersetzen keine quantitative Analyse.

## 7. Export

Primärformate sind PDF und SVG. PNG dient als Vorschau oder für Systeme ohne Vektorimport.

- PDF: TrueType/Type-42-Schriften einbetten
- SVG: Text als Text erhalten
- PNG: standardmäßig 600 dpi
- RGB-Arbeitsfarbraum
- weißer Hintergrund für Standalone-Figures, transparent optional für Affinity-Kompositionen
- niemals automatische Außenbeschneidung im finalen Export

Jeder Export erhält eine JSON-Datei mit Profil, Abmessungen, Style-Version,
Validierungsbericht und optionaler Git-Revision. Numerische Daten können als komprimiertes
NPZ sowie einfache eindimensionale Spalten zusätzlich als CSV gespeichert werden.

## 8. Prüfung vor Einreichung

- Figure bei 100 % Endgröße betrachten
- kleinste Schrift und dünnste Linie kontrollieren
- Graustufen- und Farbsehschwächen-Proof kontrollieren
- Achsen, Einheiten, Legende und Intervalle vollständig
- keine abgeschnittenen Labels
- PDF-Schriften eingebettet
- effektive Rasterauflösung ausreichend
- Caption definiert Statistik, Fehlerdarstellung und Replikatzahl
- aktuelle Journalhinweise erneut gegen das Profil prüfen

