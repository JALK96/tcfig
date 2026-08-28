from pathlib import Path

import matplotlib as mpl
import numpy as np

mpl.use("Agg")

import tcfig
from tcfig.md import plot_ecdf, plot_free_energy, plot_free_energy_surface, plot_rdf, plot_replicas

OUTPUT = Path(__file__).with_name("output")
RNG = np.random.default_rng(20260828)


def _replica_data() -> tuple[np.ndarray, np.ndarray]:
    time = np.linspace(0, 120, 480)
    replicas = np.vstack(
        [
            0.43
            + 0.11 * np.exp(-time / 27)
            + 0.025 * np.sin(time / 10 + phase)
            + RNG.normal(0, 0.014, time.size)
            for phase in np.linspace(0, np.pi, 6)
        ]
    )
    return time, replicas


def wide_assembly() -> None:
    time, replicas = _replica_data()
    coordinate = np.linspace(-2.2, 2.2, 180)
    energy = 1.4 * (coordinate**2 - 1.0) ** 2 + 0.2 * coordinate
    radius = np.linspace(0.2, 1.4, 180)
    rdf = 1 + 2.4 * np.exp(-((radius - 0.5) / 0.08) ** 2)

    with tcfig.assembly_canvas(
        "staggered",
        profile="jctc",
        height=112,
        close=True,
    ) as (fig, axes):
        plot_replicas(axes["A"], time, replicas, equilibration_until=20)
        axes["A"].set(xlabel="Time (ns)", ylabel="Radius of gyration (nm)")

        plot_ecdf(
            axes["B"],
            {
                "Reference": RNG.normal(1.0, 0.13, 120),
                "Modified": RNG.normal(1.18, 0.16, 120),
            },
        )
        axes["B"].set_xlabel("Residence time (ns)")

        plot_rdf(axes["C"], radius, rdf)
        axes["C"].set(xlabel="Distance (nm)", ylabel="$g(r)$")

        plot_free_energy(
            axes["D"],
            coordinate,
            energy,
            uncertainty=np.full_like(coordinate, 0.14),
        )
        axes["D"].set(
            xlabel="Reaction coordinate",
            ylabel="Free energy (kJ mol$^{-1}$)",
        )
        tcfig.label_panels(axes, x=-0.13)
        tcfig.export(
            fig,
            OUTPUT / "asymmetric_wide_jctc",
            source_path=__file__,
            alt_text=(
                "Staggered four-panel molecular-dynamics assembly with two wide analyses "
                "and two compact diagnostics."
            ),
        )


def long_assembly() -> None:
    coordinate = np.linspace(-2.3, 2.3, 160)
    cv1, cv2 = np.meshgrid(np.linspace(-2.2, 2.2, 90), np.linspace(-2.0, 2.0, 80))
    surface = (
        0.75 * (cv1**2 + cv2**2)
        - 2.5 * np.exp(-((cv1 + 0.9) ** 2 + (cv2 - 0.4) ** 2) / 0.55)
        - 1.9 * np.exp(-((cv1 - 1.0) ** 2 + (cv2 + 0.6) ** 2) / 0.5)
    )
    surface -= surface.min()

    with tcfig.assembly_canvas("long_story", profile="jctc", close=True) as (fig, axes):
        plot_free_energy_surface(
            axes["A"],
            cv1,
            cv2,
            surface,
            levels=np.arange(0, 7.5, 0.5),
        )
        axes["A"].set(xlabel="CV 1", ylabel="CV 2")

        plot_ecdf(axes["B"], {"State 1": RNG.normal(0.9, 0.12, 100)})
        axes["B"].set(xlabel="Lifetime (ns)", ylabel="ECDF")

        radius = np.linspace(0.2, 1.2, 150)
        plot_rdf(axes["C"], radius, 1 + 2.2 * np.exp(-((radius - 0.47) / 0.07) ** 2))
        axes["C"].set(xlabel="Distance (nm)", ylabel="$g(r)$")

        plot_free_energy(
            axes["D"],
            coordinate,
            1.3 * (coordinate**2 - 0.95) ** 2 + 0.16 * coordinate,
        )
        axes["D"].set(xlabel="Reaction coordinate", ylabel=r"$\Delta G$ (kJ mol$^{-1}$)")

        tcfig.label_panels(axes, x=-0.2)
        tcfig.export(
            fig,
            OUTPUT / "asymmetric_long_jctc",
            source_path=__file__,
            alt_text=(
                "Tall single-column molecular-dynamics narrative with a free-energy surface, "
                "two compact diagnostics, and a closing free-energy profile."
            ),
        )


if __name__ == "__main__":
    OUTPUT.mkdir(exist_ok=True)
    wide_assembly()
    long_assembly()
