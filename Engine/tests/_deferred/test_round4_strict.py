"""
Golden-fixture regression tests for Round 4 cross-tradition modules (20 modules).
Tests against fixtures/expected_round4_strict.json using Muhab full_nasab profile.
"""
import json
import pytest
from datetime import date
from pathlib import Path

from sirr_core.types import InputProfile, SystemResult

# ── Load constants + profile + fixture ────────────────────────────────────────
ENGINE = Path(__file__).resolve().parent.parent
CONSTANTS = json.loads((ENGINE / "constants.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((ENGINE / "fixtures" / "expected_round4_strict.json").read_text(encoding="utf-8"))

# Profile: Muhab full_nasab (matches muhab_profile.json)
_PYT = {'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
        'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9,
        'S':1,'T':2,'U':3,'V':4,'W':5,'X':6,'Y':7,'Z':8}
_VOWELS = set('AEIOU')
_SUBJECT = "MUHAB OMAR ISMAIL OMAR AKIF MOHAMMAD WASFI ALAJZAJI"
_ARABIC = "مهاب عمر إسماعيل عمر عاكف محمد وصفي الاجزاجي"
_DOB = date(1996, 9, 23)

def _reduce(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n

_name_upper = _SUBJECT.upper()
_expression = _reduce(sum(_PYT.get(c, 0) for c in _name_upper))
_soul_urge = _reduce(sum(_PYT.get(c, 0) for c in _name_upper if c in _VOWELS))
_personality = _reduce(sum(_PYT.get(c, 0) for c in _name_upper if c not in _VOWELS and c != ' '))
_m = _reduce(_DOB.month); _d = _reduce(_DOB.day)
_y = _reduce(sum(int(c) for c in str(_DOB.year)))
_life_path = _reduce(_m + _d + _y)
_birthday_number = _reduce(_DOB.day)

_abjad_table = CONSTANTS["arabic_letters"]["abjad_kabir"]
_abjad_first = sum(_abjad_table.get(ch, 0) for ch in "مهاب")

PROFILE = InputProfile(
    subject=_SUBJECT, arabic=_ARABIC, dob=_DOB,
    today=date(2026, 2, 13),
    birth_time_local="10:14", timezone="Asia/Riyadh", location="Dhahran, Saudi Arabia",
    life_path=_life_path, expression=_expression, soul_urge=_soul_urge,
    personality=_personality, birthday_number=_birthday_number,
    abjad_first=_abjad_first, gender="male", variant="full_nasab",
    mother_name="MIRAL MOHAMMAD OTHMAN MASHHOUR",
    mother_name_ar="ميرال محمد عثمان مشهور",
    mother_dob="1970-10-23",
)

# ── Get natal chart and bazi data for dependent modules ──
from modules import natal_chart, bazi_pillars, julian

_r_natal = natal_chart.compute(PROFILE, CONSTANTS)
NATAL_DATA = _r_natal.data if _r_natal.certainty == "COMPUTED_STRICT" else None

_r_jdn = julian.compute(PROFILE, CONSTANTS)
_jdn = int(_r_jdn.data["jdn"])
_r_bazi = bazi_pillars.compute(PROFILE, CONSTANTS, jdn=_jdn)
BAZI_DATA = _r_bazi.data


# ══════════════════════════════════════════════════════════════════════════════
# Vedic (5)
# ══════════════════════════════════════════════════════════════════════════════

def test_kala_sarpa_check():
    from modules.kala_sarpa_check import compute
    r = compute(PROFILE, CONSTANTS, natal_chart_data=NATAL_DATA)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["kala_sarpa_check"]
    assert r.data["ksy_present"] == exp["ksy_present"]
    assert r.data["rahu_house"] == exp["rahu_house"]

def test_panchamahabhuta():
    from modules.panchamahabhuta import compute
    r = compute(PROFILE, CONSTANTS, natal_chart_data=NATAL_DATA)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["panchamahabhuta"]
    assert r.data["dominant_element"] == exp["dominant_element"]
    assert r.data["weakest_element"] == exp["weakest_element"]

def test_ayurvedic_constitution():
    from modules.ayurvedic_constitution import compute
    r = compute(PROFILE, CONSTANTS, natal_chart_data=NATAL_DATA)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["ayurvedic_constitution"]
    assert r.data["dominant_dosha"] == exp["dominant_dosha"]
    assert r.data["constitution_type"] == exp["constitution_type"]

def test_mantra_seed_syllable():
    from modules.mantra_seed_syllable import compute
    r = compute(PROFILE, CONSTANTS, natal_chart_data=NATAL_DATA)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["mantra_seed_syllable"]
    assert r.data["nakshatra"] == exp["nakshatra"]
    assert r.data["pada"] == exp["pada"]
    assert r.data["bija_syllable"] == exp["bija_syllable"]

def test_vedic_gem_prescription():
    from modules.vedic_gem_prescription import compute
    r = compute(PROFILE, CONSTANTS, natal_chart_data=NATAL_DATA)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["vedic_gem_prescription"]
    assert r.data["ascendant_lord"] == exp["ascendant_lord"]
    assert r.data["primary_gem"] == exp["primary_gem"]
    assert r.data["moon_lord"] == exp["moon_lord"]


# ══════════════════════════════════════════════════════════════════════════════
# Chinese (3)
# ══════════════════════════════════════════════════════════════════════════════

def test_bazi_10_year_forecast():
    from modules.bazi_10_year_forecast import compute
    r = compute(PROFILE, CONSTANTS, bazi_data=BAZI_DATA)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["bazi_10_year_forecast"]
    assert r.data["day_master_element"] == exp["day_master_element"]
    assert r.data["direction"] == exp["direction"]
    assert r.data["onset_age"] == exp["onset_age"]
    assert len(r.data["periods"]) == 8

def test_zi_wei_deeper():
    from modules.zi_wei_deeper import compute
    r = compute(PROFILE, CONSTANTS)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["zi_wei_deeper"]
    assert r.data["year_stem"] == exp["year_stem"]
    assert r.data["hua_lu_star"] == exp["hua_lu_star"]
    assert r.data["hua_ji_star"] == exp["hua_ji_star"]

def test_four_pillars_balance():
    from modules.four_pillars_balance import compute
    r = compute(PROFILE, CONSTANTS, bazi_data=BAZI_DATA)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["four_pillars_balance"]
    assert r.data["dominant_element"] == exp["dominant_element"]
    assert r.data["weakest_element"] == exp["weakest_element"]


# ══════════════════════════════════════════════════════════════════════════════
# Hebrew (3)
# ══════════════════════════════════════════════════════════════════════════════

def test_gematria_word_matches():
    from modules.gematria_word_matches import compute
    r = compute(PROFILE, CONSTANTS)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["gematria_word_matches"]
    assert r.data["full_name_gematria"] == exp["full_name_gematria"]
    assert r.data["root"] == exp["root"]

def test_sephirotic_path_analysis():
    from modules.sephirotic_path_analysis import compute
    r = compute(PROFILE, CONSTANTS, all_results=[])
    assert isinstance(r, SystemResult)
    exp = EXPECTED["sephirotic_path_analysis"]
    assert r.data["dominant_pillar"] == exp["dominant_pillar"]
    assert r.data["daat_active"] == exp["daat_active"]

def test_solomonic_correspondences():
    from modules.solomonic_correspondences import compute
    r = compute(PROFILE, CONSTANTS, natal_chart_data=NATAL_DATA)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["solomonic_correspondences"]
    assert r.data["birth_day_planet"] == exp["birth_day_planet"]
    assert r.data["birth_day_angel"] == exp["birth_day_angel"]


# ══════════════════════════════════════════════════════════════════════════════
# African (1)
# ══════════════════════════════════════════════════════════════════════════════

def test_african_day_name_extended():
    from modules.african_day_name_extended import compute
    r = compute(PROFILE, CONSTANTS)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["african_day_name_extended"]
    assert r.data["akan_name"] == exp["akan_name"]
    assert r.data["yoruba_name"] == exp["yoruba_name"]
    assert r.data["igbo_market_day"] == exp["igbo_market_day"]
    assert r.data["swahili_day"] == exp["swahili_day"]


# ══════════════════════════════════════════════════════════════════════════════
# Western (2)
# ══════════════════════════════════════════════════════════════════════════════

def test_enneagram_deeper():
    from modules.enneagram_deeper import compute
    r = compute(PROFILE, CONSTANTS, all_results=[])
    assert isinstance(r, SystemResult)
    exp = EXPECTED["enneagram_deeper"]
    assert r.data["base_type"] == exp["base_type"]
    assert r.data["center"] == exp["center"]
    assert r.data["growth_direction"] == exp["growth_direction"]

def test_hermetic_element_balance():
    from modules.hermetic_element_balance import compute
    r = compute(PROFILE, CONSTANTS, natal_chart_data=NATAL_DATA, all_results=[])
    assert isinstance(r, SystemResult)
    exp = EXPECTED["hermetic_element_balance"]
    assert r.data["dominant_element"] == exp["dominant_element"]
    assert r.data["sun_modality"] == exp["sun_modality"]


# ══════════════════════════════════════════════════════════════════════════════
# Scientific (2)
# ══════════════════════════════════════════════════════════════════════════════

def test_circadian_medicine():
    from modules.circadian_medicine import compute
    r = compute(PROFILE, CONSTANTS)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["circadian_medicine"]
    assert r.data["birth_organ"] == exp["birth_organ"]
    assert r.data["chronotype"] == exp["chronotype"]

def test_seasonal_psychology():
    from modules.seasonal_psychology import compute
    r = compute(PROFILE, CONSTANTS)
    assert isinstance(r, SystemResult)
    exp = EXPECTED["seasonal_psychology"]
    assert r.data["birth_season"] == exp["birth_season"]
    assert r.data["temperament_tendency"] == exp["temperament_tendency"]


# ══════════════════════════════════════════════════════════════════════════════
# Bridge (4) — tested with empty all_results (structure verification)
# ══════════════════════════════════════════════════════════════════════════════

def test_element_consensus():
    from modules.element_consensus import compute
    r = compute(PROFILE, CONSTANTS, all_results=[])
    assert isinstance(r, SystemResult)
    assert r.certainty == "COMPUTED_STRICT"
    assert "consensus_element" in r.data

def test_timing_consensus():
    from modules.timing_consensus import compute
    r = compute(PROFILE, CONSTANTS, all_results=[])
    assert isinstance(r, SystemResult)
    assert r.certainty == "COMPUTED_STRICT"
    assert "consensus" in r.data

def test_planetary_ruler_consensus():
    from modules.planetary_ruler_consensus import compute
    r = compute(PROFILE, CONSTANTS, all_results=[])
    assert isinstance(r, SystemResult)
    assert r.certainty == "COMPUTED_STRICT"
    assert "consensus_planet" in r.data

def test_archetype_consensus():
    from modules.archetype_consensus import compute
    r = compute(PROFILE, CONSTANTS, all_results=[])
    assert isinstance(r, SystemResult)
    assert r.certainty == "META"
    assert "consensus_archetype" in r.data


# ══════════════════════════════════════════════════════════════════════════════
# Structure validation
# ══════════════════════════════════════════════════════════════════════════════

def test_all_round4_return_system_result():
    """All 20 Round 4 modules return proper SystemResult with required fields."""
    from modules import (
        kala_sarpa_check, panchamahabhuta, ayurvedic_constitution,
        mantra_seed_syllable, vedic_gem_prescription,
        bazi_10_year_forecast, zi_wei_deeper, four_pillars_balance,
        gematria_word_matches, sephirotic_path_analysis, solomonic_correspondences,
        african_day_name_extended, enneagram_deeper, hermetic_element_balance,
        circadian_medicine, seasonal_psychology,
        element_consensus, timing_consensus, planetary_ruler_consensus, archetype_consensus,
    )

    modules = [
        (kala_sarpa_check, {"natal_chart_data": NATAL_DATA}),
        (panchamahabhuta, {"natal_chart_data": NATAL_DATA}),
        (ayurvedic_constitution, {"natal_chart_data": NATAL_DATA}),
        (mantra_seed_syllable, {"natal_chart_data": NATAL_DATA}),
        (vedic_gem_prescription, {"natal_chart_data": NATAL_DATA}),
        (bazi_10_year_forecast, {"bazi_data": BAZI_DATA}),
        (zi_wei_deeper, {}),
        (four_pillars_balance, {"bazi_data": BAZI_DATA}),
        (gematria_word_matches, {}),
        (sephirotic_path_analysis, {"all_results": []}),
        (solomonic_correspondences, {"natal_chart_data": NATAL_DATA}),
        (african_day_name_extended, {}),
        (enneagram_deeper, {"all_results": []}),
        (hermetic_element_balance, {"natal_chart_data": NATAL_DATA, "all_results": []}),
        (circadian_medicine, {}),
        (seasonal_psychology, {}),
        (element_consensus, {"all_results": []}),
        (timing_consensus, {"all_results": []}),
        (planetary_ruler_consensus, {"all_results": []}),
        (archetype_consensus, {"all_results": []}),
    ]

    for mod, kw in modules:
        r = mod.compute(PROFILE, CONSTANTS, **kw)
        assert isinstance(r, SystemResult), f"{mod.__name__} did not return SystemResult"
        assert r.id, f"{mod.__name__} missing id"
        assert r.name, f"{mod.__name__} missing name"
        assert r.certainty, f"{mod.__name__} missing certainty"
        assert isinstance(r.data, dict), f"{mod.__name__} data is not dict"
