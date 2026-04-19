"""
SIRR Dyad Reader — Smoke Tests
Runs dyad_reader.py on existing output files and validates structure.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dyad_reader import run_dyad

ENGINE = Path(__file__).parent.parent

PROFILE_A = str(ENGINE / "output.json")
PROFILE_B = str(ENGINE / "output_gen2_mazen_maternal.json")
OUTPUT = str(ENGINE / "output_dyad_test.json")


def _run():
    """Run dyad analysis and return result dict."""
    return run_dyad(
        PROFILE_A, PROFILE_B,
        "Muhab", "Mazen",
        "uncle_maternal", OUTPUT,
    )


def test_dyad_top_level_keys():
    result = _run()
    required = [
        "dyad",
        "cross_tradition_matches",
        "independence_grouped_matches",
        "bazi_ten_gods",
        "convergence_overlap",
        "dominant_element",
        "timing_2026",
        "shared_calendar_markers",
        "relationship_archetype",
    ]
    for key in required:
        assert key in result, f"Missing top-level key: {key}"


def test_dyad_bazi_ten_gods():
    result = _run()
    tg = result["bazi_ten_gods"]
    assert "a_to_b" in tg
    assert "b_to_a" in tg
    assert tg["a_to_b"]["ten_god"] != "", "a_to_b ten_god is empty"
    assert tg["b_to_a"]["ten_god"] != "", "b_to_a ten_god is empty"
    # Muhab (Water Yin) → Mazen (Wood Yin): Water produces Wood = 食神
    assert tg["a_to_b"]["ten_god"] == "食神"


def test_dyad_cross_tradition_matches():
    result = _run()
    matches = result["cross_tradition_matches"]
    assert isinstance(matches, list)
    assert len(matches) > 0, "cross_tradition_matches is empty"
    # Each match should have required fields
    for m in matches:
        assert "module_id" in m
        assert "match" in m
        assert m["match"] is True


def test_dyad_match_summary():
    result = _run()
    summary = result["match_summary"]
    assert summary["match_count"] > 0
    assert summary["total_compared"] > 0
    assert 0 < summary["match_rate"] < 1


def test_dyad_relationship_archetype():
    result = _run()
    arch = result["relationship_archetype"]
    assert arch["relationship_type"] == "uncle_maternal"
    assert arch["match_count"] > 0
    assert arch["independence_groups_matched"] > 0


def test_dyad_deterministic():
    """Same inputs should always produce identical output."""
    r1 = _run()
    r2 = _run()
    assert r1["match_summary"] == r2["match_summary"]
    assert r1["bazi_ten_gods"] == r2["bazi_ten_gods"]
    assert len(r1["cross_tradition_matches"]) == len(r2["cross_tradition_matches"])
