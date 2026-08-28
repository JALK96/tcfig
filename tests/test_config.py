from tcfig import available_profiles, get_profile, get_tokens


def test_expected_profiles_exist():
    profiles = available_profiles()
    assert {"house", "jctc", "jcp", "pccp", "wiley_jcc", "nature"} <= set(profiles)


def test_aliases_resolve():
    assert get_profile("molecular_simulation").name == "taylor_francis_generic"
    assert get_profile("tca").name == "springer_tc"


def test_palette_tokens_exist():
    assert len(get_tokens()["color"]["palettes"]["tol_bright"]) == 7
    assert len(get_tokens()["color"]["palettes"]["tol_vibrant"]) == 7
    assert len(get_tokens()["color"]["palettes"]["tol_dark"]) == 11
