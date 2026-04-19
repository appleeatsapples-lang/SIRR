"""Tests for the Quranic Figures Full module.
Coverage: computation, grand sums, structural findings, scope separation, policy.
"""
from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from sirr_core.types import InputProfile
from modules.quranic_figures import (
    compute, _reduce, _reduction_chain, _compute_abjad,
    _passes_through_11, ABJAD_KABIR, BLOCKED_PHRASES,
)

BASE = Path(__file__).resolve().parent.parent
CONSTANTS = json.loads((BASE / "constants.json").read_text(encoding="utf-8"))
LOCKED = json.loads(
    (BASE / "fixtures" / "quranic_figures" / "quranic_figures_full_locked.json")
    .read_text(encoding="utf-8")
)

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


@pytest.fixture(scope="module")
def figures(data):
    return data["figures"]


@pytest.fixture(scope="module")
def prophets(figures):
    return [f for f in figures if f["metadata"]["is_prophet"]]


# ─── COMPUTATION TESTS ───


def test_all_46_abjad_values(figures):
    """Every figure's abjad value matches the locked table."""
    locked_map = {f["name_ar"]: f["abjad"] for f in LOCKED}
    for fig in figures:
        assert fig["abjad_value"] == locked_map[fig["name_ar"]], (
            f"{fig['name_ar']}: expected {locked_map[fig['name_ar']]}, got {fig['abjad_value']}"
        )


def test_all_46_reduction_chains(figures):
    """Every figure's reduction chain matches the locked table."""
    locked_map = {f["name_ar"]: f["chain"] for f in LOCKED}
    for fig in figures:
        assert fig["reduction_chain"] == locked_map[fig["name_ar"]], (
            f"{fig['name_ar']}: expected {locked_map[fig['name_ar']]}, got {fig['reduction_chain']}"
        )


def test_all_46_final_values(figures):
    """Every figure's final value matches the locked table."""
    locked_map = {f["name_ar"]: f["final"] for f in LOCKED}
    for fig in figures:
        assert fig["final_value"] == locked_map[fig["name_ar"]], (
            f"{fig['name_ar']}: expected {locked_map[fig['name_ar']]}, got {fig['final_value']}"
        )


def test_yajuj_majuj_computed_separately(figures):
    """Yajuj and Majuj are separate records, not merged."""
    names = [f["name_ar"] for f in figures]
    assert "يأجوج" in names
    assert "مأجوج" in names
    yajuj = next(f for f in figures if f["name_ar"] == "يأجوج")
    majuj = next(f for f in figures if f["name_ar"] == "مأجوج")
    assert yajuj["abjad_value"] != majuj["abjad_value"]
    assert yajuj["final_value"] == 5
    assert majuj["final_value"] == 8


def test_farawn_tagged_title_as_name(figures):
    """Pharaoh has TITLE_AS_NAME special tag."""
    pharaoh = next(f for f in figures if f["name_ar"] == "فرعون")
    assert pharaoh["special_tag"] == "TITLE_AS_NAME"
    assert "TITLE_AS_NAME" in pharaoh["convergence_tags"]


# ─── GRAND SUM TESTS ───


def test_prophet_sum_equals_4327(data):
    assert data["checksums"]["prophet_sum"] == 4327


def test_prophet_sum_reduction_equals_7(data):
    assert data["checksums"]["prophet_sum_reduction"] == 7


def test_ibrahim_unique_at_7_within_prophets(data):
    sf = data["structural_findings"]
    assert sf["ibrahim_unique_at_7"]["unique_within_prophets"] is True


def test_full_corpus_grand_sum_retired(data):
    """Full corpus grand sum is retired — it must appear in retired_findings."""
    retired_names = [r["name"] for r in data["retired_findings"]]
    assert "Full corpus grand sum" in retired_names


# ─── STRUCTURAL FINDINGS TESTS ───


def test_seal_cluster_all_pass_11_to_2(data):
    sf = data["structural_findings"]
    assert sf["seal_cluster"]["all_11_to_2"] is True


def test_mosaic_axis_all_equal_8(data):
    sf = data["structural_findings"]
    assert sf["mosaic_axis"]["all_equal_8"] is True


def test_chain_endpoints_9_plus_2_equals_11(data):
    sf = data["structural_findings"]
    ep = sf["chain_endpoints"]
    assert ep["adam_final"] == 9
    assert ep["muhammad_final"] == 2
    assert ep["sum"] == 11


def test_adam_isa_frequency_both_25(data):
    sf = data["structural_findings"]
    freq = sf["adam_isa_frequency_25"]
    assert freq["adam_freq"] == 25
    assert freq["isa_freq"] == 25
    assert freq["match"] is True


def test_ayyub_raw_equals_19(figures):
    ayyub = next(f for f in figures if f["name_ar"] == "أيوب")
    assert ayyub["abjad_value"] == 19


# ─── FULL CORPUS TESTS ───


def test_master_11_full_set_count_equals_5(data):
    """5 figures pass through 11 to reach 2: Sulayman, Yahya, Muhammad, Maryam, Jibril."""
    full_set = data["master_11_chain"]["full_set"]
    assert len(full_set) == 5
    expected = {"سليمان", "يحيى", "محمد", "مريم", "جبريل"}
    assert set(full_set) == expected


def test_haman_breaks_ibrahim_uniqueness_in_full_corpus(figures):
    """Haman has final=7, same as Ibrahim, breaking prophet-chain uniqueness."""
    haman = next(f for f in figures if f["name_ar"] == "هامان")
    ibrahim = next(f for f in figures if f["name_ar"] == "إبراهيم")
    assert haman["final_value"] == 7
    assert ibrahim["final_value"] == 7


def test_antagonist_table_all_mismatches(data):
    """All antagonists diverge from their opposed prophet."""
    for ant in data["antagonist_table"]:
        if ant["prophet_final"] is not None:
            assert ant["mismatch"] is True
            assert ant["final"] != ant["prophet_final"]


def test_harut_marut_diverge(data):
    pair = next(p for p in data["paired_figures"] if p["pair"] == "هاروت/ماروت")
    assert pair["diverge"] is True
    assert pair["final_1"] != pair["final_2"]


def test_yajuj_majuj_diverge(data):
    pair = next(p for p in data["paired_figures"] if p["pair"] == "يأجوج/مأجوج")
    assert pair["diverge"] is True
    assert pair["final_1"] != pair["final_2"]


# ─── SCOPE SEPARATION TESTS ───


def test_ibrahim_uniqueness_scoped_to_prophet_chain(data):
    sf = data["structural_findings"]
    tags = sf["ibrahim_unique_at_7"]["tags"]
    assert "PROPHET_CHAIN_ONLY" in tags


def test_grand_sum_convergence_not_tagged_on_full_corpus(data):
    sf = data["structural_findings"]
    tags = sf["prophet_chain_grand_sum"]["tags"]
    assert "PROPHET_CHAIN_ONLY" in tags
    assert "FULL_CORPUS" not in tags


# ─── POLICY TESTS ───


def test_blocked_phrases_absent_from_output(result):
    """No blocked phrases appear anywhere in the output."""
    output_str = json.dumps(result.data, ensure_ascii=False).lower()
    for phrase in BLOCKED_PHRASES:
        assert phrase.lower() not in output_str, f"Blocked phrase found: {phrase}"


def test_kimi_metadata_cannot_elevate_confidence(data):
    """Extended tradition metadata from Kimi is LOW strength only."""
    # Check convergences fixture
    convergences = json.loads(
        (BASE / "fixtures" / "quranic_figures" / "quranic_figures_full_convergences.json")
        .read_text(encoding="utf-8")
    )
    # None of the CORE convergences reference Kimi
    for c in convergences:
        if c["strength"] in ("HIGH", "MEDIUM"):
            tags = c.get("tags", [])
            assert "EXTENDED_TRADITION_METADATA" not in tags


def test_gemini_psychological_layer_not_in_source_tier():
    """Extended tradition data is metadata-only — check the fixture."""
    ext = json.loads(
        (BASE / "fixtures" / "quranic_figures" / "quranic_figures_full_extended_tradition.json")
        .read_text(encoding="utf-8")
    )
    for item in ext:
        assert item["strength"] == "LOW"


def test_cognate_matches_tagged_expected_not_convergence():
    """Cognate Hebrew matches use EXPECTED_COGNATE_MATCH, not CROSS_TRADITION_CONVERGENCE."""
    hebrew = json.loads(
        (BASE / "fixtures" / "quranic_figures" / "quranic_figures_full_hebrew.json")
        .read_text(encoding="utf-8")
    )
    cognates = [h for h in hebrew if h["tag"] == "EXPECTED_COGNATE_MATCH"]
    assert len(cognates) == 4  # Adam, Lut, Yusuf, Ayyub
    for c in cognates:
        assert c["tag"] != "CROSS_TRADITION_CONVERGENCE"


def test_muhammad_tagged_cross_tradition_convergence():
    """Muhammad/מחמד is the only CROSS_TRADITION_CONVERGENCE in Hebrew table."""
    hebrew = json.loads(
        (BASE / "fixtures" / "quranic_figures" / "quranic_figures_full_hebrew.json")
        .read_text(encoding="utf-8")
    )
    cross = [h for h in hebrew if h["tag"] == "CROSS_TRADITION_CONVERGENCE"]
    assert len(cross) == 1
    assert cross[0]["name_ar"] == "محمد"
    assert cross[0]["abjad"] == 92
    assert cross[0]["gematria"] == 92


# ─── HELPER FUNCTION TESTS ───


def test_reduce_basic():
    assert _reduce(4327) == 7
    assert _reduce(92) == 2
    assert _reduce(9) == 9
    assert _reduce(45) == 9


def test_reduction_chain_format():
    assert _reduction_chain(45) == "9"
    assert _reduction_chain(275) == "14→5"
    assert _reduction_chain(4327) == "16→7"
    assert _reduction_chain(9) == "9"


def test_passes_through_11():
    assert _passes_through_11(92) is True   # 92 → 11 → 2
    assert _passes_through_11(191) is True  # 191 → 11 → 2
    assert _passes_through_11(38) is True   # 38 → 11 → 2
    assert _passes_through_11(45) is False  # 45 → 9
    assert _passes_through_11(19) is False  # 19 → 10 → 1


def test_compute_abjad_known_values():
    assert _compute_abjad("آدم") == 45
    assert _compute_abjad("محمد") == 92
    assert _compute_abjad("إبراهيم") == 259
    assert _compute_abjad("نوح") == 64


# ─── SYSTEM RESULT SHAPE ───


def test_result_shape(result):
    assert result.id == "quranic_figures"
    assert result.certainty == "LOOKUP_FIXED"
    assert result.question == "Q1_IDENTITY"
    assert len(result.references) >= 5


def test_entity_count(data):
    assert data["entity_count"] == 46
    assert data["record_count"] == 47  # Yajuj + Majuj = 2 records from 1 collective


def test_prophet_count(data):
    assert data["prophet_count"] == 25
