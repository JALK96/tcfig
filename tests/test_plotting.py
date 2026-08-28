import numpy as np
import pytest

mpl = pytest.importorskip("matplotlib")
mpl.use("Agg")

import tcfig
from tcfig.md import plot_replicas


def test_canvas_dimensions_and_validation():
    with tcfig.canvas(profile="jctc", width="single", height="standard", close=True) as (
        fig,
        ax,
    ):
        ax.plot([0, 1], [0, 1])
        ax.set(xlabel="Time (ps)", ylabel="Observable")
        report = tcfig.validate_figure(fig)
        assert report.ok
        assert report.width_mm == pytest.approx(84.6, abs=0.05)


def test_forbidden_colormap_fails():
    with tcfig.canvas(profile="house", close=True) as (fig, ax):
        ax.imshow(np.arange(9).reshape(3, 3), cmap="jet")
        report = tcfig.validate_figure(fig)
        assert any(issue.code == "forbidden-colormap" for issue in report.issues)


def test_replicas_shape_check():
    with (
        tcfig.canvas(profile="house", close=True) as (_, ax),
        pytest.raises(ValueError, match="shape"),
    ):
            plot_replicas(ax, [0, 1, 2], np.ones((2, 2)))


def test_tol_colormap_is_constructed():
    assert tcfig.get_cmap("tol_sunset").name == "tol_sunset"


def test_asymmetric_assembly_dimensions_and_labels():
    with tcfig.assembly_canvas("lead-right", profile="jctc", close=True) as (fig, axes):
        assert tuple(axes) == ("A", "B", "C")
        assert fig.get_size_inches()[0] * 25.4 == pytest.approx(177.8, abs=0.05)
        labels = tcfig.label_panels(axes)
        assert [label.get_text() for label in labels] == ["a", "b", "c"]
        assert tcfig.validate_figure(fig).ok
