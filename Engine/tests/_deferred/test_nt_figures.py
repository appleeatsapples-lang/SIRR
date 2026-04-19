"""Tests for NT Figures module (#166).
Coverage: computation, isopsephy values, chains, master 11, historically attested, policy.
"""
from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from sirr_core.types import InputProfile
from modules.nt_figures import (
    compute, _reduce, _reduction_chain,
    _passes_through_11, ISOPSEPHY, BLOCKED_PHRASES,
)

BASE = Path(__file__).resolve().parent.parent
CONSTANTS = json.loads((BASE / "constants.json").read_text(encoding="utf-8"))
LOCKED = json.loads(
    (BASE / "fixtures" / "scripture" / "nt_figures_locked.json")
    .read_text(encoding="utf-8")
)

PROFILE = InputProfile(
    subject="MUHAB OMAR ISMAIL OMAR AKIF MOHAMMAD WASFI ALAJZAJI",
    arabic="مهاب عمر إسماعيل عمر عاكف محمد وصفي الاجزاجي",
    dob=date(1996, 9, 23),
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


def test_all_34_isopsephy_values(figures):
    """Every figure's isopsephy value matches the locked table."""
    locked_map = {f["name_gr"]: f["isopsephy"] for f in LOCKED}
    for fig in figures:
        assert fig["isopsephy_value"] == locked_map[fig["name_gr"]], (
            f"{fig['name_gr']}: expected {locked_map[fig['name_gr']]}, got {fig['isopsephy_value']}"
        )


def test_all_34_reduction_chains(figures):
    """Every figure's reduction chain matches the locked table."""
    locked_map = {f["name_gr"]: f["chain"] for f in LOCKED}
    for fig in figures:
        assert fig["reduction_chain"] == locked_map[fig["name_gr"]], (
            f"{fig['name_gr']}: expected {locked_map[fig['name_gr']]}, got {fig['reduction_chain']}"
        )


def test_all_34_final_values(figures):
    """Every figure's final value matches the locked table."""
    locked_map = {f["name_gr"]: f["final"] for f in LOCKED}
    for fig in figures:
        assert fig["final_value"] == locked_map[fig["name_gr"]], (
            f"{fig['name_gr']}: expected {locked_map[fig['name_gr']]}, got {fig['final_value']}"
        )


def test_figure_count(data):
    assert data["figure_count"] == 34


# ─── ISOPSEPHY TABLE TESTS ───


def test_no_value_6_in_isopsephy():
    """Digamma absent from koine Greek — no value 6 exists."""
    assert 6 not in ISOPSEPHY.values()


def test_zeta_equals_7():
    """ζ = 7 (not 6)."""
    assert ISOPSEPHY["ζ"] == 7


def test_final_sigma_equals_sigma():
    """Final sigma ς = same as σ = 200."""
    assert ISOPSEPHY["ς"] == ISOPSEPHY["σ"] == 200


# ─── KEY FIGURE TESTS ───


def test_yesous_888_confirmed(figures):
    """Ἰησοῦς = 888."""
    jesus = next(f for f in figures if f["name_en"] == "Jesus")
    assert jesus["isopsephy_value"] == 888


def test_yesous_reduces_to_6(figures):
    """888 → 24 → 6."""
    jesus = next(f for f in figures if f["name_en"] == "Jesus")
    assert jesus["final_value"] == 6
    assert jesus["reduction_chain"] == "24→6"


def test_yesous_historically_attested(data):
    """Jesus 888 has HISTORICALLY_ATTESTED tag."""
    ha = data["historically_attested"]
    assert len(ha) >= 1
    jesus_ha = next(h for h in ha if h["figure"] == "Ἰησοῦς")
    assert jesus_ha["value"] == 888
    assert jesus_ha["tag"] == "HISTORICALLY_ATTESTED"


# ─── MASTER 11 TESTS ───


def test_zechariah_master_11(figures):
    """Ζαχαρίας (920) passes through 11."""
    zach = next(f for f in figures if f["name_en"] == "Zechariah")
    assert zach["master_11"] is True
    assert zach["isopsephy_value"] == 920


def test_timothy_master_11(figures):
    """Τιμόθεος (704) passes through 11."""
    tim = next(f for f in figures if f["name_en"] == "Timothy")
    assert tim["master_11"] is True
    assert tim["isopsephy_value"] == 704


def test_master_11_count(data):
    """2 NT figures have master 11 chains."""
    assert data["master_11_count"] == 2


# ─── POLICY TESTS ───


def test_blocked_phrases_absent_from_output(result):
    """No blocked phrases appear anywhere in the output."""
    output_str = json.dumps(result.data, ensure_ascii=False).lower()
    for phrase in BLOCKED_PHRASES:
        assert phrase.lower() not in output_str, f"Blocked phrase found: {phrase}"


# ─── SYSTEM RESULT SHAPE ───


def test_result_shape(result):
    assert result.id == "nt_figures"
    assert result.certainty == "LOOKUP_FIXED"
    assert result.question == "Q1_IDENTITY"
    assert len(result.references) >= 5


# ─── HELPER FUNCTION TESTS ───


def test_reduce_basic():
    assert _reduce(888) == 6
    assert _reduce(1119) == 3
    assert _reduce(920) == 2
    assert _reduce(9) == 9


def test_reduction_chain_format():
    assert _reduction_chain(888) == "24→6"
    assert _reduction_chain(1119) == "12→3"
    assert _reduction_chain(9) == "9"


def test_passes_through_11_values():
    assert _passes_through_11(920) is True   # 920 → 11 → 2
    assert _passes_through_11(704) is True   # 704 → 11 → 2
    assert _passes_through_11(888) is False  # 888 → 24 → 6
