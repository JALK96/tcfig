"""Publication figures for theoretical chemistry and molecular dynamics."""

__version__ = "0.3.0"

from .colors import condition_styles, get_cmap, palette, semantic_color
from .config import JournalProfile, available_profiles, get_profile, get_tokens
from .export import ExportResult, export
from .figure import canvas, figure, label_panels, resolve_size_mm
from .labels import quantity_label
from .layouts import (
    AssemblySpec,
    FixedTrack,
    assembly_canvas,
    available_assemblies,
    fixed_mm,
    get_assembly,
    resolve_track_ratios,
)
from .styles import panel_label_size, rc_params, style_context
from .validate import ValidationIssue, ValidationReport, validate_figure

__all__ = [
    "AssemblySpec",
    "ExportResult",
    "FixedTrack",
    "JournalProfile",
    "ValidationIssue",
    "ValidationReport",
    "assembly_canvas",
    "available_assemblies",
    "available_profiles",
    "canvas",
    "condition_styles",
    "export",
    "figure",
    "fixed_mm",
    "get_assembly",
    "get_cmap",
    "get_profile",
    "get_tokens",
    "label_panels",
    "palette",
    "panel_label_size",
    "quantity_label",
    "rc_params",
    "resolve_size_mm",
    "resolve_track_ratios",
    "semantic_color",
    "style_context",
    "validate_figure",
]
