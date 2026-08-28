"""Generate open Affinity-compatible grids and an Adobe Swatch Exchange palette."""

from __future__ import annotations

import json
import struct
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "tcfig" / "data"
OUTPUT = ROOT / "templates" / "affinity"
ASSEMBLY_OUTPUT = OUTPUT / "assemblies"
PROFILES = (
    "house",
    "jctc",
    "jcp",
    "pccp",
    "wiley_jcc",
    "springer_tc",
    "elsevier_tc",
    "nature",
    "taylor_francis_generic",
)


def load_toml(path: Path):
    with path.open("rb") as handle:
        return tomllib.load(handle)


def svg_grid(name: str, profile: dict, gap_mm: float) -> tuple[str, dict]:
    widths = profile["widths_mm"]
    width = float(widths.get("double", widths["single"]))
    height = min(150.0, float(profile["max_height_mm"]))
    half = (width - gap_mm) / 2
    third = (width - 2 * gap_mm) / 3
    row = 46.0
    horizontal = [row, row + gap_mm, 2 * row + gap_mm, 2 * (row + gap_mm)]
    vertical = [third, third + gap_mm, 2 * third + gap_mm, 2 * (third + gap_mm)]
    title_size = max(3.0, profile["base_font_pt"] * 0.3528)

    lines = []
    for x in vertical:
        lines.append(
            f'<line x1="{x:.3f}" y1="0" x2="{x:.3f}" y2="{height:.3f}" />'
        )
    for x in (half, half + gap_mm):
        lines.append(
            f'<line x1="{x:.3f}" y1="0" x2="{x:.3f}" y2="{height:.3f}" '
            'class="strong" />'
        )
    for y in horizontal:
        if y < height:
            lines.append(
                f'<line x1="0" y1="{y:.3f}" x2="{width:.3f}" y2="{y:.3f}" />'
            )

    single = float(widths["single"])
    single_box = (
        f'<rect x="0" y="0" width="{single:.3f}" height="{min(70.0, height):.3f}" '
        'class="single" />'
    )
    verified = "verified" if profile["verified"] else "working profile — verify before use"
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm"
     viewBox="0 0 {width} {height}">
  <title>tcfig {name} composition grid</title>
  <style>
    .border {{ fill: #ffffff; stroke: #171717; stroke-width: 0.25; }}
    .guide {{ fill: none; stroke: #56B4E9; stroke-width: 0.18; stroke-dasharray: 1.2 1.2; }}
    .guide .strong {{ stroke: #0072B2; stroke-dasharray: none; }}
    .single {{ fill: #E6F4FA; fill-opacity: 0.32; stroke: #DDAA33; stroke-width: 0.22; }}
    .label {{ font-family: Arial, Helvetica, sans-serif; font-size: {title_size:.3f}px; fill: #171717; }}
    .small {{ font-size: {max(2.2, title_size * 0.72):.3f}px; fill: #666666; }}
  </style>
  <g id="BACKGROUND"><rect class="border" x="0" y="0" width="{width}" height="{height}" /></g>
  <g id="SINGLE_COLUMN_REFERENCE">{single_box}</g>
  <g id="GRID" class="guide">{''.join(lines)}</g>
  <g id="INFO">
    <rect x="2" y="{height - 15:.3f}" width="{min(width - 4, 88):.3f}" height="13" fill="#FFFFFF" fill-opacity="0.9" />
    <text class="label" x="4" y="{height - 10:.3f}">tcfig · {name} · {width:g} × {height:g} mm</text>
    <text class="label small" x="4" y="{height - 5.5:.3f}">gap {gap_mm:g} mm · {verified} · place plots at 100%</text>
  </g>
</svg>
'''
    coordinates = {
        "profile": name,
        "canvas_mm": {"width": width, "height": height},
        "single_width_mm": single,
        "gap_mm": gap_mm,
        "two_panel_width_mm": half,
        "three_panel_width_mm": third,
        "vertical_guides_mm": vertical + [half, half + gap_mm],
        "horizontal_guides_mm": [value for value in horizontal if value < height],
        "verified": bool(profile["verified"]),
        "source": profile["source"],
    }
    return svg, coordinates


def _segments(total: float, gap: float, ratios: list[float]) -> tuple[list[float], list[float]]:
    usable = total - gap * (len(ratios) - 1)
    unit = usable / sum(ratios)
    sizes = [ratio * unit for ratio in ratios]
    starts = []
    cursor = 0.0
    for size in sizes:
        starts.append(cursor)
        cursor += size + gap
    return starts, sizes


def assembly_slots(
    mosaic: list[str],
    width: float,
    height: float,
    gap: float,
    width_ratios: list[float],
    height_ratios: list[float],
) -> dict[str, dict[str, float]]:
    x_starts, column_widths = _segments(width, gap, width_ratios)
    y_starts, row_heights = _segments(height, gap, height_ratios)
    slots = {}
    for panel in dict.fromkeys("".join(mosaic)):
        cells = [
            (row, column)
            for row, values in enumerate(mosaic)
            for column, value in enumerate(values)
            if value == panel
        ]
        rows = [row for row, _ in cells]
        columns = [column for _, column in cells]
        left_column, right_column = min(columns), max(columns)
        top_row, bottom_row = min(rows), max(rows)
        slots[panel] = {
            "x": x_starts[left_column],
            "y": y_starts[top_row],
            "width": (
                sum(column_widths[left_column : right_column + 1])
                + gap * (right_column - left_column)
            ),
            "height": (
                sum(row_heights[top_row : bottom_row + 1])
                + gap * (bottom_row - top_row)
            ),
        }
    return slots


def svg_assembly(
    profile_name: str,
    profile: dict,
    assembly_name: str,
    assembly: dict,
    tokens: dict,
    gap_mm: float,
) -> tuple[str, dict]:
    width_slot = assembly["default_width"]
    height_slot = assembly["default_height"]
    width = float(profile["widths_mm"][width_slot])
    height = min(
        float(tokens["layout"]["heights_mm"][width_slot][height_slot]),
        float(profile["max_height_mm"]),
    )
    mosaic = list(assembly["mosaic"])
    width_ratios = [float(value) for value in assembly["width_ratios"]]
    height_ratios = [float(value) for value in assembly["height_ratios"]]
    slots = assembly_slots(
        mosaic,
        width,
        height,
        gap_mm,
        width_ratios,
        height_ratios,
    )
    fills = tokens["color"]["palettes"]["tol_pale"]
    rectangles = []
    for index, (panel, slot) in enumerate(slots.items()):
        fill = fills[index % len(fills)]
        center_x = slot["x"] + slot["width"] / 2
        center_y = slot["y"] + slot["height"] / 2
        rectangles.append(
            f'<g id="SLOT_{panel}">'
            f'<rect x="{slot["x"]:.3f}" y="{slot["y"]:.3f}" '
            f'width="{slot["width"]:.3f}" height="{slot["height"]:.3f}" '
            f'fill="{fill}" stroke="#4477AA" stroke-width="0.25" />'
            f'<text class="panel" x="{center_x:.3f}" y="{center_y:.3f}">{panel}</text>'
            "</g>"
        )

    verified = "verified" if profile["verified"] else "verify before use"
    font_size = max(2.5, float(profile["base_font_pt"]) * 0.3528)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm"
     viewBox="0 0 {width} {height}">
  <title>tcfig {profile_name} {assembly_name} assembly</title>
  <style>
    .panel {{ font-family: Arial, Helvetica, sans-serif; font-size: {font_size * 1.5:.3f}px;
              font-weight: bold; text-anchor: middle; dominant-baseline: middle; fill: #171717; }}
    .info {{ font-family: Arial, Helvetica, sans-serif; font-size: {font_size:.3f}px; fill: #171717; }}
    .small {{ font-size: {max(2.2, font_size * 0.72):.3f}px; fill: #666666; }}
  </style>
  <rect x="0" y="0" width="{width}" height="{height}" fill="#FFFFFF" stroke="#171717" stroke-width="0.25" />
  {''.join(rectangles)}
  <g id="INFO">
    <rect x="2" y="{height - 14:.3f}" width="{min(width - 4, 118):.3f}" height="12" fill="#FFFFFF" fill-opacity="0.92" />
    <text class="info" x="4" y="{height - 9.5:.3f}">tcfig · {profile_name} · {assembly_name} · {width:g} × {height:g} mm</text>
    <text class="info small" x="4" y="{height - 5.2:.3f}">gap {gap_mm:g} mm · {verified} · place at 100%</text>
  </g>
</svg>
'''
    return svg, {
        "profile": profile_name,
        "assembly": assembly_name,
        "description": assembly["description"],
        "canvas_mm": {"width": width, "height": height},
        "gap_mm": gap_mm,
        "slots_mm": slots,
        "verified": bool(profile["verified"]),
        "source": profile["source"],
    }


def write_ase(path: Path, colors: list[tuple[str, str]]) -> None:
    blocks = []
    for name, value in colors:
        red = int(value[1:3], 16) / 255
        green = int(value[3:5], 16) / 255
        blue = int(value[5:7], 16) / 255
        encoded = (name + "\0").encode("utf-16-be")
        payload = (
            struct.pack(">H", len(name) + 1)
            + encoded
            + b"RGB "
            + struct.pack(">fffH", red, green, blue, 0)
        )
        blocks.append(struct.pack(">HI", 0x0001, len(payload)) + payload)
    path.write_bytes(b"ASEF" + struct.pack(">HHI", 1, 0, len(blocks)) + b"".join(blocks))


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ASSEMBLY_OUTPUT.mkdir(parents=True, exist_ok=True)
    profiles = load_toml(DATA / "profiles.toml")["profiles"]
    tokens = load_toml(DATA / "design_tokens.toml")
    gap = float(tokens["layout"]["panel_gap_mm"])
    all_coordinates = {}
    for name in PROFILES:
        svg, coordinates = svg_grid(name, profiles[name], gap)
        (OUTPUT / f"grid_{name}.svg").write_text(svg, encoding="utf-8")
        all_coordinates[name] = coordinates
    (OUTPUT / "grid_coordinates.json").write_text(
        json.dumps(all_coordinates, indent=2), encoding="utf-8"
    )

    assembly_coordinates = {}
    for profile_name in PROFILES:
        profile_dir = ASSEMBLY_OUTPUT / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        assembly_coordinates[profile_name] = {}
        for assembly_name, assembly in tokens["layout"]["assemblies"].items():
            svg, coordinates = svg_assembly(
                profile_name,
                profiles[profile_name],
                assembly_name,
                assembly,
                tokens,
                gap,
            )
            (profile_dir / f"{assembly_name}.svg").write_text(svg, encoding="utf-8")
            assembly_coordinates[profile_name][assembly_name] = coordinates
    (ASSEMBLY_OUTPUT / "assembly_coordinates.json").write_text(
        json.dumps(assembly_coordinates, indent=2), encoding="utf-8"
    )

    colors = []
    for palette_name, values in tokens["color"]["palettes"].items():
        for index, value in enumerate(values, start=1):
            colors.append((f"TC / {palette_name} / {index:02d}", value))
    for role, value in tokens["color"]["semantic"].items():
        colors.append((f"TC / semantic / {role}", value))
    write_ase(OUTPUT / "tcfig-palettes.ase", colors)


if __name__ == "__main__":
    main()
