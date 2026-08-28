"""Load design tokens and publication profiles from package TOML files."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache, lru_cache
from importlib.resources import files
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True)
class JournalProfile:
    """Physical and technical requirements for a publication family."""

    name: str
    label: str
    publisher: str
    source: str
    verified: bool
    widths_mm: Mapping[str, float]
    max_height_mm: float
    base_font_pt: float
    min_font_pt: float
    max_font_pt: float
    min_line_pt: float
    raster_photo_dpi: int
    raster_combo_dpi: int
    raster_line_dpi: int

    def width_mm(self, slot: str) -> float:
        try:
            return self.widths_mm[slot]
        except KeyError as exc:
            choices = ", ".join(sorted(self.widths_mm))
            raise ValueError(
                f"Profile '{self.name}' has no width slot '{slot}'. Available: {choices}."
            ) from exc


def _read_toml(name: str) -> dict[str, Any]:
    resource = files("tcfig.data").joinpath(name)
    with resource.open("rb") as handle:
        return tomllib.load(handle)


@lru_cache(maxsize=1)
def get_tokens() -> Mapping[str, Any]:
    """Return the immutable top-level design-token mapping."""

    return MappingProxyType(_read_toml("design_tokens.toml"))


@lru_cache(maxsize=1)
def _profile_data() -> tuple[dict[str, Any], dict[str, str]]:
    data = _read_toml("profiles.toml")
    return data["profiles"], data.get("aliases", {})


def available_profiles() -> tuple[str, ...]:
    profiles, _ = _profile_data()
    return tuple(sorted(profiles))


@cache
def get_profile(name: str = "house") -> JournalProfile:
    """Resolve a profile name or journal alias."""

    profiles, aliases = _profile_data()
    canonical = aliases.get(name.lower(), name.lower())
    if canonical not in profiles:
        choices = ", ".join(available_profiles())
        raise ValueError(f"Unknown profile '{name}'. Available: {choices}.")
    values = profiles[canonical]
    return JournalProfile(
        name=canonical,
        label=str(values["label"]),
        publisher=str(values["publisher"]),
        source=str(values["source"]),
        verified=bool(values["verified"]),
        widths_mm=MappingProxyType(
            {key: float(value) for key, value in values["widths_mm"].items()}
        ),
        max_height_mm=float(values["max_height_mm"]),
        base_font_pt=float(values["base_font_pt"]),
        min_font_pt=float(values["min_font_pt"]),
        max_font_pt=float(values["max_font_pt"]),
        min_line_pt=float(values["min_line_pt"]),
        raster_photo_dpi=int(values["raster_photo_dpi"]),
        raster_combo_dpi=int(values["raster_combo_dpi"]),
        raster_line_dpi=int(values["raster_line_dpi"]),
    )
