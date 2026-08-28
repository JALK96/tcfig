import pytest

from tcfig import resolve_size_mm


@pytest.mark.parametrize(
    ("profile", "slot", "expected"),
    [
        ("jctc", "single", 84.6),
        ("jcp", "double", 170.0),
        ("pccp", "single", 83.0),
        ("nature", "double", 183.0),
    ],
)
def test_profile_widths(profile, slot, expected):
    width, _ = resolve_size_mm(profile, slot, "standard")
    assert width == pytest.approx(expected)


def test_missing_intermediate_is_explicit():
    with pytest.raises(ValueError, match="no width slot"):
        resolve_size_mm("jcp", "intermediate", "standard")


def test_height_limit_is_enforced():
    with pytest.raises(ValueError, match="exceeds"):
        resolve_size_mm("nature", "double", 180)

