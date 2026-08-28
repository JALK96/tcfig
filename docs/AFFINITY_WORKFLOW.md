# Affinity-Workflow

Die Dateien unter `templates/affinity/` sind keine proprietären `.afdesign`-Dateien.
Sie sind bewusst als offene SVG-Raster und ASE-Farbpalette gespeichert und lassen sich
in Affinity Designer oder Publisher importieren.

## Einrichtung

1. Das SVG des Zielprofils in Affinity öffnen oder platzieren.
2. Dokumenteinheit auf Millimeter stellen.
3. Die Ebene `GRID` sperren oder ihre Linien in Hilfslinien umwandeln.
4. `tcfig-palettes.ase` als Dokument- oder Anwendungspalette importieren.
5. Textstile mit Arial und der Basisschrift des Profils anlegen.

## Platzieren von Python-Plots

- PDF oder SVG verwenden.
- Transformationsmaßstab X/Y auf 100 % setzen.
- Seitenverhältnis sperren.
- Nicht optisch passend ziehen; stattdessen den passenden Slot neu exportieren.
- Panelbuchstaben erst in der Gesamtkomposition setzen.
- Vor Übergabe prüfen, ob Text editierbar und Schriften eingebettet sind.

## Rasterlogik

- Außenrahmen entspricht der finalen Figure-Größe.
- Bei zweispaltigen Profilen werden zwei Primärspalten mit dem definierten Zwischenraum gezeigt.
- Halbpanels innerhalb einer Spalte besitzen 4 mm Abstand.
- Horizontale Module dienen als Vorschlag, nicht als Zwang für wissenschaftlich ungeeignete Seitenverhältnisse.

Die SVG-Linien werden nicht exportiert. Für die finale Figure wird die Ebene `GRID`
ausgeblendet und nur die komponierte Abbildung exportiert.

## Asymmetrische Vorlagen

Unter `templates/affinity/assemblies/<profil>/` liegen für jedes Journalprofil sechs
fertige Assembly-SVGs. Jeder farbige Slot ist als eigene Ebene `SLOT_A`, `SLOT_B` usw.
angelegt. Die Slotmaße stehen zusätzlich in `assembly_coordinates.json`.

- Wide-Plot: `lead_top`, `wide_triptych` oder `staggered`
- Long-/Sidebar-Plot: `lead_right` oder `sidebar_matrix`
- lange Einspaltenabbildung: `long_story`

Ein Plot wird für die reale Slotbreite neu aus Python exportiert. Er wird nicht in Affinity
verzerrt, um einen unpassenden Slot zu füllen.
