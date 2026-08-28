"""Opinionated plot primitives for common molecular-dynamics results."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from .colors import get_cmap, palette, semantic_color
from .config import get_tokens


def plot_replicas(
    ax: Any,
    time: Sequence[float],
    replicas: Any,
    *,
    color: str | None = None,
    label: str | None = None,
    interval: tuple[float, float] = (0.1, 0.9),
    center: str = "median",
    equilibration_until: float | None = None,
) -> dict[str, Any]:
    """Show individual trajectories, ensemble center and a quantile interval."""

    values = np.asarray(replicas, dtype=float)
    x = np.asarray(time, dtype=float)
    if values.ndim != 2 or values.shape[1] != x.size:
        raise ValueError("replicas must have shape (n_replicas, n_timepoints).")
    if not 0 <= interval[0] < interval[1] <= 1:
        raise ValueError("interval must contain ordered quantiles between 0 and 1.")

    chosen = color or palette("tol_high_contrast")[0]
    line_token = get_tokens()["line"]
    individual = [
        ax.plot(x, row, color=chosen, alpha=0.22, linewidth=line_token["replica_pt"])[0]
        for row in values
    ]
    low, high = np.quantile(values, interval, axis=0)
    band = ax.fill_between(x, low, high, color=chosen, alpha=0.14, linewidth=0)
    if center == "median":
        center_values = np.median(values, axis=0)
    elif center == "mean":
        center_values = np.mean(values, axis=0)
    else:
        raise ValueError("center must be 'median' or 'mean'.")
    summary = ax.plot(
        x,
        center_values,
        color=chosen,
        linewidth=line_token["emphasis_pt"],
        label=label,
    )[0]
    equilibration = None
    if equilibration_until is not None:
        equilibration = ax.axvspan(
            x.min(),
            equilibration_until,
            color=semantic_color("missing"),
            zorder=-5,
            linewidth=0,
        )
    return {
        "replicas": individual,
        "interval": band,
        "center": summary,
        "equilibration": equilibration,
    }


def plot_ecdf(
    ax: Any,
    groups: Mapping[str, Sequence[float]],
    *,
    colors: Sequence[str] | None = None,
) -> list[Any]:
    """Plot empirical cumulative distributions without smoothing assumptions."""

    chosen = tuple(colors) if colors is not None else palette("tol_bright")
    artists = []
    for index, (label, values) in enumerate(groups.items()):
        sample = np.sort(np.asarray(values, dtype=float))
        if sample.size == 0:
            continue
        probability = np.arange(1, sample.size + 1) / sample.size
        artists.append(
            ax.step(
                sample,
                probability,
                where="post",
                color=chosen[index % len(chosen)],
                label=label,
            )[0]
        )
    ax.set_ylabel("Cumulative probability")
    ax.set_ylim(0, 1)
    return artists


def plot_free_energy(
    ax: Any,
    coordinate: Sequence[float],
    free_energy: Sequence[float],
    *,
    uncertainty: Sequence[float] | None = None,
    color: str | None = None,
    label: str | None = None,
    zero: bool = True,
) -> dict[str, Any]:
    """Plot a 1D free-energy profile with an optional uncertainty band."""

    x = np.asarray(coordinate, dtype=float)
    y = np.asarray(free_energy, dtype=float)
    if x.shape != y.shape:
        raise ValueError("coordinate and free_energy must have identical shape.")
    if zero:
        y = y - np.nanmin(y)
    chosen = color or palette("tol_high_contrast")[0]
    band = None
    if uncertainty is not None:
        error = np.asarray(uncertainty, dtype=float)
        if error.shape != y.shape:
            raise ValueError("uncertainty must have the same shape as free_energy.")
        band = ax.fill_between(x, y - error, y + error, color=chosen, alpha=0.16, linewidth=0)
    line = ax.plot(x, y, color=chosen, label=label)[0]
    return {"line": line, "interval": band}


def plot_rdf(
    ax: Any,
    radius: Sequence[float],
    g_r: Sequence[float],
    *,
    uncertainty: Sequence[float] | None = None,
    color: str | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    """Plot a radial distribution function with the bulk reference at one."""

    chosen = color or palette("tol_high_contrast")[0]
    x = np.asarray(radius, dtype=float)
    y = np.asarray(g_r, dtype=float)
    reference = ax.axhline(1.0, color=semantic_color("muted"), linewidth=0.6, linestyle="--")
    band = None
    if uncertainty is not None:
        error = np.asarray(uncertainty, dtype=float)
        band = ax.fill_between(x, y - error, y + error, color=chosen, alpha=0.16, linewidth=0)
    line = ax.plot(x, y, color=chosen, label=label)[0]
    return {"line": line, "interval": band, "reference": reference}


def plot_free_energy_surface(
    ax: Any,
    x: Any,
    y: Any,
    free_energy: Any,
    *,
    levels: int | Sequence[float] = 12,
    cmap_role: str = "scientific_sequential",
    colorbar: bool = False,
) -> dict[str, Any]:
    """Plot a masked 2D free-energy surface with quantitative contours."""

    values = np.ma.masked_invalid(np.asarray(free_energy, dtype=float))
    cmap = get_cmap(cmap_role).copy()
    cmap.set_bad(semantic_color("missing"))
    filled = ax.contourf(x, y, values, levels=levels, cmap=cmap)
    contours = ax.contour(
        x,
        y,
        values,
        levels=filled.levels[::2],
        colors=semantic_color("foreground"),
        linewidths=0.35,
        alpha=0.55,
    )
    bar = ax.figure.colorbar(filled, ax=ax) if colorbar else None
    return {"filled": filled, "contours": contours, "colorbar": bar}

