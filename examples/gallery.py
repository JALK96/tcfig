from pathlib import Path

import matplotlib as mpl
import numpy as np

mpl.use("Agg")

import tcfig
from tcfig.md import plot_ecdf, plot_free_energy, plot_free_energy_surface, plot_rdf, plot_replicas

OUTPUT = Path(__file__).with_name("output")
RNG = np.random.default_rng(20260828)


def overview() -> None:
    time = np.linspace(0, 100, 401)
    replicas = np.vstack(
        [
            0.35 + 0.16 * np.exp(-time / 24) + 0.035 * np.sin(time / 8 + phase)
            + RNG.normal(0, 0.018, time.size)
            for phase in np.linspace(0, np.pi, 8)
        ]
    )

    with tcfig.canvas(
        profile="jctc",
        width="double",
        height=145,
        nrows=2,
        ncols=2,
        close=True,
    ) as (fig, axes):
        plot_replicas(
            axes[0, 0],
            time,
            replicas,
            label="Ensemble median",
            equilibration_until=20,
        )
        axes[0, 0].set(xlabel="Time (ns)", ylabel="Radius of gyration (nm)")
        axes[0, 0].legend(loc="upper right")

        plot_ecdf(
            axes[0, 1],
            {
                "Reference": RNG.normal(1.05, 0.12, 150),
                "Modified": RNG.normal(1.22, 0.16, 150),
            },
        )
        axes[0, 1].set_xlabel("Residence time (ns)")
        axes[0, 1].legend(loc="lower right")

        radius = np.linspace(0.2, 1.4, 220)
        rdf = 1 + 2.5 * np.exp(-((radius - 0.48) / 0.08) ** 2) - 0.55 * np.exp(
            -((radius - 0.73) / 0.11) ** 2
        )
        plot_rdf(axes[1, 0], radius, rdf, uncertainty=np.full_like(radius, 0.08))
        axes[1, 0].set(xlabel="Distance (nm)", ylabel="$g(r)$", ylim=(0, 4.0))

        cv1 = np.linspace(-2.6, 2.6, 100)
        cv2 = np.linspace(-2.2, 2.2, 90)
        x_grid, y_grid = np.meshgrid(cv1, cv2)
        energy = (
            0.7 * (x_grid**2 + 0.7 * y_grid**2)
            - 2.6 * np.exp(-((x_grid + 1.1) ** 2 + (y_grid - 0.5) ** 2) / 0.45)
            - 2.0 * np.exp(-((x_grid - 1.0) ** 2 + (y_grid + 0.7) ** 2) / 0.6)
        )
        energy -= np.nanmin(energy)
        surface = plot_free_energy_surface(
            axes[1, 1], x_grid, y_grid, energy, levels=np.arange(0, 7.5, 0.5)
        )
        axes[1, 1].set(xlabel="Collective variable 1", ylabel="Collective variable 2")
        bar = fig.colorbar(surface["filled"], ax=axes[1, 1])
        bar.set_label("Free energy (kJ mol$^{-1}$)")

        tcfig.label_panels(axes)
        tcfig.export(
            fig,
            OUTPUT / "md_overview_jctc",
            data={"time_ns": time, "replicas": replicas},
            alt_text=(
                "Four-panel molecular-dynamics figure showing replica convergence, an empirical "
                "distribution comparison, a radial distribution function, and a two-dimensional "
                "free-energy surface."
            ),
            source_path=__file__,
        )


def free_energy_comparison() -> None:
    coordinate = np.linspace(-2.5, 2.5, 180)
    reference = 1.7 * (coordinate**2 - 1.1) ** 2
    modified = 1.35 * (coordinate**2 - 0.9) ** 2 + 0.35 * coordinate
    uncertainty = 0.12 + 0.05 * np.abs(coordinate)
    colors = tcfig.palette("tol_high_contrast")

    with tcfig.canvas(profile="pccp", width="single", height="standard", close=True) as (
        fig,
        ax,
    ):
        plot_free_energy(
            ax,
            coordinate,
            reference,
            uncertainty=uncertainty,
            color=colors[0],
            label="Reference",
        )
        plot_free_energy(
            ax,
            coordinate,
            modified,
            uncertainty=uncertainty * 1.2,
            color=colors[1],
            label="Modified",
        )
        ax.set(xlabel="Reaction coordinate", ylabel="Free energy (kJ mol$^{-1}$)")
        ax.legend()
        tcfig.export(
            fig,
            OUTPUT / "free_energy_pccp",
            data={
                "coordinate": coordinate,
                "reference_kj_mol": reference - reference.min(),
                "modified_kj_mol": modified - modified.min(),
            },
            source_path=__file__,
        )


def palette_reference() -> None:
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgb

    qualitative = (
        "tol_high_contrast",
        "tol_bright",
        "tol_vibrant",
        "tol_muted",
        "tol_medium_contrast",
        "tol_dark",
        "tol_light",
        "tol_pale",
    )
    continuous = (
        ("scientific_sequential", "sequential · magnitude"),
        ("scientific_diverging", "diverging · signed deviation"),
        ("scientific_cyclic", "cyclic · angle / phase"),
        ("tol_sunset", "Tol sunset · diverging"),
        ("tol_nightfall", "Tol nightfall · diverging"),
        ("tol_ylorbr", "Tol YlOrBr · sequential"),
        ("tol_iridescent", "Tol iridescent · sequential"),
    )

    with tcfig.canvas(
        profile="house",
        width="double",
        height=180,
        nrows=len(qualitative) + len(continuous),
        ncols=1,
        close=True,
    ) as (fig, axes):
        for ax, name in zip(axes[: len(qualitative)], qualitative, strict=True):
            colors = tcfig.palette(name)
            for index, color in enumerate(colors):
                ax.add_patch(plt.Rectangle((index, 0), 1, 1, color=color, linewidth=0))
                red, green, blue = to_rgb(color)
                luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
                text_color = "#FFFFFF" if luminance < 0.42 else "#171717"
                ax.text(
                    index + 0.5,
                    0.5,
                    str(index + 1),
                    color=text_color,
                    ha="center",
                    va="center",
                )
            label = f"Tol {name.removeprefix('tol_').replace('_', ' ')}"
            ax.set(xlim=(0, len(colors)), ylim=(0, 1))
            ax.set_axis_off()
            ax.text(-0.015, 0.5, label, transform=ax.transAxes, ha="right", va="center")

        gradient = np.linspace(0, 1, 512)[None, :]
        for ax, (role, label) in zip(axes[len(qualitative) :], continuous, strict=True):
            ax.imshow(gradient, aspect="auto", cmap=tcfig.get_cmap(role), extent=(0, 1, 0, 1))
            ax.set_axis_off()
            ax.text(-0.015, 0.5, label, transform=ax.transAxes, ha="right", va="center")

        tcfig.export(
            fig,
            OUTPUT / "palette_reference",
            alt_text=(
                "Reference sheet with three colorblind-safe categorical palettes and "
                "sequential, diverging, and cyclic scientific colormaps."
            ),
            source_path=__file__,
        )


if __name__ == "__main__":
    OUTPUT.mkdir(exist_ok=True)
    overview()
    free_energy_comparison()
    palette_reference()
