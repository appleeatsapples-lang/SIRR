"""
SIRR Batch 9-13 — Regression Tests (35 new modules)
Tests against golden fixtures generated from the corrected 4-name Muhab profile.
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sirr_core.types import InputProfile
from modules import (
    julian, bazi_pillars, natal_chart,
    cornerstone, life_purpose, steiner_cycles, enneagram_dob,
    tarot_year, tarot_name, latin_ordinal,
    greek_isopsephy, coptic_isopsephy, armenian_gematria,
    georgian_gematria, agrippan, thelemic_gematria, trithemius,
    planetary_hours, god_of_day, celtic_tree, ogham, birth_rune,
    bazi_hidden_stems, bazi_ten_gods, bazi_combos, bazi_shensha,
    bazhai, meihua, pawukon, primbon, tibetan_mewa,
    dreamspell, tonalpohualli, ethiopian_asmat,
    rose_cross_sigil, planetary_kameas, ars_magna, gd_correspondences,
    taksir, bast_kasr, istikhara_adad, zakat_huruf, jafr, buduh,
    akan_kra_din, persian_abjad,
    antiscia, yogini_dasha, ashtottari_dasha,
    zi_wei_dou_shu, shadbala,
    almuten, reception, declinations, midpoints, harmonic_charts,
    zodiacal_releasing, solar_arc, dorothean_chronocrators,
    ashtakavarga, shodashavarga, tasyir, kalachakra_dasha,
    bonification, zairja, qimen, liu_ren,
    primary_directions, chara_dasha, sarvatobhadra, tajika, kp_system,
    taiyi, onmyodo, uranian,
    nadi_amsa, maramataka,
    babylonian_horoscope,
    sudarshana,
    mahabote, human_design, gene_keys,
)


def _load():
    base = Path(__file__).parent.parent
    constants = json.loads((base / "constants.json").read_text(encoding="utf-8"))
    expected = json.loads((base / "fixtures" / "expected_batch9_strict.json").read_text(encoding="utf-8"))
    profile = InputProfile(
        subject="MUHAB OMAR ISMAIL OMAR AKIF MOHAMMAD WASFI ALAJZAJI",
        arabic="\u0645\u0647\u0627\u0628 \u0639\u0645\u0631 \u0625\u0633\u0645\u0627\u0639\u064a\u0644 \u0639\u0645\u0631 \u0639\u0627\u0643\u0641 \u0645\u062d\u0645\u062f \u0648\u0635\u0641\u064a \u0627\u0644\u0627\u062c\u0632\u0627\u062c\u064a",
        dob=date(YYYY,M,D),
        today=date(2026, 2, 15),
        birth_time_local="10:14",
        timezone="Asia/Riyadh",
        location="Dhahran, Saudi Arabia",
        life_path=3, expression=11, soul_urge=5, personality=6,
        birthday_number=5, abjad_first=48,
    )
    return constants, expected, profile


def _bazi_data():
    c, e, p = _load()
    jdn = int(julian.compute(p, c).data["jdn"])
    return bazi_pillars.compute(p, c, jdn=jdn).data


def _natal_chart_data():
    c, e, p = _load()
    r = natal_chart.compute(p, c)
    return r.data if r.certainty == "COMPUTED_STRICT" else None


# ── Batch 9: Quick Wins ──

def test_cornerstone():
    c, e, p = _load()
    r = cornerstone.compute(p, c)
    assert r.data["cornerstone"] == e["cornerstone"]["cornerstone"]
    assert r.data["first_vowel"] == e["cornerstone"]["first_vowel"]
    assert r.data["capstone"] == e["cornerstone"]["capstone"]

def test_life_purpose():
    c, e, p = _load()
    r = life_purpose.compute(p, c)
    assert r.data["birth_day_reduced"] == e["life_purpose"]["birth_day_reduced"]
    assert r.data["millman_raw"] == e["life_purpose"]["millman_raw"]

def test_steiner_cycles():
    c, e, p = _load()
    r = steiner_cycles.compute(p, c)
    assert r.data["cycle_number"] == e["steiner_cycles"]["cycle_number"]
    assert r.data["phase_name"] == e["steiner_cycles"]["phase_name"]

def test_enneagram_dob():
    c, e, p = _load()
    r = enneagram_dob.compute(p, c)
    assert r.data["enneagram_type"] == e["enneagram_dob"]["enneagram_type"]
    assert r.data["type_name"] == e["enneagram_dob"]["type_name"]

def test_tarot_year():
    c, e, p = _load()
    r = tarot_year.compute(p, c)
    assert r.data["card_number"] == e["tarot_year"]["card_number"]
    assert r.data["card_name"] == e["tarot_year"]["card_name"]

def test_tarot_name():
    c, e, p = _load()
    r = tarot_name.compute(p, c)
    assert r.data["expression_card_number"] == e["tarot_name"]["expression_card_number"]
    assert r.data["expression_card_name"] == e["tarot_name"]["expression_card_name"]

def test_latin_ordinal():
    c, e, p = _load()
    r = latin_ordinal.compute(p, c)
    assert r.data["ordinal_sum"] == e["latin_ordinal"]["ordinal_sum"]
    assert r.data["ordinal_root"] == e["latin_ordinal"]["ordinal_root"]


# ── Batch 10: Gematria Battery ──

def test_greek_isopsephy():
    c, e, p = _load()
    r = greek_isopsephy.compute(p, c)
    assert r.data["total"] == e["greek_isopsephy"]["total"]
    assert r.data["root"] == e["greek_isopsephy"]["root"]

def test_coptic_isopsephy():
    c, e, p = _load()
    r = coptic_isopsephy.compute(p, c)
    assert r.data["total"] == e["coptic_isopsephy"]["total"]
    assert r.data["root"] == e["coptic_isopsephy"]["root"]

def test_armenian_gematria():
    c, e, p = _load()
    r = armenian_gematria.compute(p, c)
    assert r.data["total"] == e["armenian_gematria"]["total"]
    assert r.data["root"] == e["armenian_gematria"]["root"]

def test_georgian_gematria():
    c, e, p = _load()
    r = georgian_gematria.compute(p, c)
    assert r.data["total"] == e["georgian_gematria"]["total"]
    assert r.data["root"] == e["georgian_gematria"]["root"]

def test_agrippan():
    c, e, p = _load()
    r = agrippan.compute(p, c)
    assert r.data["total"] == e["agrippan"]["total"]
    assert r.data["root"] == e["agrippan"]["root"]

def test_thelemic_gematria():
    c, e, p = _load()
    r = thelemic_gematria.compute(p, c)
    assert r.data["total"] == e["thelemic_gematria"]["total"]
    assert r.data["root"] == e["thelemic_gematria"]["root"]

def test_trithemius():
    c, e, p = _load()
    r = trithemius.compute(p, c)
    assert r.data["cipher_sum"] == e["trithemius"]["cipher_sum"]
    assert r.data["cipher_root"] == e["trithemius"]["cipher_root"]

# ── Batch 11: Calendar Systems ──

def test_planetary_hours():
    c, e, p = _load()
    r = planetary_hours.compute(p, c)
    assert r.data["day_ruler"] == e["planetary_hours"]["day_ruler"]
    assert r.data["hour_ruler"] == e["planetary_hours"]["hour_ruler"]

def test_god_of_day():
    c, e, p = _load()
    r = god_of_day.compute(p, c)
    assert r.data["deity"] == e["god_of_day"]["deity"]
    assert r.data["day_of_year"] == e["god_of_day"]["day_of_year"]

def test_celtic_tree():
    c, e, p = _load()
    r = celtic_tree.compute(p, c)
    assert r.data["tree"] == e["celtic_tree"]["tree"]
    assert r.data["ogham_letter"] == e["celtic_tree"]["ogham_letter"]

def test_ogham():
    c, e, p = _load()
    r = ogham.compute(p, c)
    assert r.data["primary_fid"] == e["ogham"]["primary_fid"]
    assert r.data["primary_tree"] == e["ogham"]["primary_tree"]

def test_birth_rune():
    c, e, p = _load()
    r = birth_rune.compute(p, c)
    assert r.data["rune"] == e["birth_rune"]["rune"]
    assert r.data["rune_character"] == e["birth_rune"]["rune_character"]


# ── Batch 12: BaZi Sub-Layers ──

def test_bazi_hidden_stems():
    c, e, p = _load()
    bd = _bazi_data()
    r = bazi_hidden_stems.compute(p, c, bazi_data=bd)
    assert r.data["hidden_element_distribution"] == e["bazi_hidden_stems"]["hidden_element_distribution"]

def test_bazi_ten_gods():
    c, e, p = _load()
    bd = _bazi_data()
    r = bazi_ten_gods.compute(p, c, bazi_data=bd)
    assert r.data["day_master"] == e["bazi_ten_gods"]["day_master"]
    assert r.data["day_master_element"] == e["bazi_ten_gods"]["day_master_element"]

def test_bazi_combos():
    c, e, p = _load()
    bd = _bazi_data()
    r = bazi_combos.compute(p, c, bazi_data=bd)
    assert r.data["six_clashes"] == e["bazi_combos"]["six_clashes"]

def test_bazi_shensha():
    c, e, p = _load()
    bd = _bazi_data()
    r = bazi_shensha.compute(p, c, bazi_data=bd)
    assert r.data["day_master"] == e["bazi_shensha"]["day_master"]
    assert r.data["star_count"] == e["bazi_shensha"]["star_count"]

# ── Batch 13: Additional P1 Systems ──

def test_bazhai():
    c, e, p = _load()
    r = bazhai.compute(p, c)
    assert r.data["gua_number"] == e["bazhai"]["gua_number"]
    assert r.data["gua_name"] == e["bazhai"]["gua_name"]

def test_meihua():
    c, e, p = _load()
    r = meihua.compute(p, c)
    assert r.data["moving_line"] == e["meihua"]["moving_line"]

def test_pawukon():
    c, e, p = _load()
    r = pawukon.compute(p, c)
    assert r.data["wuku"] == e["pawukon"]["wuku"]
    assert r.data["saptawara"] == e["pawukon"]["saptawara"]

def test_primbon():
    c, e, p = _load()
    r = primbon.compute(p, c)
    assert r.data["weton"] == e["primbon"]["weton"]
    assert r.data["neptu_sum"] == e["primbon"]["neptu_sum"]

def test_tibetan_mewa():
    c, e, p = _load()
    r = tibetan_mewa.compute(p, c)
    assert r.data["mewa_number"] == e["tibetan_mewa"]["mewa_number"]
    assert r.data["parkha_name"] == e["tibetan_mewa"]["parkha_name"]

def test_dreamspell():
    c, e, p = _load()
    r = dreamspell.compute(p, c)
    assert r.data["kin"] == e["dreamspell"]["kin"]
    assert r.data["galactic_signature"] == e["dreamspell"]["galactic_signature"]

def test_tonalpohualli():
    c, e, p = _load()
    r = tonalpohualli.compute(p, c)
    assert r.data["trecena"] == e["tonalpohualli"]["trecena"]
    assert r.data["day_sign"] == e["tonalpohualli"]["day_sign"]

def test_ethiopian_asmat():
    c, e, p = _load()
    r = ethiopian_asmat.compute(p, c)
    assert r.data["total"] == e["ethiopian_asmat"]["total"]
    assert r.data["root"] == e["ethiopian_asmat"]["root"]

def test_rose_cross_sigil():
    c, e, p = _load()
    r = rose_cross_sigil.compute(p, c)
    assert r.data["path_length"] == e["rose_cross_sigil"]["path_length"]
    assert r.data["total_angular_travel"] == e["rose_cross_sigil"]["total_angular_travel"]

def test_planetary_kameas():
    c, e, p = _load()
    r = planetary_kameas.compute(p, c)
    assert r.data["planet"] == e["planetary_kameas"]["planet"]
    assert r.data["magic_constant"] == e["planetary_kameas"]["magic_constant"]

def test_ars_magna():
    c, e, p = _load()
    r = ars_magna.compute(p, c)
    assert r.data["dominant_dignity"] == e["ars_magna"]["dominant_dignity"]

def test_gd_correspondences():
    c, e, p = _load()
    r = gd_correspondences.compute(p, c)
    assert r.data["life_path"] == e["gd_correspondences"]["life_path"]
    assert r.data["expression"] == e["gd_correspondences"]["expression"]


# ── Batch 8: Islamic Ilm al-Huruf ──

def test_taksir():
    c, e, p = _load()
    r = taksir.compute(p, c)
    assert r.data["letter_count"] == e["taksir"]["letter_count"]
    assert r.data["depth"] == e["taksir"]["depth"]

def test_bast_kasr():
    c, e, p = _load()
    r = bast_kasr.compute(p, c)
    assert r.data["original_letters"] == e["bast_kasr"]["original_letters"]
    assert r.data["expanded_text"] == e["bast_kasr"]["expanded_text"]

def test_istikhara_adad():
    c, e, p = _load()
    r = istikhara_adad.compute(p, c)
    assert r.data["abjad_total"] == e["istikhara_adad"]["abjad_total"]

def test_zakat_huruf():
    c, e, p = _load()
    r = zakat_huruf.compute(p, c)
    assert r.data["abjad_total"] == e["zakat_huruf"]["abjad_total"]
    assert r.data["letter_count"] == e["zakat_huruf"]["letter_count"]

def test_jafr():
    c, e, p = _load()
    r = jafr.compute(p, c)
    assert r.data["name_letter_count"] == e["jafr"]["name_letter_count"]
    assert r.data["seed_offset"] == e["jafr"]["seed_offset"]

def test_buduh():
    c, e, p = _load()
    r = buduh.compute(p, c)
    assert r.data["abjad_total"] == e["buduh"]["abjad_total"]
    assert r.data["abjad_root"] == e["buduh"]["abjad_root"]

# ── Module 112: Akan Kra Din ──

def test_akan_kra_din():
    c, e, p = _load()
    r = akan_kra_din.compute(p, c)
    assert r.certainty == "LOOKUP_FIXED"
    assert r.data["birth_weekday"] == e["akan_kra_din"]["birth_weekday"]
    assert r.data["kra_name"] == e["akan_kra_din"]["kra_name"]
    assert r.data["day_akan"] == e["akan_kra_din"]["day_akan"]
    assert r.data["archetype"] == e["akan_kra_din"]["archetype"]

# ── Module 113: Persian Extended Abjad ──

def test_persian_abjad():
    c, e, p = _load()
    r = persian_abjad.compute(p, c)
    assert r.data["total"] == e["persian_abjad"]["total"]
    assert r.data["root"] == e["persian_abjad"]["root"]
    assert r.data["persian_letters_used"] == e["persian_abjad"]["persian_letters_used"]
    assert r.data["extension_delta"] == e["persian_abjad"]["extension_delta"]

# ── Module 114: Antiscia ──

def test_antiscia():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = antiscia.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["antiscia"]
    assert r.data["conjunction_count"] == exp["conjunction_count"]
    assert r.data["orb_used"] == exp["orb_used"]
    # Spot-check Mercury contra-antiscia value
    assert abs(r.data["planets"]["Mercury"]["contra_antiscia"] - 190.0406) < 0.001
    # Spot-check Moon antiscia
    assert abs(r.data["planets"]["Moon"]["antiscia"] - 231.7511) < 0.001

# ── Module 115: Yogini Dasha ──

def test_yogini_dasha():
    c, e, p = _load()
    r = yogini_dasha.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["yogini_dasha"]
    assert r.data["birth_nakshatra"] == exp["birth_nakshatra"]
    assert r.data["starting_yogini"] == exp["starting_yogini"]
    assert r.data["current_yogini"] == exp["current_yogini"]
    assert r.data["cycle_length_years"] == exp["cycle_length_years"]

# ── Module 116: Ashtottari Dasha ──

def test_ashtottari_dasha():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = ashtottari_dasha.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["ashtottari_dasha"]
    assert r.data["applicable"] == exp["applicable"]
    assert r.data["rahu_house"] == exp["rahu_house"]
    assert r.data["starting_planet"] == exp["starting_planet"]
    assert r.data["current_planet"] == exp["current_planet"]
    assert r.data["cycle_length_years"] == exp["cycle_length_years"]

# ── Module 117: Zi Wei Dou Shu ──

def test_zi_wei_dou_shu():
    c, e, p = _load()
    r = zi_wei_dou_shu.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["zi_wei_dou_shu"]
    assert r.data["applicable"] is True
    assert r.data["ming_gong"] == exp["ming_gong"]
    assert r.data["shen_gong"] == exp["shen_gong"]
    assert r.data["zi_wei_palace"] == exp["zi_wei_palace"]
    assert r.data["da_yun_direction"] == exp["da_yun_direction"]
    assert r.data["lunar_month"] == exp["lunar_month"]
    assert r.data["hour_branch"] == exp["hour_branch"]

# ── Module 118: Shadbala ──

def test_shadbala():
    c, e, p = _load()
    r = shadbala.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["shadbala"]
    assert r.data["applicable"] is True
    assert r.data["strongest"] == exp["strongest"]
    assert r.data["weakest"] == exp["weakest"]
    assert r.data["tithi"] == exp["tithi"]
    assert r.data["is_waxing"] is True
    assert r.data["is_daytime"] is True
    assert r.data["lagna"] == exp["lagna"]
    # Spot-check totals (allow ±0.5 for rounding)
    moon_total = r.data["planets"]["Moon"]["total"]
    assert 153.0 <= moon_total <= 154.5, f"Moon total {moon_total} out of range"
    venus_total = r.data["planets"]["Venus"]["total"]
    assert 29.0 <= venus_total <= 32.0, f"Venus total {venus_total} out of range"

# ── Module 119: Almuten Figuris ──

def test_almuten():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = almuten.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["almuten"]
    assert r.data["almuten"] == exp["almuten"]
    assert r.data["almuten_score"] == exp["almuten_score"]
    assert r.data["is_diurnal"] == exp["is_diurnal"]

# ── Module 120: Mutual Reception ──

def test_reception():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = reception.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["reception"]
    assert r.data["mutual_reception_count"] == exp["mutual_reception_count"]
    assert r.data["generosity_count"] == exp["generosity_count"]

# ── Module 121: Declinations ──

def test_declinations():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = declinations.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["declinations"]
    assert r.data["parallel_count"] == exp["parallel_count"]
    assert r.data["contraparallel_count"] == exp["contraparallel_count"]
    assert r.data["oob_count"] == exp["oob_count"]
    assert abs(r.data["declinations"]["Sun"] - exp["sun_declination"]) < 0.001

# ── Module 122: Midpoints ──

def test_midpoints():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = midpoints.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["midpoints"]
    assert r.data["total_midpoints"] == exp["total_midpoints"]
    assert r.data["activation_count"] == exp["activation_count"]
    assert r.data["unique_midpoint_count"] == exp["unique_midpoint_count"]

# ── Module 123: Harmonic Charts ──

def test_harmonic_charts():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = harmonic_charts.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["harmonic_charts"]
    assert r.data["total_conjunction_count"] == exp["total_conjunction_count"]

# ── Module 124: Zodiacal Releasing ──

def test_zodiacal_releasing():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = zodiacal_releasing.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["zodiacal_releasing"]
    assert r.data["fortune_sign"] == exp["fortune_sign"]
    assert r.data["spirit_sign"] == exp["spirit_sign"]
    assert r.data["current_fortune_l1_sign"] == exp["current_fortune_l1_sign"]
    assert r.data["current_fortune_l1_ruler"] == exp["current_fortune_l1_ruler"]
    assert r.data["current_spirit_l1_sign"] == exp["current_spirit_l1_sign"]
    assert r.data["current_spirit_l1_ruler"] == exp["current_spirit_l1_ruler"]

# ── Module 125: Solar Arc Directions ──

def test_solar_arc():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = solar_arc.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["solar_arc"]
    assert abs(r.data["solar_arc"] - exp["solar_arc"]) < 0.001
    assert r.data["contact_count"] == exp["contact_count"]

# ── Module 126: Dorothean Chronocrators ──

def test_dorothean_chronocrators():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = dorothean_chronocrators.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["dorothean_chronocrators"]
    assert r.data["sect_light"] == exp["sect_light"]
    assert r.data["sect_sign"] == exp["sect_sign"]
    assert r.data["element"] == exp["element"]
    assert r.data["current_period"] == exp["current_period"]
    assert r.data["current_ruler"] == exp["current_ruler"]
    assert r.data["total_years"] == exp["total_years"]

# ── Module 127: Ashtakavarga ──

def test_ashtakavarga():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = ashtakavarga.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["ashtakavarga"]
    assert r.data["strongest_sign"] == exp["strongest_sign"]
    assert r.data["strongest_bindus"] == exp["strongest_bindus"]
    assert r.data["weakest_sign"] == exp["weakest_sign"]
    assert r.data["weakest_bindus"] == exp["weakest_bindus"]

# ── Module 128: Shodashavarga ──

def test_shodashavarga():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = shodashavarga.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["shodashavarga"]
    assert r.data["navamsha_asc"] == exp["navamsha_asc"]
    assert r.data["strongest_planet"] == exp["strongest_planet"]
    assert r.data["weakest_planet"] == exp["weakest_planet"]

# ── Module 129: Tasyir ──

def test_tasyir():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = tasyir.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["tasyir"]
    assert r.data["hyleg"] == exp["hyleg"]
    assert r.data["directed_sign"] == exp["directed_sign"]
    assert r.data["age"] == exp["age"]
    assert r.data["current_contact_count"] == exp["current_contact_count"]

# ── Module 130: Kalachakra Dasha ──

def test_kalachakra_dasha():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = kalachakra_dasha.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["kalachakra_dasha"]
    assert r.data["nakshatra"] == exp["nakshatra"]
    assert r.data["pada"] == exp["pada"]
    assert r.data["direction"] == exp["direction"]
    assert r.data["start_sign"] == exp["start_sign"]
    assert r.data["current_period_sign"] == exp["current_period_sign"]
    assert r.data["age"] == exp["age"]


# ── Batch 18a: Hellenistic + Islamic + Chinese ──

def test_bonification():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = bonification.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["bonification"]["data"]
    assert r.data["strongest_planet"] == exp["strongest_planet"]
    assert r.data["weakest_planet"] == exp["weakest_planet"]
    assert r.data["total_bonified"] == exp["total_bonified"]
    assert r.data["total_maltreated"] == exp["total_maltreated"]
    assert r.data["is_diurnal"] == exp["is_diurnal"]


def test_zairja():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = zairja.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["zairja"]["data"]
    assert r.data["abjad_sum"] == exp["abjad_sum"]
    assert r.data["manzil_index"] == exp["manzil_index"]
    assert r.data["starting_manzil"] == exp["starting_manzil"]
    assert r.data["starting_letter"] == exp["starting_letter"]
    assert r.data["dominant_element"] == exp["dominant_element"]
    assert r.data["chord_sequence"] == exp["chord_sequence"]


def test_qimen():
    c, e, p = _load()
    ncd = _natal_chart_data()
    bd = _bazi_data()
    r = qimen.compute(p, c, natal_chart_data=ncd, bazi_data=bd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["qimen"]
    assert r.data["dun_type"] == exp["dun_type"]
    assert r.data["ju_number"] == exp["ju_number"]
    assert r.data["solar_term"] == exp["solar_term"]
    assert r.data["yuan"] == exp["yuan"]
    assert r.data["xun_head"] == exp["xun_head"]
    assert r.data["empty_branches"] == exp["empty_branches"]
    assert r.data["lead_star"] == exp["lead_star"]
    assert r.data["lead_star_pinyin"] == exp["lead_star_pinyin"]
    assert r.data["lead_door"] == exp["lead_door"]
    assert r.data["lead_door_pinyin"] == exp["lead_door_pinyin"]


def test_liu_ren():
    c, e, p = _load()
    ncd = _natal_chart_data()
    bd = _bazi_data()
    r = liu_ren.compute(p, c, natal_chart_data=ncd, bazi_data=bd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["liu_ren"]
    assert r.data["monthly_general"] == exp["monthly_general"]
    assert r.data["monthly_general_pinyin"] == exp["monthly_general_pinyin"]
    assert r.data["dominant_element"] == exp["dominant_element"]
    assert r.data["three_transmissions"][0]["branch"] == exp["transmission_initial"]
    assert r.data["three_transmissions"][1]["branch"] == exp["transmission_middle"]
    assert r.data["three_transmissions"][2]["branch"] == exp["transmission_final"]


def test_primary_directions():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = primary_directions.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["primary_directions"]
    assert r.data["method"] == exp["method"]
    assert r.data["obliquity"] == exp["obliquity"]
    assert r.data["ramc"] == exp["ramc"]
    assert r.data["total_events"] == exp["total_events"]


def test_chara_dasha():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = chara_dasha.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["chara_dasha"]
    assert r.data["lagna_sign"] == exp["lagna_sign"]
    assert r.data["lagna_parity"] == exp["lagna_parity"]
    assert r.data["progression_direction"] == exp["progression_direction"]
    assert r.data["current_dasha_sign"] == exp["current_dasha_sign"]
    assert r.data["current_dasha_lord"] == exp["current_dasha_lord"]
    assert r.data["total_cycle_years"] == exp["total_cycle_years"]


def test_sarvatobhadra():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = sarvatobhadra.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["sarvatobhadra"]
    assert r.data["vedha_count"] == exp["vedha_count"]
    assert r.data["positive_vedhas"] == exp["positive_vedhas"]
    assert r.data["negative_vedhas"] == exp["negative_vedhas"]
    assert r.data["natal_tithi"] == exp["natal_tithi"]
    assert r.data["natal_tithi_name"] == exp["natal_tithi_name"]
    assert r.data["moon_rashi"] == exp["moon_rashi"]


def test_tajika():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = tajika.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["tajika"]
    assert r.data["muntha_sign"] == exp["muntha_sign"]
    assert r.data["muntha_lord"] == exp["muntha_lord"]
    assert r.data["return_rising"] == exp["return_rising"]
    assert r.data["varsheshvara"] == exp["varsheshvara"]
    assert r.data["lagna_lord"] == exp["lagna_lord"]


def test_kp_system():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = kp_system.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["kp_system"]
    assert r.data["ayanamsa"] == exp["ayanamsa"]
    assert r.data["dominant_sub_lord"] == exp["dominant_sub_lord"]
    assert r.data["kp_planets"]["Sun"]["sign_lord"] == exp["kp_planets"]["Sun"]["sign_lord"]
    assert r.data["kp_planets"]["Sun"]["star_lord"] == exp["kp_planets"]["Sun"]["star_lord"]
    assert r.data["kp_planets"]["Sun"]["sub_lord"] == exp["kp_planets"]["Sun"]["sub_lord"]
    assert r.data["kp_planets"]["Moon"]["sign_lord"] == exp["kp_planets"]["Moon"]["sign_lord"]
    assert r.data["kp_planets"]["Moon"]["star_lord"] == exp["kp_planets"]["Moon"]["star_lord"]
    assert r.data["kp_planets"]["Moon"]["sub_lord"] == exp["kp_planets"]["Moon"]["sub_lord"]


# ── Batch 19: Tai Yi + Onmyōdō + Uranian ──

def test_taiyi():
    c, e, p = _load()
    r = taiyi.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["taiyi"]
    assert r.data["method"] == exp["method"]
    assert r.data["accumulated_years"] == exp["accumulated_years"]
    assert r.data["taiyi_palace"] == exp["taiyi_palace"]
    assert r.data["taiyi_palace_element"] == exp["taiyi_palace_element"]
    assert r.data["grand_cycle_phase"] == exp["grand_cycle_phase"]
    assert r.data["host_guest_relationship"] == exp["host_guest_relationship"]
    assert r.data["year_stem"] == exp["year_stem"]
    assert r.data["year_branch"] == exp["year_branch"]


def test_onmyodo():
    c, e, p = _load()
    r = onmyodo.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["onmyodo"]
    assert r.data["method"] == exp["method"]
    assert r.data["yin_yang"] == exp["yin_yang"]
    assert r.data["birth_element"] == exp["birth_element"]
    assert r.data["eto"]["eto_name"] == exp["eto_name"]
    assert r.data["rokuyo"]["reading"] == exp["rokuyo_reading"]
    assert r.data["juni_sho"]["quality"] == exp["juni_sho_quality"]
    assert r.data["day_yin_yang"] == exp["day_yin_yang"]


def test_uranian():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = uranian.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["uranian"]
    assert r.data["method"] == exp["method"]
    assert r.data["point_count"] == exp["point_count"]
    assert r.data["tnp_count"] == exp["tnp_count"]
    assert r.data["midpoint_count"] == exp["midpoint_count"]
    assert r.data["picture_count"] == exp["picture_count"]
    assert r.data["dominant_point"] == exp["dominant_point"]


# ── Batch 20: Nadi Amsa + Maramataka ──

def test_nadi_amsa():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = nadi_amsa.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["nadi_amsa"]
    assert r.data["method"] == exp["method"]
    assert r.data["ayanamsa"] == exp["ayanamsa"]
    assert r.data["dominant_tattwa"] == exp["dominant_tattwa"]
    assert r.data["lagna_nadi_amsa"]["amsa_index"] == exp["lagna_amsa_index"]
    assert r.data["lagna_nadi_amsa"]["tattwa"] == exp["lagna_tattwa"]
    assert r.data["lagna_nadi_amsa"]["nadi_name"] == exp["lagna_nadi_name"]
    assert r.data["moon_nadi_amsa"]["amsa_index"] == exp["moon_amsa_index"]
    assert r.data["moon_nadi_amsa"]["tattwa"] == exp["moon_tattwa"]


def test_maramataka():
    c, e, p = _load()
    r = maramataka.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["maramataka"]
    assert r.data["method"] == exp["method"]
    assert r.data["lunar_day"] == exp["lunar_day"]
    assert r.data["night_name"] == exp["night_name"]
    assert r.data["night_quality"] == exp["night_quality"]
    assert r.data["moon_phase_name"] == exp["moon_phase_name"]
    assert r.data["tangaroa_proximity"] == exp["tangaroa_proximity"]
    assert r.data["is_tangaroa_night"] == exp["is_tangaroa_night"]


# ── Batch 21a: Babylonian Nativity Horoscope ──

def test_babylonian_horoscope():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = babylonian_horoscope.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["babylonian_horoscope"]
    assert r.data["method"] == exp["method"]
    assert r.data["babylonian_ayanamsa"] == exp["babylonian_ayanamsa"]
    assert r.data["lunar_day"] == exp["lunar_day"]
    assert r.data["babylonian_month"] == exp["babylonian_month"]
    assert r.data["month_length"] == exp["month_length"]
    assert r.data["birth_watch"] == exp["birth_watch"]
    assert r.data["babylonian_positions"]["Sun"]["akkadian_sign"] == exp["babylonian_positions"]["Sun"]["akkadian_sign"]
    assert r.data["babylonian_positions"]["Moon"]["akkadian_sign"] == exp["babylonian_positions"]["Moon"]["akkadian_sign"]
    assert r.data["babylonian_positions"]["Jupiter"]["akkadian_sign"] == exp["babylonian_positions"]["Jupiter"]["akkadian_sign"]
    assert r.data["planet_order"] == exp["planet_order"]


# ── Batch 21b: Sudarshana Chakra ──

def test_sudarshana():
    c, e, p = _load()
    ncd = _natal_chart_data()
    r = sudarshana.compute(p, c, natal_chart_data=ncd)
    assert r.certainty == "COMPUTED_STRICT"
    exp = e["sudarshana"]
    assert r.data["ayanamsha"] == exp["ayanamsha"]
    assert r.data["completed_years"] == exp["completed_years"]
    assert r.data["active_house"] == exp["active_house"]
    assert r.data["cycle_position"] == exp["cycle_position"]
    assert r.data["wheels"]["lagna"]["start_sign"] == exp["wheels"]["lagna"]["start_sign"]
    assert r.data["wheels"]["lagna"]["active_sign"] == exp["wheels"]["lagna"]["active_sign"]
    assert r.data["wheels"]["sun"]["start_sign"] == exp["wheels"]["sun"]["start_sign"]
    assert r.data["wheels"]["sun"]["active_sign"] == exp["wheels"]["sun"]["active_sign"]
    assert r.data["wheels"]["moon"]["start_sign"] == exp["wheels"]["moon"]["start_sign"]
    assert r.data["wheels"]["moon"]["active_sign"] == exp["wheels"]["moon"]["active_sign"]
    assert r.data["triple_activation"] == exp["triple_activation"]
    assert r.data["natal_triple_conjunction"] == exp["natal_triple_conjunction"]
    assert r.data["year_quality"] == exp["year_quality"]


# ── Round 2: Mahabote + Human Design + Gene Keys ──

def test_mahabote():
    c, e, p = _load()
    r = mahabote.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["adjusted_year"] == e["mahabote"]["adjusted_year"]
    assert r.data["remainder"] == e["mahabote"]["remainder"]
    assert r.data["house1_planet"] == e["mahabote"]["house1_planet"]
    assert r.data["birth_animal"] == e["mahabote"]["birth_animal"]
    assert r.data["birth_planet"] == e["mahabote"]["birth_planet"]
    assert r.data["direction"] == e["mahabote"]["direction"]


def test_human_design():
    c, e, p = _load()
    r = human_design.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["type"] == e["human_design"]["type"]
    assert r.data["profile"] == e["human_design"]["profile"]
    assert r.data["authority"] == e["human_design"]["authority"]
    assert len(r.data["all_activated_gates"]) > 0
    assert len(r.data["defined_channels"]) >= 0


def test_gene_keys():
    c, e, p = _load()
    hd = human_design.compute(p, c)
    r = gene_keys.compute(p, c, human_design_data=hd.data)
    assert r.certainty == "COMPUTED_STRICT"
    assert "spheres" in r.data
    assert "lifes_work" in r.data["spheres"]
    lw = r.data["spheres"]["lifes_work"]
    assert lw["gate"] == e["gene_keys"]["lifes_work_gate"]
    assert lw["shadow"] == e["gene_keys"]["lifes_work_shadow"]
