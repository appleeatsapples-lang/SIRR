"""Tests for Torah Figures module (#165).
Coverage: computation, gematria values, chains, master 11, within-Torah matches, policy.
"""
from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from sirr_core.types import InputProfile
from modules.torah_figures import (
    compute, _reduce, _reduction_chain, _compute_gematria,
    _passes_through_11, GEMATRIA_STANDARD, BLOCKED_PHRASES,
)

BASE = Path(__file__).resolve().parent.parent
CONSTANTS = json.loads((BASE / "constants.json").read_text(encoding="utf-8"))
LOCKED = json.loads(
    (BASE / "fixtures" / "scripture" / "torah_figures_locked.json")
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


# ─── COMPUTATION TESTS ───


def test_all_68_gematria_values(figures):
    """Every figure's gematria value matches the locked table."""
    locked_map = {f["name_he"]: f["gematria"] for f in LOCKED}
    for fig in figures:
        assert fig["gematria_value"] == locked_map[fig["name_he"]], (
            f"{fig['name_he']}: expected {locked_map[fig['name_he']]}, got {fig['gematria_value']}"
        )


def test_all_68_reduction_chains(figures):
    """Every figure's reduction chain matches the locked table."""
    locked_map = {f["name_he"]: f["chain"] for f in LOCKED}
    for fig in figures:
        assert fig["reduction_chain"] == locked_map[fig["name_he"]], (
            f"{fig['name_he']}: expected {locked_map[fig['name_he']]}, got {fig['reduction_chain']}"
        )


def test_all_68_final_values(figures):
    """Every figure's final value matches the locked table."""
    locked_map = {f["name_he"]: f["final"] for f in LOCKED}
    for fig in figures:
        assert fig["final_value"] == locked_map[fig["name_he"]], (
            f"{fig['name_he']}: expected {locked_map[fig['name_he']]}, got {fig['final_value']}"
        )


def test_figure_count(data):
    assert data["figure_count"] == 68


# ─── SOFIT RULING TESTS ───


def test_ruling_no_sofit_values():
    """Standard values only — mem=40 not 600, nun=50 not 700."""
    assert GEMATRIA_STANDARD["מ"] == 40
    assert GEMATRIA_STANDARD["נ"] == 50
    assert GEMATRIA_STANDARD["כ"] == 20
    assert GEMATRIA_STANDARD["פ"] == 80
    assert GEMATRIA_STANDARD["צ"] == 90
    # No sofit keys in table
    for val in GEMATRIA_STANDARD.values():
        assert val <= 400, f"Sofit value detected: {val}"


def test_adam_45_not_sofit():
    """Adam = 45 with standard, would be 605 with sofit mem."""
    assert _compute_gematria("אדם") == 45


def test_yosef_156_not_sofit():
    """Joseph = 156 with standard, would be 876 with sofit pe."""
    assert _compute_gematria("יוסף") == 156


def test_miriam_290_not_sofit():
    """Miriam = 290 with standard, would be 850 with sofit mem."""
    assert _compute_gematria("מרים") == 290


# ─── MASTER 11 TESTS ───


def test_yaakov_master_11():
    """Jacob (182) passes through 11."""
    assert _passes_through_11(182) is True


def test_issachar_master_11():
    """Issachar (830) passes through 11."""
    assert _passes_through_11(830) is True


def test_miriam_master_11():
    """Miriam (290) passes through 11."""
    assert _passes_through_11(290) is True


def test_goliath_master_11():
    """Goliath (443) passes through 11."""
    assert _passes_through_11(443) is True


def test_abigail_master_11():
    """Abigail (56) passes through 11."""
    assert _passes_through_11(56) is True


def test_master_11_count(data):
    """5 Torah figures have master 11 chains."""
    assert data["master_11_count"] == 5


def test_miriam_equals_290_master_11(figures):
    miriam = next(f for f in figures if f["name_en"] == "Miriam")
    assert miriam["gematria_value"] == 290
    assert miriam["master_11"] is True


# ─── WITHIN-TORAH MATCH TESTS ───


def test_yosef_equals_yechezkel_156(data):
    """Joseph = Ezekiel = 156."""
    match = next(m for m in data["within_torah_matches"] if m["shared_value"] == 156)
    assert "יוסף" in match["figures"]
    assert "יחזקאל" in match["figures"]
    assert match["verified"] is True


def test_yitzchak_equals_hagar_208(data):
    """Isaac = Hagar = 208."""
    match = next(m for m in data["within_torah_matches"] if m["shared_value"] == 208)
    assert "יצחק" in match["figures"]
    assert "הגר" in match["figures"]
    assert match["verified"] is True


def test_yehoshua_equals_tzippora_391(data):
    """Joshua = Zipporah = 391."""
    match = next(m for m in data["within_torah_matches"] if m["shared_value"] == 391)
    assert "יהושע" in match["figures"]
    assert "ציפורה" in match["figures"]
    assert match["verified"] is True


# ─── SPECIFIC FIGURE TESTS ───


def test_david_gematria():
    assert _compute_gematria("דוד") == 14


def test_moshe_gematria():
    assert _compute_gematria("משה") == 345


def test_avraham_gematria():
    assert _compute_gematria("אברהם") == 248


def test_shlomo_gematria():
    assert _compute_gematria("שלמה") == 375


# ─── POLICY TESTS ───


def test_blocked_phrases_absent_from_output(result):
    """No blocked phrases appear anywhere in the output."""
    output_str = json.dumps(result.data, ensure_ascii=False).lower()
    for phrase in BLOCKED_PHRASES:
        assert phrase.lower() not in output_str, f"Blocked phrase found: {phrase}"


def test_sofit_ruling_in_output(data):
    assert "NEVER_USED" in data["sofit_ruling"]


# ─── SYSTEM RESULT SHAPE ───


def test_result_shape(result):
    assert result.id == "torah_figures"
    assert result.certainty == "LOOKUP_FIXED"
    assert result.question == "Q1_IDENTITY"
    assert len(result.references) >= 4


# ─── HELPER FUNCTION TESTS ───


def test_reduce_basic():
    assert _reduce(45) == 9
    assert _reduce(248) == 5
    assert _reduce(182) == 2
    assert _reduce(9) == 9


def test_reduction_chain_format():
    assert _reduction_chain(45) == "9"
    assert _reduction_chain(248) == "14→5"
    assert _reduction_chain(182) == "11→2"
    assert _reduction_chain(9) == "9"


def test_passes_through_11_false():
    assert _passes_through_11(45) is False  # 45 → 9
    assert _passes_through_11(19) is False  # 19 → 10 → 1
