"""Tests for Cross-Scripture Intersection module (#167).
Coverage: cross-tradition matches, within-Torah matches, master 11 chain,
retired findings, cognate ruling, policy.
"""
from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from sirr_core.types import InputProfile
from modules.cross_scripture import compute, BLOCKED_PHRASES

BASE = Path(__file__).resolve().parent.parent
CONSTANTS = json.loads((BASE / "constants.json").read_text(encoding="utf-8"))

PROFILE = InputProfile(
    subject="MUHAB OMAR ISMAIL OMAR AKIF MOHAMMAD WASFI ALAJZAJI",
    arabic="مهاب عمر إسماعيل عمر عاكف محمد وصفي [REDACTED-FAMILY-AR]",
    dob=date(YYYY,M,D),
    today=date(2026, 4, 2),
)


@pytest.fixture(scope="module")
def result():
    return compute(PROFILE, CONSTANTS)


@pytest.fixture(scope="module")
def data(result):
    return result.data


# ─── CROSS-TRADITION TESTS ───


def test_isa_yesous_both_reduce_to_6(data):
    """Isa (Arabic) and Jesus (Greek) both reduce to 6."""
    matches = data["cross_tradition_reduced_matches"]
    jesus = next(m for m in matches if m["figure_en"] == "Jesus / Isa")
    assert jesus["arabic"]["reduced"] == 6
    assert jesus["greek"]["reduced"] == 6
    assert jesus["hebrew"]["reduced"] == 8  # diverges
    assert jesus["match_type"] == "CROSS_TRADITION_REDUCED_MATCH"


def test_musa_moses_both_reduce_to_8(data):
    """Musa (Arabic) and Moses (Greek) both reduce to 8."""
    matches = data["cross_tradition_reduced_matches"]
    moses = next(m for m in matches if m["figure_en"] == "Moses / Musa")
    assert moses["arabic"]["reduced"] == 8
    assert moses["greek"]["reduced"] == 8
    assert moses["hebrew"]["reduced"] == 3  # diverges
    assert moses["match_type"] == "CROSS_TRADITION_REDUCED_MATCH"


def test_cross_match_count(data):
    assert data["cross_match_count"] == 2


def test_no_triple_reduced_match_found(data):
    """No triple reduced matches exist (all have at least one divergence)."""
    for match in data["cross_tradition_reduced_matches"]:
        systems = [match["arabic"]["reduced"], match["greek"]["reduced"], match["hebrew"]["reduced"]]
        assert len(set(systems)) > 1, "Triple match found — should not exist"


# ─── WITHIN-TRADITION TESTS ───


def test_within_torah_match_count(data):
    assert data["within_match_count"] == 3


def test_yosef_yechezkel_156(data):
    match = next(m for m in data["within_tradition_matches"] if m["shared_value"] == 156)
    assert "Joseph" in match["figures_en"]
    assert "Ezekiel" in match["figures_en"]


def test_yitzchak_hagar_208(data):
    match = next(m for m in data["within_tradition_matches"] if m["shared_value"] == 208)
    assert "Isaac" in match["figures_en"]
    assert "Hagar" in match["figures_en"]


# ─── MASTER 11 CROSS-TRADITION TESTS ───


def test_master_11_count_across_all_three(data):
    """12 total master 11 entries across all three traditions."""
    assert data["master_11_total"] == 12


def test_greek_entries_in_master_11(data):
    """2 Greek entries in master 11 chain."""
    m11 = data["master_11_cross_tradition"]
    assert m11["greek"]["count"] == 2


def test_hebrew_entries_in_master_11(data):
    """5 Hebrew entries in master 11 chain."""
    m11 = data["master_11_cross_tradition"]
    assert m11["hebrew"]["count"] == 5


def test_arabic_entries_in_master_11(data):
    """5 Arabic entries in master 11 chain."""
    m11 = data["master_11_cross_tradition"]
    assert m11["arabic"]["count"] == 5


# ─── RETIRED FINDINGS TESTS ───


def test_cognate_pairs_tagged_expected_not_convergence(data):
    """Cognate pairs are retired — not treated as convergence."""
    retired = data["retired_findings"]
    cognate = next(r for r in retired if "cognate" in r["finding"].lower())
    assert cognate["tag"] == "RETIRED"


def test_hawwa_ayyub_rejected(data):
    """חוה=19 ↔ أيوب=19 was Grok-rejected."""
    retired = data["retired_findings"]
    hawwa = next(r for r in retired if "חוה" in r["finding"])
    assert "GROK_REJECTED" in hawwa["reason"]


# ─── CORPUS STATS TESTS ───


def test_corpus_total(data):
    stats = data["corpus_stats"]
    assert stats["torah_figures"] == 68
    assert stats["nt_figures"] == 34
    assert stats["quranic_figures"] == 46
    assert stats["total"] == 148


# ─── POLICY TESTS ───


def test_blocked_phrases_absent_from_output(result):
    """No blocked phrases appear anywhere in the output."""
    output_str = json.dumps(result.data, ensure_ascii=False).lower()
    for phrase in BLOCKED_PHRASES:
        assert phrase.lower() not in output_str, f"Blocked phrase found: {phrase}"


def test_grok_ruling_present(data):
    assert "tautological" in data["grok_ruling"]


# ─── SYSTEM RESULT SHAPE ───


def test_result_shape(result):
    assert result.id == "cross_scripture"
    assert result.certainty == "LOOKUP_FIXED"
    assert result.question == "Q1_IDENTITY"
    assert len(result.references) >= 5
