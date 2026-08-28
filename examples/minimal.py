from pathlib import Path

import matplotlib as mpl
import numpy as np

mpl.use("Agg")

import tcfig

OUTPUT = Path(__file__).with_name("output")

x = np.linspace(0, 10, 250)
y = np.sin(x) * np.exp(-x / 12)

with tcfig.canvas(profile="jctc", width="single", height="standard", close=True) as (
    fig,
    ax,
):
    ax.plot(x, y)
    ax.set(xlabel="Time (ps)", ylabel="Correlation")
    tcfig.export(
        fig,
        OUTPUT / "minimal_jctc",
        data={"time_ps": x, "correlation": y},
        alt_text="Damped oscillatory correlation as a function of simulation time.",
        source_path=__file__,
    )
