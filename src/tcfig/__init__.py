"""Publication figures for theoretical chemistry and molecular dynamics."""

__version__ = "0.2.0"

from .colors import condition_styles, get_cmap, palette, semantic_color
from .config import JournalProfile, available_profiles, get_profile, get_tokens
from .export import ExportResult, export
from .figure import canvas, figure, label_panels, resolve_size_mm
from .layouts import AssemblySpec, assembly_canvas, available_assemblies, get_assembly
from .styles import rc_params, style_context
from .validate import ValidationIssue, ValidationReport, validate_figure

__all__ = [
    "AssemblySpec",
    "ExportResult",
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
    "get_assembly",
    "get_cmap",
    "get_profile",
    "get_tokens",
    "label_panels",
    "palette",
    "rc_params",
    "resolve_size_mm",
    "semantic_color",
    "style_context",
    "validate_figure",
]
