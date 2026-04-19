"""
Tests for the narrative synthesis module.
Validates schema, policy compliance, and module ID validity.
"""
import json
from pathlib import Path

OUTPUT = Path(__file__).parent.parent / "fixtures" / "synthetic_output.json"


def _load():
    return json.loads(OUTPUT.read_text(encoding="utf-8"))


def test_narrative_schema():
    """Verify narrative block has all required top-level keys."""
    data = _load()
    assert "narrative" in data, "output.json missing 'narrative' key"
    n = data["narrative"]

    # Top-level keys
    assert n["version"].startswith("narrative_v")
    assert "generated_at" in n
    assert "profile_ref" in n
    assert "policy" in n
    assert "core_numbers" in n
    assert "convergence_summary" in n
    assert "mirror_reading" in n

    # Policy
    assert n["policy"]["no_prediction_language"] is True
    assert n["policy"]["no_destiny_claims"] is True
    assert n["policy"]["mode"] == "mirror_not_crystal_ball"

    # Mirror reading sub-keys
    mr = n["mirror_reading"]
    assert "headline" in mr
    assert "threads" in mr
    assert len(mr["threads"]) >= 2
    assert "cross_tradition_clusters" in mr
    assert "elemental_summary" in mr
    assert "integration_principles" in mr
    assert "uncertainties" in mr

    # Core numbers present
    cn = n["core_numbers"]
    assert "life_path" in cn
    assert "expression" in cn
    assert "soul_urge" in cn
    assert "personality" in cn
    assert "birthday" in cn
    assert "abjad_first" in cn

    # Convergence summary
    cs = n["convergence_summary"]
    assert "dominant_root" in cs
    assert "dominant_systems" in cs
    assert "secondary" in cs


def test_narrative_no_prediction_language():
    """Verify no banned phrases in narrative text."""
    data = _load()
    text = json.dumps(data["narrative"]).lower()
    banned = [
        "you will", "your destiny", "you are fated", "will happen",
        "your purpose is", "destined", "meant to be", "should become",
        "you must", "your fate is",
    ]
    for phrase in banned:
        assert phrase not in text, f"Banned phrase found in narrative: '{phrase}'"


def test_narrative_module_ids_valid():
    """Verify all referenced module_ids exist in results."""
    data = _load()
    valid_ids = {r["id"] for r in data["results"]}
    # profile.core_numbers is a special synthetic source tag, not a module
    valid_ids.add("profile.core_numbers")

    n = data["narrative"]
    mr = n["mirror_reading"]

    for thread in mr.get("threads", []):
        for mid in thread.get("module_ids", []):
            assert mid in valid_ids, f"Invalid module_id in thread '{thread['id']}': {mid}"

    for cluster in mr.get("cross_tradition_clusters", []):
        for mid in cluster.get("module_ids", []):
            assert mid in valid_ids, f"Invalid module_id in cluster '{cluster['id']}': {mid}"

    for mid in mr.get("elemental_summary", {}).get("module_ids", []):
        assert mid in valid_ids, f"Invalid module_id in elemental_summary: {mid}"
