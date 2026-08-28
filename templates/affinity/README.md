# Affinity assets

Die Dateien in diesem Ordner werden mit `scripts/generate_affinity_assets.py` erzeugt.

- `grid_<profile>.svg`: maßhaltiges Kompositionsraster
- `grid_coordinates.json`: exakte Hilfslinienkoordinaten in Millimetern
- `tcfig-palettes.ase`: importierbare Farbpalette für Affinity
- `assemblies/<profil>/*.svg`: asymmetrische Wide-/Long-Kompositionen
- `assemblies/assembly_coordinates.json`: exakte Slotmaße aller Assemblies

Die sichtbaren Rasterebenen dienen als Konstruktionshilfe und müssen vor dem finalen
Export ausgeblendet werden. Das Taylor-&-Francis-Raster ist als Arbeitsprofil markiert
und vor einer konkreten Einreichung zu verifizieren.
