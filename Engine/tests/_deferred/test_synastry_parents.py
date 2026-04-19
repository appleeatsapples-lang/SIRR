"""Test synastry between gen2_omar and gen2_miral (parents demo pair)."""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runner import load_profile, load_constants
from modules.natal_chart import compute as compute_natal
from modules.synastry import compute as compute_synastry


def _run_parents_synastry():
    base = Path(__file__).parent.parent / "fixtures" / "family"
    path_a = str(base / "gen2_omar.json")
    path_b = str(base / "gen2_miral.json")

    constants = load_constants()
    profile_a = load_profile(path_a)
    profile_b = load_profile(path_b)

    natal_a = compute_natal(profile_a, constants)
    natal_b = compute_natal(profile_b, constants)

    natal_data_a = natal_a.data if natal_a.certainty == "COMPUTED_STRICT" else None
    natal_data_b = natal_b.data if natal_b.certainty == "COMPUTED_STRICT" else None

    result = compute_synastry(
        profile_a, constants,
        natal_chart_data=natal_data_a,
        second_profile_path=path_b,
        second_profile=profile_b,
        second_natal_data=natal_data_b,
    )
    return result


def test_synastry_parents_structure():
    r = _run_parents_synastry()
    d = r.data

    # Person A is Omar
    assert "OMAR" in d["person_a"]["name"]
    # Person B is Miral
    assert "MIRAL" in d["person_b"]["name"]

    # Cross aspects found (noon chart fallback)
    assert isinstance(d["cross_aspects"], list)
    assert len(d["cross_aspects"]) > 0

    # Harmony score is float 0-1
    assert isinstance(d["harmony_score"], float)
    assert 0.0 <= d["harmony_score"] <= 1.0

    # Challenge score is float 0-1
    assert isinstance(d["challenge_score"], float)
    assert 0.0 <= d["challenge_score"] <= 1.0

    # Connection type is valid
    assert d["connection_type"] in (
        "complementary", "mirror", "dynamic", "complex")

    # Composite sun sign present
    assert d["composite_sun_sign"] != "unknown"

    # SIRR metrics
    m = d["sirr_metrics"]
    assert "combined_life_path" in m
    assert m["lp_compatibility"] in (
        "highly compatible", "compatible", "neutral",
        "challenging", "dynamic")
    assert isinstance(m["shared_abjad_roots"], list)
    assert isinstance(m["shared_meta_patterns"], list)

    # Key aspects (top 5 or fewer)
    assert isinstance(d["key_aspects"], list)
    assert len(d["key_aspects"]) <= 5
    if d["key_aspects"]:
        ka = d["key_aspects"][0]
        assert "planet_a" in ka
        assert "planet_b" in ka
        assert "aspect" in ka
        assert "orb" in ka
        assert "nature" in ka
