# Bundled fonts

Liberation Sans 2.1.5 (Regular, Bold, Italic, BoldItalic), SIL Open Font License 1.1
(`LICENSE-LiberationSans.txt`). Metric-compatible with Arial, so layouts designed
for Arial keep their dimensions. Source: official release archive
`liberation-fonts-ttf-2.1.5.tar.gz` from https://github.com/liberationfonts/liberation-fonts
(SHA-256 7191c669bf38899f73a2094ed00f7b800553364f90e2637010a69c0e268f25d0).

tcfig registers these files with Matplotlib at import, so figures do not depend on
system fonts or Matplotlib's font cache. Mathematical symbols come from the STIX
fonts shipped with Matplotlib. To edit exported PDF/SVG text in another program
(for example Affinity), install the files listed by `tcfig.font_files()`.
