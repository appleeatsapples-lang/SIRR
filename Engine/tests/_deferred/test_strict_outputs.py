"""
SIRR v2 New Systems — Regression Tests
Tests every COMPUTED_STRICT and key LOOKUP_FIXED module against golden fixtures.
If any of these break, something fundamental has changed.
"""
import json
import sys
from datetime import date
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sirr_core.types import InputProfile
from modules import (
    julian, biorhythm, geomancy, challenges, attitude, profection,
    bridges, notarikon, atbash, albam, nayin, iching, wafq, essence,
    firdaria, compound, mayan, cardology, sabian, temperament,
    bazi_growth, vedic_tithi, vedic_yoga, synthesis,
    pinnacles, personal_year, karmic_debt, lo_shu_grid,
    hidden_passion, subconscious_self, maturity,
    abjad_kabir, abjad_saghir, abjad_wusta, abjad_maghribi, hijri,
    solar_lunar, elemental_letters, luminous_dark,
    decan, day_ruler, tarot_birth, dwad,
    hebrew_gematria, avgad, tree_of_life, hebrew_calendar,
    chinese_zodiac, nine_star_ki, flying_star, bazi_pillars,
    bazi_daymaster, bazi_luck_pillars,
    # Mandaean gematria + malwasha
    mandaean_gematria, malwasha,
    # P0 gap analysis: remaining modules
    chaldean, ifa, manazil, nakshatra, vimshottari,
    # Ephemeris Phase 1: Foundation
    natal_chart, house_system, aspects,
    # Ephemeris Phase 2: High-value systems
    essential_dignities, sect, arabic_parts,
    solar_return, progressions, fixed_stars,
    # Egyptian
    egyptian_decan,
    # Islamic lettrism

    # Arabic Linguistic Sciences
    arabic_roots, arabic_morphology, name_semantics,
    arabic_phonetics, arabic_letter_nature,
    # Wave 1
    digit_patterns, lineage_computation, hijri_calendar_encoding,
    calligraphy_structure, divine_breath, letter_position_encoding,
    abjad_visual_architecture, name_weight, arabic_rhetoric, sonority_curve,
    larger_awfaq, qibla_as_axis, prayer_times_as_timing, chronobiology,
    void_matrix, barzakh_coefficient, hermetic_alignment,
    execution_pattern_analysis, minimum_viable_signature,
    # Round 5 Wave 1: Decoz layer
    balance_number, rational_thought, inclusion_table, special_letters,
    period_cycles, transit_letters, yearly_essence_cycle, minor_numbers,
    # Round 5 Wave 2: Tarot + Esoteric + Hellenistic
    tarot_greer_birth_cards, greer_zodiac_card, prenatal_syzygy,
    cheiro_extensions, roman_chronogram, hebrew_aiq_beker,
    # Round 5 Wave 3: Cross-tradition
    tibetan_parkha, tibetan_elements, tamil_panchapakshi,
    chinese_jian_chu, igbo_market_day, zoroastrian_day_yazata,
    vedic_arudha_pada, vedic_upapada_lagna, vedic_pushkara_navamsha,
    bazi_san_he_san_hui, zwds_si_hua_palace, hebrew_mispar_variants,
    # Round 5 Wave 4: Planes of Expression
    planes_of_expression,
)


def _load():
    base = Path(__file__).parent.parent
    constants = json.loads((base / "constants.json").read_text(encoding="utf-8"))
    expected = json.loads((base / "fixtures" / "expected_muhab_strict.json").read_text(encoding="utf-8"))
    profile = InputProfile(
        subject="MUHAB OMAR ISMAIL OMAR AKIF MOHAMMAD WASFI ALAJZAJI",
        arabic="\u0645\u0647\u0627\u0628 \u0639\u0645\u0631 \u0625\u0633\u0645\u0627\u0639\u064a\u0644 \u0639\u0645\u0631 \u0639\u0627\u0643\u0641 \u0645\u062d\u0645\u062f \u0648\u0635\u0641\u064a \u0627\u0644\u0627\u062c\u0632\u0627\u062c\u064a",
        dob=date(YYYY,M,D),
        today=date(2026, 2, 13),
        birth_time_local="10:14",
        timezone="Asia/Riyadh",
        location="Dhahran, Saudi Arabia",
        life_path=3, expression=11, soul_urge=5, personality=6,
        birthday_number=5, abjad_first=48, gender="male",
        mother_name="MIRAL MOHAMMAD OTHMAN MASHHOUR",
        mother_name_ar="ميرال محمد عثمان مشهور",
        mother_dob="1970-10-23",
    )
    return constants, expected, profile


def test_julian():
    c, e, p = _load()
    r = julian.compute(p, c)
    assert r.data["jdn"] == e["julian"]["jdn"]
    assert r.certainty == "COMPUTED_STRICT"


def test_biorhythm():
    c, e, p = _load()
    r = biorhythm.compute(p, c)
    assert r.data["days_alive"] == e["biorhythm"]["days_alive"]


def test_geomancy():
    c, e, p = _load()
    jdn = julian.compute(p, c).data["jdn"]
    r = geomancy.compute(p, c, jdn)
    assert r.data["index"] == e["geomancy"]["index"]
    assert r.data["figure"].startswith(e["geomancy"]["figure_starts_with"])


def test_challenges():
    c, e, p = _load()
    r = challenges.compute(p, c)
    assert r.data["challenge_1"] == e["challenges"]["challenge_1"]
    assert r.data["challenge_2"] == e["challenges"]["challenge_2"]
    assert r.data["challenge_3"] == e["challenges"]["challenge_3"]
    assert r.data["challenge_4"] == e["challenges"]["challenge_4"]


def test_attitude():
    c, e, p = _load()
    r = attitude.compute(p, c)
    assert r.data["raw"] == e["attitude"]["raw"]
    assert r.data["reduced"] == e["attitude"]["reduced"]


def test_profection():
    c, e, p = _load()
    r = profection.compute(p, c)
    assert r.data["age"] == e["profection"]["age"]
    assert r.data["house"] == e["profection"]["house"]


def test_bridges():
    c, e, p = _load()
    r = bridges.compute(p, c)
    assert r.data["bridges"]["lp_su"] == e["bridges"]["lp_su"]
    assert r.data["bridges"]["lp_pers"] == e["bridges"]["lp_pers"]


def test_notarikon():
    c, e, p = _load()
    r = notarikon.compute(p, c)
    assert r.data["arabic_sum"] == e["notarikon"]["arabic_sum"]
    assert r.data["arabic_root"] == e["notarikon"]["arabic_root"]
    assert r.data["latin_sum"] == e["notarikon"]["latin_sum"]


def test_atbash():
    c, e, p = _load()
    r = atbash.compute(p, c)
    assert r.data["atbash_sum"] == e["atbash"]["atbash_sum"]
    assert r.data["atbash_root"] == e["atbash"]["atbash_root"]


def test_albam():
    c, e, p = _load()
    r = albam.compute(p, c)
    assert r.data["albam_sum"] == e["albam"]["albam_sum"]
    assert r.data["albam_root"] == e["albam"]["albam_root"]


def test_nayin():
    c, e, p = _load()
    r = nayin.compute(p, c)
    assert r.data["sexagenary_position"] == e["nayin"]["sexagenary_position"]
    assert r.data["nayin_english"] == e["nayin"]["nayin_english"]
    assert r.data["nayin_chinese"] == e["nayin"]["nayin_chinese"]
    assert r.data["element"] == e["nayin"]["element"]


def test_iching():
    c, e, p = _load()
    r = iching.compute(p, c)
    assert r.data["hexagram_number"] == e["iching"]["hexagram_number"]


def test_wafq():
    c, e, p = _load()
    r = wafq.compute(p, c, base_number=48)
    assert r.data["row_sum"] == e["wafq"]["row_sum"]
    assert r.data["center"] == e["wafq"]["center"]


def test_essence():
    c, e, p = _load()
    r = essence.compute(p, c, age=29)
    assert r.data["reduced"] == e["essence"]["reduced"]


def test_firdaria():
    c, e, p = _load()
    r = firdaria.compute(p, c)
    assert r.data["major_planet"] == e["firdaria"]["major_planet"]
    assert r.data["sub_planet"] == e["firdaria"]["sub_planet"]
    assert r.data["birth_type"] == e["firdaria"]["birth_type"]


# ── BATCH 1: Pure Math Expansion ──

def test_pinnacles():
    c, e, p = _load()
    r = pinnacles.compute(p, c)
    assert r.data["pinnacle_1"]["value"] == e["pinnacles"]["p1"]
    assert r.data["pinnacle_2"]["value"] == e["pinnacles"]["p2"]
    assert r.data["pinnacle_3"]["value"] == e["pinnacles"]["p3"]
    assert r.data["pinnacle_4"]["value"] == e["pinnacles"]["p4"]
    assert r.data["current_pinnacle"] == e["pinnacles"]["current"]


def test_personal_year():
    c, e, p = _load()
    r = personal_year.compute(p, c)
    assert r.data["personal_year"] == e["personal_year"]["personal_year"]
    assert r.data["personal_month"] == e["personal_year"]["personal_month"]


def test_karmic_debt():
    c, e, p = _load()
    r = karmic_debt.compute(p, c)
    assert r.data["has_karmic_debt"] == e["karmic_debt"]["has_karmic_debt"]
    assert r.data["count"] == e["karmic_debt"]["count"]


def test_lo_shu_grid():
    c, e, p = _load()
    r = lo_shu_grid.compute(p, c)
    assert r.data["present"] == e["lo_shu_grid"]["present"]
    assert r.data["missing"] == e["lo_shu_grid"]["missing"]
    assert r.data["concentrated"].get(9, 0) == e["lo_shu_grid"]["concentrated_9"]


def test_hidden_passion():
    c, e, p = _load()
    r = hidden_passion.compute(p, c)
    assert r.data["hidden_passion"] == e["hidden_passion"]["hidden_passion"]
    assert r.data["frequency"] == e["hidden_passion"]["frequency"]


def test_subconscious_self():
    c, e, p = _load()
    r = subconscious_self.compute(p, c)
    assert r.data["score"] == e["subconscious_self"]["score"]
    assert r.data["digits_missing"] == e["subconscious_self"]["missing"]


def test_maturity():
    c, e, p = _load()
    r = maturity.compute(p, c)
    assert r.data["maturity_number"] == e["maturity"]["maturity_number"]
    assert r.data["raw_sum"] == e["maturity"]["raw_sum"]


# ── BATCH 2: Arabic Expansion ──

def test_abjad_kabir():
    c, e, p = _load()
    r = abjad_kabir.compute(p, c)
    assert r.data["total"] == e["abjad_kabir"]["total"]
    assert r.data["root"] == e["abjad_kabir"]["root"]
    assert r.data["word_sums"]["مهاب"] == e["abjad_kabir"]["word_sum_muhab"]


def test_abjad_saghir():
    c, e, p = _load()
    r = abjad_saghir.compute(p, c)
    assert r.data["total"] == e["abjad_saghir"]["total"]
    assert r.data["root"] == e["abjad_saghir"]["root"]


def test_abjad_wusta():
    c, e, p = _load()
    r = abjad_wusta.compute(p, c)
    assert r.data["total"] == e["abjad_wusta"]["total"]
    assert r.data["root"] == e["abjad_wusta"]["root"]


def test_abjad_maghribi():
    c, e, p = _load()
    r = abjad_maghribi.compute(p, c)
    assert r.data["total"] == e["abjad_maghribi"]["total"]
    assert r.data["root"] == e["abjad_maghribi"]["root"]
    assert r.data["word_sums"]["مهاب"] == e["abjad_maghribi"]["word_sum_muhab"]
    assert r.certainty == "COMPUTED_STRICT"


def test_hijri():
    c, e, p = _load()
    r = hijri.compute(p, c)
    assert r.data["birth_year"] == e["hijri"]["birth_year"]
    assert r.data["birth_month"] == e["hijri"]["birth_month"]
    assert r.data["birth_day"] == e["hijri"]["birth_day"]


def test_solar_lunar():
    c, e, p = _load()
    r = solar_lunar.compute(p, c)
    assert r.data["solar_count"] == e["solar_lunar"]["solar_count"]
    assert r.data["lunar_count"] == e["solar_lunar"]["lunar_count"]
    assert r.data["dominant"] == e["solar_lunar"]["dominant"]


def test_elemental_letters():
    c, e, p = _load()
    r = elemental_letters.compute(p, c)
    assert r.data["dominant_element"] == e["elemental_letters"]["dominant_element"]
    assert r.data["counts"]["fire"] == e["elemental_letters"]["fire_count"]
    assert r.data["counts"]["earth"] == e["elemental_letters"]["earth_count"]


def test_luminous_dark():
    c, e, p = _load()
    r = luminous_dark.compute(p, c)
    assert r.data["luminous_count"] == e["luminous_dark"]["luminous_count"]
    assert r.data["dark_count"] == e["luminous_dark"]["dark_count"]
    assert r.data["dominant"] == e["luminous_dark"]["dominant"]


def test_compound():
    c, e, p = _load()
    r = compound.compute(p, c)
    assert r.data["life_path"]["compound"] == e["compound"]["life_path_compound"]
    assert r.data["life_path"]["name"] == e["compound"]["life_path_name"]
    assert r.data["birthday"]["compound"] == e["compound"]["birthday_compound"]
    assert r.data["birthday"]["name"] == e["compound"]["birthday_name"]
    assert r.data["abjad_first_name"]["name"] == e["compound"]["abjad_first_name"]


def test_decan():
    c, e, p = _load()
    from modules import decan
    r = decan.compute(p, c)
    assert r.data["sign"] == e["decan"]["sign"]
    assert r.data["decan"] == e["decan"]["decan"]
    assert r.data["decan_ruler"] == e["decan"]["decan_ruler"]


def test_day_ruler():
    c, e, p = _load()
    from modules import day_ruler
    r = day_ruler.compute(p, c)
    assert r.data["birth_weekday"] == e["day_ruler"]["birth_weekday"]
    assert r.data["planetary_ruler"] == e["day_ruler"]["planetary_ruler"]


def test_tarot_birth():
    c, e, p = _load()
    from modules import tarot_birth
    r = tarot_birth.compute(p, c)
    assert r.data["raw_sum"] == e["tarot_birth"]["raw_sum"]
    assert r.data["primary_card_number"] == e["tarot_birth"]["primary_card_number"]
    assert r.data["primary_card_name"] == e["tarot_birth"]["primary_card_name"]
    assert r.data["secondary_card_number"] == e["tarot_birth"]["secondary_card_number"]


def test_dwad():
    c, e, p = _load()
    from modules import dwad
    r = dwad.compute(p, c)
    assert r.data["sun_sign"] == e["dwad"]["sun_sign"]
    assert r.data["dwad_sign"] == e["dwad"]["dwad_sign"]
    assert r.data["dwad_number"] == e["dwad"]["dwad_number"]


def test_hebrew_gematria():
    c, e, p = _load()
    r = hebrew_gematria.compute(p, c)
    assert r.data["total_gematria"] == e["hebrew_gematria"]["total_gematria"]
    assert r.data["gematria_root"] == e["hebrew_gematria"]["gematria_root"]
    assert r.data["letter_count"] == e["hebrew_gematria"]["letter_count"]


def test_mandaean_gematria():
    c, e, p = _load()
    r = mandaean_gematria.compute(p, c)
    assert r.data["total_gematria"] == e["mandaean_gematria"]["total_gematria"]
    assert r.data["gematria_root"] == e["mandaean_gematria"]["gematria_root"]
    assert r.data["letter_count"] == e["mandaean_gematria"]["letter_count"]


def test_malwasha():
    c, e, p = _load()
    r = malwasha.compute(p, c)
    assert r.certainty == "LOOKUP_FIXED"
    assert r.data["birth_sign"] == e["malwasha"]["birth_sign"]
    assert r.data["birth_sign_mandaean"] == e["malwasha"]["birth_sign_mandaean"]
    assert r.data["birth_sign_value"] == e["malwasha"]["birth_sign_value"]
    assert r.data["birth_hour"] == e["malwasha"]["birth_hour"]
    assert r.data["result_sign"] == e["malwasha"]["result_sign"]
    assert r.data["result_value"] == e["malwasha"]["result_value"]
    assert r.data["mother_value"] == e["malwasha"]["mother_value"]
    assert r.data["final_value"] == e["malwasha"]["final_value"]
    assert r.data["protective_name"] == e["malwasha"]["protective_name"]
    assert r.data["full_title"] == e["malwasha"]["full_title"]
    assert r.data["matrilineal_axis"] == True


def test_avgad():
    c, e, p = _load()
    r = avgad.compute(p, c)
    assert r.data["original_sum"] == e["avgad"]["original_sum"]
    assert r.data["avgad_sum"] == e["avgad"]["avgad_sum"]
    assert r.data["avgad_root"] == e["avgad"]["avgad_root"]
    assert r.data["delta"] == e["avgad"]["delta"]


def test_tree_of_life():
    c, e, p = _load()
    r = tree_of_life.compute(p, c)
    assert r.data["primary_sephirah"] == e["tree_of_life"]["primary_sephirah"]
    assert r.data["secondary_sephirah"] == e["tree_of_life"]["secondary_sephirah"]
    assert r.data["primary_world"] == e["tree_of_life"]["primary_world"]


def test_hebrew_calendar():
    c, e, p = _load()
    r = hebrew_calendar.compute(p, c)
    assert r.data["hebrew_day"] == e["hebrew_calendar"]["hebrew_day"]
    assert r.data["hebrew_month"] == e["hebrew_calendar"]["hebrew_month"]
    assert r.data["hebrew_year"] == e["hebrew_calendar"]["hebrew_year"]
    assert r.data["holiday"] == e["hebrew_calendar"]["holiday"]


def test_chinese_zodiac():
    c, e, p = _load()
    r = chinese_zodiac.compute(p, c)
    assert r.data["animal"] == e["chinese_zodiac"]["animal"]
    assert r.data["heavenly_stem"] == e["chinese_zodiac"]["heavenly_stem"]
    assert r.data["stem_element"] == e["chinese_zodiac"]["stem_element"]
    assert r.data["sexagenary_position"] == e["chinese_zodiac"]["sexagenary_position"]


def test_nine_star_ki():
    c, e, p = _load()
    r = nine_star_ki.compute(p, c)
    assert r.data["year_star"] == e["nine_star_ki"]["year_star"]
    assert r.data["month_star"] == e["nine_star_ki"]["month_star"]
    assert r.data["ki_string"] == e["nine_star_ki"]["ki_string"]


def test_flying_star():
    c, e, p = _load()
    r = flying_star.compute(p, c)
    assert r.data["birth_year_star"] == e["flying_star"]["birth_year_star"]
    assert r.data["current_year_star"] == e["flying_star"]["current_year_star"]


def test_bazi_pillars():
    c, e, p = _load()
    jdn = int(julian.compute(p, c).data["jdn"])
    r = bazi_pillars.compute(p, c, jdn=jdn)
    assert r.data["year_pillar"]["pillar"] == e["bazi_pillars"]["year_pillar"]
    assert r.data["month_pillar"]["pillar"] == e["bazi_pillars"]["month_pillar"]
    assert r.data["day_pillar"]["pillar"] == e["bazi_pillars"]["day_pillar"]
    assert r.data["day_master"] == e["bazi_pillars"]["day_master"]
    assert r.data["hour_pillar"]["pillar"] == e["bazi_pillars"]["hour_pillar"]


def test_bazi_daymaster():
    c, e, p = _load()
    jdn = int(julian.compute(p, c).data["jdn"])
    bazi_data = bazi_pillars.compute(p, c, jdn=jdn).data
    r = bazi_daymaster.compute(p, c, bazi_data=bazi_data)
    assert r.data["day_master_element"] == e["bazi_daymaster"]["day_master_element"]
    assert r.data["seasonal_strength"] == e["bazi_daymaster"]["seasonal_strength"]
    assert r.data["classification"] == e["bazi_daymaster"]["classification"]
    assert r.data["support_count"] == e["bazi_daymaster"]["support_count"]
    assert r.data["drain_count"] == e["bazi_daymaster"]["drain_count"]
    assert r.certainty == "COMPUTED_STRICT"


def test_bazi_luck_pillars():
    c, e, p = _load()
    jdn = int(julian.compute(p, c).data["jdn"])
    bazi_data = bazi_pillars.compute(p, c, jdn=jdn).data
    r = bazi_luck_pillars.compute(p, c, bazi_data=bazi_data)
    assert r.data["direction"] == e["bazi_luck_pillars"]["direction"]
    assert r.data["onset_age"] == e["bazi_luck_pillars"]["onset_age"]
    assert r.data["current_luck_pillar"] == e["bazi_luck_pillars"]["current_luck_pillar"]
    assert r.data["pillars"][0]["pillar"] == e["bazi_luck_pillars"]["first_pillar"]
    assert r.certainty == "COMPUTED_STRICT"


# ── P0 Gap Analysis: 12 previously untested modules ──

def test_bazi_growth():
    c, e, p = _load()
    r = bazi_growth.compute(p, c)
    assert r.data["day_master"] == e["bazi_growth"]["day_master"]
    assert r.data["year_phase"] == e["bazi_growth"]["year_phase"]
    assert r.data["month_phase"] == e["bazi_growth"]["month_phase"]
    assert r.data["day_phase"] == e["bazi_growth"]["day_phase"]


def test_cardology():
    c, e, p = _load()
    r = cardology.compute(p, c)
    assert r.data["birth_card"] == e["cardology"]["birth_card"]
    assert r.data["solar_value"] == e["cardology"]["solar_value"]
    assert r.data["rank"] == e["cardology"]["rank"]
    assert r.data["suit"] == e["cardology"]["suit"]
    assert r.certainty == "COMPUTED_STRICT"


def test_chaldean():
    c, e, p = _load()
    r = chaldean.compute(p, c)
    assert r.data["chaldean_total"] == e["chaldean"]["chaldean_total"]
    assert r.data["chaldean_root"] == e["chaldean"]["chaldean_root"]
    assert r.data["pythagorean_total"] == e["chaldean"]["pythagorean_total"]
    assert r.data["pythagorean_root"] == e["chaldean"]["pythagorean_root"]
    assert r.data["agrees_with_pythagorean"] == e["chaldean"]["agrees_with_pythagorean"]
    assert r.data["letter_count"] == e["chaldean"]["letter_count"]
    assert r.certainty == "COMPUTED_STRICT"


def test_ifa():
    c, e, p = _load()
    r = ifa.compute(p, c)
    assert r.data["combined_odu"] == e["ifa"]["combined_odu"]
    assert r.data["odu_index"] == e["ifa"]["odu_index"]
    assert r.data["is_meji"] == e["ifa"]["is_meji"]
    assert r.data["right_leg"]["name"] == e["ifa"]["right_leg_name"]
    assert r.data["left_leg"]["name"] == e["ifa"]["left_leg_name"]
    assert r.certainty == "COMPUTED_STRICT"


def test_manazil():
    c, e, p = _load()
    r = manazil.compute(p, c)
    assert r.data["manzil_number"] == e["manazil"]["manzil_number"]
    assert r.data["name_transliterated"] == e["manazil"]["name_transliterated"]
    assert r.data["name_english"] == e["manazil"]["name_english"]
    assert r.data["element"] == e["manazil"]["element"]


def test_mayan():
    c, e, p = _load()
    jdn = julian.compute(p, c).data["jdn"]
    r = mayan.compute(p, c, jdn)
    assert r.data["total_kin"] == e["mayan"]["total_kin"]
    assert r.data["glord"] == e["mayan"]["glord"]
    assert r.data["tzolkin"] == e["mayan"]["tzolkin"]
    assert r.data["tzolkin_number"] == e["mayan"]["tzolkin_number"]
    assert r.data["tzolkin_sign"] == e["mayan"]["tzolkin_sign"]
    assert r.data["haab_day"] == e["mayan"]["haab_day"]
    assert r.data["haab_month"] == e["mayan"]["haab_month"]
    assert r.certainty == "COMPUTED_STRICT"


def test_nakshatra():
    c, e, p = _load()
    r = nakshatra.compute(p, c)
    assert r.data["nakshatra_number"] == e["nakshatra"]["nakshatra_number"]
    assert r.data["nakshatra_name"] == e["nakshatra"]["nakshatra_name"]
    assert r.data["ruler"] == e["nakshatra"]["ruler"]
    assert r.data["pada"] == e["nakshatra"]["pada"]


def test_sabian():
    c, e, p = _load()
    r = sabian.compute(p, c)
    assert r.data["solar_sign"] == e["sabian"]["solar_sign"]
    assert r.data["solar_degree"] == e["sabian"]["solar_degree"]
    assert r.data["sabian_key"] == e["sabian"]["sabian_key"]
    assert r.certainty == "LOOKUP_FIXED"


def test_temperament():
    c, e, p = _load()
    r = temperament.compute(p, c, "Water", "Fire")
    assert r.data["primary_element"] == e["temperament"]["primary_element"]
    assert r.data["primary_temperament"] == e["temperament"]["primary_temperament"]
    assert r.data["blend"] == e["temperament"]["blend"]
    assert r.certainty == "LOOKUP_FIXED"


def test_vedic_tithi():
    c, e, p = _load()
    r = vedic_tithi.compute(p, c)
    assert r.data["tithi_number"] == e["vedic_tithi"]["tithi_number"]
    assert r.data["tithi_name"] == e["vedic_tithi"]["tithi_name"]
    assert r.data["phase"] == e["vedic_tithi"]["phase"]
    assert r.data["group"] == e["vedic_tithi"]["group"]


def test_vedic_yoga():
    c, e, p = _load()
    r = vedic_yoga.compute(p, c)
    assert r.data["yoga_name"] == e["vedic_yoga"]["yoga_name"]
    assert r.data["yoga_number"] == e["vedic_yoga"]["yoga_number"]
    assert r.data["quality"] == e["vedic_yoga"]["quality"]


def test_vimshottari():
    c, e, p = _load()
    r = vimshottari.compute(p, c)
    assert r.data["birth_nakshatra"] == e["vimshottari"]["birth_nakshatra"]
    assert r.data["birth_nakshatra_ruler"] == e["vimshottari"]["birth_nakshatra_ruler"]
    assert r.data["first_dasha_remaining_years"] == e["vimshottari"]["first_dasha_remaining_years"]
    assert r.data["current_maha_dasha"] == e["vimshottari"]["current_maha_dasha"]
    assert r.data["current_dasha_start_age"] == e["vimshottari"]["current_dasha_start_age"]
    assert r.data["current_dasha_end_age"] == e["vimshottari"]["current_dasha_end_age"]
    assert r.certainty == "COMPUTED_STRICT"


# ── Ephemeris Phase 1: Foundation ──

def test_natal_chart():
    c, e, p = _load()
    r = natal_chart.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["sun_sign"] == e["natal_chart"]["sun_sign"]
    assert r.data["moon_sign"] == e["natal_chart"]["moon_sign"]
    assert r.data["rising_sign"] == e["natal_chart"]["rising_sign"]
    assert r.data["planets"]["Sun"]["longitude"] == e["natal_chart"]["sun_longitude"]
    assert r.data["planets"]["Moon"]["longitude"] == e["natal_chart"]["moon_longitude"]
    assert r.data["ascendant"]["longitude"] == e["natal_chart"]["ascendant_longitude"]
    assert r.data["planets"]["Sun"]["degree"] == e["natal_chart"]["sun_degree"]
    assert r.data["planets"]["Sun"]["minute"] == e["natal_chart"]["sun_minute"]
    assert len(r.data["planets"]) == e["natal_chart"]["planet_count"]


def test_house_system():
    c, e, p = _load()
    natal_data = natal_chart.compute(p, c).data
    r = house_system.compute(p, c, natal_chart_data=natal_data)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["system"] == e["house_system"]["system"]
    assert r.data["ascending_sign"] == e["house_system"]["ascending_sign"]
    assert r.data["planet_houses"]["Sun"]["house"] == e["house_system"]["sun_house"]
    assert r.data["planet_houses"]["Moon"]["house"] == e["house_system"]["moon_house"]
    assert r.data["mc_house"] == e["house_system"]["mc_house"]


def test_aspects():
    c, e, p = _load()
    natal_data = natal_chart.compute(p, c).data
    r = aspects.compute(p, c, natal_chart_data=natal_data)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["aspect_count"] == e["aspects"]["aspect_count"]
    assert r.data["aspects"][0]["aspect"] == e["aspects"]["tightest_aspect"]
    assert r.data["aspects"][0]["planet_1"] == e["aspects"]["tightest_pair"][0]
    assert r.data["aspects"][0]["planet_2"] == e["aspects"]["tightest_pair"][1]
    assert r.data["aspects"][0]["orb"] == e["aspects"]["tightest_orb"]
    assert r.data["summary"]["conjunction"] == e["aspects"]["conjunction_count"]
    assert r.data["summary"]["opposition"] == e["aspects"]["opposition_count"]
    assert r.data["summary"]["trine"] == e["aspects"]["trine_count"]
    assert r.data["summary"]["square"] == e["aspects"]["square_count"]
    assert r.data["summary"]["sextile"] == e["aspects"]["sextile_count"]


# ── Ephemeris Phase 2: High-value systems ──

def test_essential_dignities():
    c, e, p = _load()
    natal_data = natal_chart.compute(p, c).data
    r = essential_dignities.compute(p, c, natal_chart_data=natal_data)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["is_diurnal"] == e["essential_dignities"]["is_diurnal"]
    assert r.data["total_score"] == e["essential_dignities"]["total_score"]
    assert r.data["dignified_count"] == e["essential_dignities"]["dignified_count"]
    assert r.data["debilitated_count"] == e["essential_dignities"]["debilitated_count"]
    assert r.data["dignities"]["Mercury"]["conditions"] == e["essential_dignities"]["mercury_conditions"]
    assert r.data["dignities"]["Mercury"]["score"] == e["essential_dignities"]["mercury_score"]
    assert r.data["dignities"]["Sun"]["conditions"] == e["essential_dignities"]["sun_conditions"]
    assert r.data["dignities"]["Sun"]["score"] == e["essential_dignities"]["sun_score"]
    assert r.data["dignities"]["Jupiter"]["score"] == e["essential_dignities"]["jupiter_score"]
    assert r.data["dignities"]["Saturn"]["score"] == e["essential_dignities"]["saturn_score"]


def test_sect():
    c, e, p = _load()
    natal_data = natal_chart.compute(p, c).data
    r = sect.compute(p, c, natal_chart_data=natal_data)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["chart_sect"] == e["sect"]["chart_sect"]
    assert r.data["is_diurnal"] == e["sect"]["is_diurnal"]
    assert r.data["mercury_sect"] == e["sect"]["mercury_sect"]
    assert r.data["benefic_of_sect"] == e["sect"]["benefic_of_sect"]
    assert r.data["malefic_contrary"] == e["sect"]["malefic_contrary"]
    assert r.data["in_sect_count"] == e["sect"]["in_sect_count"]
    assert r.data["out_sect_count"] == e["sect"]["out_sect_count"]


def test_arabic_parts():
    c, e, p = _load()
    natal_data = natal_chart.compute(p, c).data
    r = arabic_parts.compute(p, c, natal_chart_data=natal_data)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["lots"]["Fortune"]["sign"] == e["arabic_parts"]["fortune_sign"]
    assert r.data["fortune_house"] == e["arabic_parts"]["fortune_house"]
    assert r.data["lots"]["Spirit"]["sign"] == e["arabic_parts"]["spirit_sign"]
    assert r.data["spirit_house"] == e["arabic_parts"]["spirit_house"]
    assert r.data["lot_count"] == e["arabic_parts"]["lot_count"]


def test_solar_return():
    c, e, p = _load()
    natal_data = natal_chart.compute(p, c).data
    r = solar_return.compute(p, c, natal_chart_data=natal_data)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["return_year"] == e["solar_return"]["return_year"]
    assert r.data["return_date"] == e["solar_return"]["return_date"]
    assert r.data["return_time_local"] == e["solar_return"]["return_time_local"]
    assert r.data["return_rising"] == e["solar_return"]["return_rising"]
    assert r.data["return_moon_sign"] == e["solar_return"]["return_moon_sign"]
    assert r.data["sun_house"] == e["solar_return"]["sun_house"]


def test_progressions():
    c, e, p = _load()
    natal_data = natal_chart.compute(p, c).data
    r = progressions.compute(p, c, natal_chart_data=natal_data)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["age"] == e["progressions"]["age"]
    assert r.data["progressed_sun_sign"] == e["progressions"]["progressed_sun_sign"]
    assert r.data["progressed_moon_sign"] == e["progressions"]["progressed_moon_sign"]
    assert r.data["moon_sign_changed"] == e["progressions"]["moon_sign_changed"]
    assert r.data["sun_advance_degrees"] == e["progressions"]["sun_advance_degrees"]


def test_fixed_stars():
    c, e, p = _load()
    natal_data = natal_chart.compute(p, c).data
    r = fixed_stars.compute(p, c, natal_chart_data=natal_data)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["conjunction_count"] == e["fixed_stars"]["conjunction_count"]
    assert r.data["royal_conjunction_count"] == e["fixed_stars"]["royal_conjunction_count"]
    assert r.data["orb_used"] == e["fixed_stars"]["orb_used"]
    assert len(r.data["stars"]) == e["fixed_stars"]["star_count"]


def test_synthesis_convergence_claim():
    """AUDIT-GRADE: Pin the exact convergence claim against meta-fixture.
    
    This is the 'test the tester' — ensures synthesis.py produces the same
    dominant_root, module_votes, and group_count that are published in reports
    and compared against the Monte Carlo baseline. Any regression in vote
    logic, whitelist, or group assignment breaks this test.
    
    Meta-fixture: fixtures/synthesis_meta_fixture.json
    Frozen baseline: fixtures/baseline_v3_20260227_n10000.json
    """
    import subprocess
    meta = json.loads(
        (Path(__file__).parent.parent / "fixtures" / "synthesis_meta_fixture.json").read_text()
    )
    
    # Run the full engine via runner.py and load synthesis output
    # (runner.py writes output.json; we read synthesis from there)
    base = Path(__file__).parent.parent
    result = subprocess.run(
        [sys.executable, "runner.py", "fixtures/muhab_profile.json"],
        cwd=str(base),
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"runner.py failed: {result.stderr}"
    
    output = json.loads((base / "output.json").read_text())
    s = output["synthesis"]
    nc = s["number_convergences"]
    
    # Find dominant convergence (highest system_count)
    top = max(nc, key=lambda x: x["system_count"])
    
    # Pin the three numbers that constitute the published claim
    assert top["number"] == meta["dominant_root"], (
        f"Dominant root changed: {top['number']} != {meta['dominant_root']}"
    )
    assert top["system_count"] == meta["module_votes"], (
        f"Module vote count changed: {top['system_count']} != {meta['module_votes']}. "
        f"Check for double-counting (avgad?), new modules in whitelist, or group reassignment."
    )
    assert top["group_count"] == meta["group_count"], (
        f"Group count changed: {top['group_count']} != {meta['group_count']}. "
        f"Check SYSTEM_TO_GROUP assignments."
    )
    
    # Pin the tier — significant finding should stay significant
    assert top["tier"] == meta["tier"], (
        f"Tier changed: {top['tier']} != {meta['tier']}"
    )
    
    # Pin total system count — no modules silently added/removed
    assert s["confidence_summary"]["total_systems"] == meta["total_systems"], (
        f"Total system count changed: {s['confidence_summary']['total_systems']} != {meta['total_systems']}"
    )
    
    # Pin lockable % — no modules silently downgraded to APPROX
    assert s["confidence_summary"]["lockable_pct"] == meta["lockable_pct"], (
        f"Lockable % changed: {s['confidence_summary']['lockable_pct']} != {meta['lockable_pct']}"
    )


def test_synthesis_runs():
    """Synthesis engine should run without errors and produce expected structure."""
    c, e, p = _load()
    jdn = julian.compute(p, c).data["jdn"]
    results = [
        julian.compute(p, c),
        biorhythm.compute(p, c),
        geomancy.compute(p, c, jdn),
        challenges.compute(p, c),
        attitude.compute(p, c),
        profection.compute(p, c),
        bridges.compute(p, c),
        nayin.compute(p, c),
        iching.compute(p, c),
    ]
    synth = synthesis.synthesize(results, c)
    assert "confidence_summary" in synth
    assert synth["confidence_summary"]["total_systems"] == len(results)
    assert "number_convergences" in synth
    assert "element_convergences" in synth


def test_all_modules_return_system_result():
    """Every module must return a SystemResult with required fields."""
    c, e, p = _load()
    jdn = julian.compute(p, c).data["jdn"]

    all_results = [
        julian.compute(p, c),
        biorhythm.compute(p, c),
        mayan.compute(p, c, jdn),
        geomancy.compute(p, c, jdn),
        iching.compute(p, c),
        wafq.compute(p, c, 48),
        essence.compute(p, c, 29),
        cardology.compute(p, c),
        nayin.compute(p, c),
        compound.compute(p, c),
        sabian.compute(p, c),
        challenges.compute(p, c),
        bridges.compute(p, c),
        attitude.compute(p, c),
        profection.compute(p, c),
        firdaria.compute(p, c),
        notarikon.compute(p, c),
        atbash.compute(p, c),
        albam.compute(p, c),
        temperament.compute(p, c, "Water", "Fire"),
        bazi_growth.compute(p, c),
        vedic_tithi.compute(p, c),
        vedic_yoga.compute(p, c),
        pinnacles.compute(p, c),
        personal_year.compute(p, c),
        karmic_debt.compute(p, c),
        lo_shu_grid.compute(p, c),
        hidden_passion.compute(p, c),
        subconscious_self.compute(p, c),
        maturity.compute(p, c),
        abjad_kabir.compute(p, c),
        abjad_saghir.compute(p, c),
        abjad_wusta.compute(p, c),
        abjad_maghribi.compute(p, c),
        hijri.compute(p, c),
        solar_lunar.compute(p, c),
        elemental_letters.compute(p, c),
        luminous_dark.compute(p, c),
        decan.compute(p, c),
        day_ruler.compute(p, c),
        tarot_birth.compute(p, c),
        dwad.compute(p, c),
        hebrew_gematria.compute(p, c),
        mandaean_gematria.compute(p, c),
        avgad.compute(p, c),
        tree_of_life.compute(p, c),
        hebrew_calendar.compute(p, c),
        chinese_zodiac.compute(p, c),
        nine_star_ki.compute(p, c),
        flying_star.compute(p, c),
        bazi_pillars.compute(p, c, jdn=jdn),
        bazi_daymaster.compute(p, c, bazi_data=bazi_pillars.compute(p, c, jdn=jdn).data),
        bazi_luck_pillars.compute(p, c, bazi_data=bazi_pillars.compute(p, c, jdn=jdn).data),
    ]

    assert len(all_results) == 53
    for r in all_results:
        assert r.id, f"Missing id in {r}"
        assert r.certainty, f"Missing certainty in {r}"
        assert r.data is not None, f"Missing data in {r}"
        assert r.constants_version == c["version"], f"Version mismatch in {r.id}"


def test_egyptian_decan():
    c, e, p = _load()
    r = egyptian_decan.compute(p, c)
    assert r.data["ptolemaic_decan"] == e["egyptian_decan"]["ptolemaic_decan"]
    assert r.data["decan_sign"] == e["egyptian_decan"]["decan_sign"]
    assert r.data["planetary_ruler"] == e["egyptian_decan"]["planetary_ruler"]
    assert r.data["deity"] == e["egyptian_decan"]["deity"]
    assert r.certainty == "COMPUTED_STRICT"


def test_weton():
    from modules import weton
    c, e, p = _load()
    r = weton.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["weton"] == e["weton"]["weton"]
    assert r.data["pasar"] == e["weton"]["pasar"]
    assert r.data["saptawara"] == e["weton"]["saptawara"]
    assert r.data["total_neptu"] == e["weton"]["total_neptu"]
    assert r.data["weton_cycle_position"] == e["weton"]["weton_cycle_position"]
    assert r.data["day_ruler"] == e["weton"]["day_ruler"]


def test_planetary_joy():
    from modules import planetary_joy
    c, e, p = _load()
    r = planetary_joy.compute(p, c)
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["in_joy"] == e["planetary_joy"]["in_joy"]
    assert r.data["near_joy"] == e["planetary_joy"]["near_joy"]
    assert r.data["joy_count"] == e["planetary_joy"]["joy_count"]
    assert r.data["headline"] == e["planetary_joy"]["headline"]


def test_prashna_natal():
    from modules import prashna_natal
    import re
    c, e, p = _load()
    # prashna_natal: today-dependent — test structure + invariants, not exact values
    r = prashna_natal.compute(p, c, natal_chart_data=None)
    # Certainty: APPROX (solar noon fallback) or COMPUTED_STRICT (explicit question_time)
    assert r.certainty in ("APPROX", "COMPUTED_STRICT"), f"Unexpected certainty: {r.certainty}"
    # Required structural fields present
    for field in ("prashna_lagna", "prashna_lagna_lord", "prashna_moon_sign",
                  "prashna_moon_nakshatra", "tara_name", "tara_quality", "ishta_graha"):
        assert field in r.data, f"Missing field: {field}"
    # Lagna must be a valid zodiac sign
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    assert r.data["prashna_lagna"] in SIGNS, f"Invalid lagna: {r.data['prashna_lagna']}"
    assert r.data["prashna_moon_sign"] in SIGNS, f"Invalid moon sign: {r.data['prashna_moon_sign']}"
    # Tara quality must be one of the defined values
    assert r.data["tara_quality"] in ("Favorable", "Unfavorable", "Neutral")
    # Moon longitude in valid sidereal range
    assert 0.0 <= r.data["prashna_moon_deg"] < 360.0
    # Interpretation present and substantive
    assert r.interpretation is not None and len(r.interpretation) > 40
    # Natal Moon nakshatra should resolve (birth_time_local + location both in profile)
    assert r.data["natal_moon_nakshatra"] is not None, "Natal Moon nakshatra should resolve from birth data"


def test_rectification():
    from modules import rectification
    c, e, p = _load()
    r = rectification.compute(p, c)
    ex = e["rectification"]
    assert r.certainty == ex["certainty"]
    assert r.data["base_time"] == ex["base_time"]
    assert r.data["base_ascendant_sign"] == ex["base_ascendant_sign"]
    assert r.data["base_ascendant_degree"] == ex["base_ascendant_degree"]
    assert r.data["base_mc_sign"] == ex["base_mc_sign"]
    assert r.data["base_moon_sign"] == ex["base_moon_sign"]
    assert r.data["base_sun_house"] == ex["base_sun_house"]
    assert r.data["ascendant_sign_stable"] == ex["ascendant_sign_stable"]
    assert r.data["mc_sign_stable"] == ex["mc_sign_stable"]
    assert r.data["moon_sign_stable"] == ex["moon_sign_stable"]
    assert r.data["time_sensitivity"] == ex["time_sensitivity"]
    # Variants must exist
    assert "variants" in r.data
    for v in ("minus_30", "minus_15", "plus_15", "plus_30"):
        assert v in r.data["variants"]
        assert "ascendant_sign" in r.data["variants"][v]
    # Confidence note present
    assert r.data["confidence_note"] and len(r.data["confidence_note"]) > 20


def test_prashna_natal_upgraded():
    from modules import prashna_natal
    c, e, p = _load()
    r = prashna_natal.compute(p, c, natal_chart_data=None)
    # Must be APPROX in birth_fallback mode (noon fallback, today != dob)
    assert r.certainty == "APPROX", f"Unexpected certainty: {r.certainty}"
    # Horary mode present
    assert r.data["horary_mode"] == "birth_fallback"
    # Radicality fields present
    assert r.data["radicality"] in ("RADICAL", "NON_RADICAL", "QUESTIONABLE")
    assert isinstance(r.data["radicality_notes"], list)
    # Horary significators present
    assert "planetary_hour_ruler" in r.data
    assert "moon_void_of_course" in r.data
    assert "via_combusta" in r.data
    assert "querent_significator" in r.data
    assert isinstance(r.data["moon_void_of_course"], bool)
    assert isinstance(r.data["via_combusta"], bool)
    # Moon aspects (may be None if no aspect found, but key must exist)
    assert "moon_last_aspect" in r.data
    assert "moon_next_aspect" in r.data
    # Standard prashna fields still present
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    assert r.data["prashna_lagna"] in SIGNS
    assert r.data["prashna_moon_sign"] in SIGNS
    assert "tara_name" in r.data
    assert "ishta_graha" in r.data
    # Interpretation present
    assert r.interpretation and len(r.interpretation) > 40


def test_horary_timing():
    from modules import horary_timing
    c, e, p = _load()
    r = horary_timing.compute(p, c)
    ex = e["horary_timing"]
    assert r.certainty == ex["certainty"]
    assert r.data["day_of_week"] == ex["day_of_week"]
    assert r.data["day_ruler"] == ex["day_ruler"]
    assert r.data["current_hour_number"] == ex["current_hour_number"]
    assert r.data["current_hour_ruler"] == ex["current_hour_ruler"]
    # Structural checks
    assert r.data["today"] == "2026-02-13"
    assert len(r.data["chaldean_day_hour_sequence"]) == 7
    assert r.data["chaldean_day_hour_sequence"][0] == r.data["day_ruler"]
    assert r.interpretation and len(r.interpretation) > 20


def test_jaimini_karakas():
    from modules import jaimini_karakas, natal_chart
    c, e, p = _load()
    nc = natal_chart.compute(p, c)
    ncd = nc.data if nc.certainty == "COMPUTED_STRICT" else None
    r = jaimini_karakas.compute(p, c, natal_chart_data=ncd)
    ex = e["jaimini_karakas"]
    assert r.certainty == ex["certainty"]
    ak = r.data["atmakaraka"]
    assert ak["planet"] == ex["atmakaraka_planet"]
    assert ak["sign"] == ex["atmakaraka_sign"]
    assert ak["degree_in_sign"] == ex["atmakaraka_degree"]
    assert r.data["ak_sign"] == ex["ak_sign"]
    assert r.data["ak_navamsha_sign"] == ex["ak_navamsha_sign"]
    assert r.data["karakamsha"] == ex["karakamsha"]
    amk = r.data["amatyakaraka"]
    assert amk["planet"] == ex["amatyakaraka_planet"]
    # All 7 karakas present
    for k in ("atmakaraka", "amatyakaraka", "bhratrikaraka", "matrikaraka",
              "pitrikaraka", "putrakaraka", "gnatikaraka"):
        assert k in r.data, f"Missing karaka: {k}"


def test_jaimini_argala():
    from modules import jaimini_argala, natal_chart
    c, e, p = _load()
    nc = natal_chart.compute(p, c)
    ncd = nc.data if nc.certainty == "COMPUTED_STRICT" else None
    r = jaimini_argala.compute(p, c, natal_chart_data=ncd)
    ex = e["jaimini_argala"]
    assert r.certainty == ex["certainty"]
    assert r.data["lagna_sign"] == ex["lagna_sign"]
    assert r.data["net_argala"] == ex["net_argala"]
    assert r.data["strong_count"] == ex["strong_count"]
    assert r.data["blocked_count"] == ex["blocked_count"]
    # Argala keys present
    for k in ("dhana_2nd", "sukha_4th", "labha_11th", "suta_5th"):
        assert k in r.data["argala"], f"Missing argala: {k}"
        assert "strength" in r.data["argala"][k]


def test_jaimini_navamsha():
    from modules import jaimini_navamsha, jaimini_karakas, natal_chart
    c, e, p = _load()
    nc = natal_chart.compute(p, c)
    ncd = nc.data if nc.certainty == "COMPUTED_STRICT" else None
    rk = jaimini_karakas.compute(p, c, natal_chart_data=ncd)
    karakas_data = rk.data if rk.certainty == "COMPUTED_STRICT" else None
    r = jaimini_navamsha.compute(p, c, natal_chart_data=ncd, karakas_data=karakas_data)
    ex = e["jaimini_navamsha"]
    assert r.certainty == ex["certainty"]
    assert r.data["d9_ascendant"] == ex["d9_ascendant"]
    assert r.data["karakamsha"] == ex["karakamsha"]
    assert r.data["atmakaraka_navamsha"] == ex["atmakaraka_navamsha"]
    # Vargottama is a list
    assert isinstance(r.data["vargottama"], list)
    # D9 positions present for key planets
    assert "Sun" in r.data["d9_positions"]
    assert "Moon" in r.data["d9_positions"]
    assert "d9_sign" in r.data["d9_positions"]["Sun"]


def test_astrocartography():
    from modules import astrocartography, natal_chart
    c, e, p = _load()
    nc = natal_chart.compute(p, c)
    ncd = nc.data if nc.certainty == "COMPUTED_STRICT" else None
    r = astrocartography.compute(p, c, natal_chart_data=ncd)
    ex = e["astrocartography"]
    assert r.certainty == ex["certainty"]
    # Birth location
    assert r.data["birth_location"]["name"] == ex["birth_location_name"]
    # Closest lines is a non-empty list
    assert isinstance(r.data["closest_lines"], list)
    assert len(r.data["closest_lines"]) > 0
    # Closest line matches
    top = r.data["closest_lines"][0]
    assert top["planet"] == ex["closest_planet"]
    assert top["line_type"] == ex["closest_line_type"]
    assert round(top["distance_km"], 1) == ex["closest_distance_km"]
    # Saturn line present
    assert "saturn_line" in r.data
    assert r.data["saturn_line"]["MC_longitude"] == ex["saturn_MC_longitude"]
    assert r.data["saturn_line"]["IC_longitude"] == ex["saturn_IC_longitude"]
    # Jupiter line present
    assert "jupiter_line" in r.data
    assert r.data["jupiter_line"]["MC_longitude"] == ex["jupiter_MC_longitude"]
    assert r.data["jupiter_line"]["IC_longitude"] == ex["jupiter_IC_longitude"]
    # Planetary lines for all 7 planets
    for planet in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        assert planet in r.data["planetary_lines"]
        for lt in ("MC", "IC", "ASC", "DSC"):
            assert lt in r.data["planetary_lines"][planet]


def test_kp_sublords():
    from modules import kp_sublords, natal_chart
    c, e, p = _load()
    nc = natal_chart.compute(p, c)
    ncd = nc.data if nc.certainty == "COMPUTED_STRICT" else None
    r = kp_sublords.compute(p, c, natal_chart_data=ncd)
    ex = e["kp_sublords"]
    assert r.certainty == ex["certainty"]
    # Key sub-lords match
    assert r.data["ascendant_sub_lord"] == ex["ascendant_sub_lord"]
    assert r.data["moon_sub_lord"] == ex["moon_sub_lord"]
    assert r.data["mercury_sub_lord"] == ex["mercury_sub_lord"]
    assert r.data["jupiter_sub_lord"] == ex["jupiter_sub_lord"]
    assert r.data["saturn_sub_lord"] == ex["saturn_sub_lord"]
    # KP pointers match
    assert r.data["points"]["ascendant"]["kp_pointer"] == ex["ascendant_kp_pointer"]
    assert r.data["points"]["Moon"]["kp_pointer"] == ex["moon_kp_pointer"]
    # All 6 points present
    for key in ("ascendant", "Sun", "Moon", "Mercury", "Jupiter", "Saturn"):
        assert key in r.data["points"], f"Missing point: {key}"
        pt = r.data["points"][key]
        assert "star_lord" in pt
        assert "sub_lord" in pt
        assert "sub_sub_lord" in pt
        assert "kp_pointer" in pt
    # Significator analysis has 12 houses
    assert len(r.data.get("significator_analysis", {})) == 12


def test_draconic_chart():
    from modules import draconic_chart, natal_chart
    c, e, p = _load()
    nc = natal_chart.compute(p, c)
    ncd = nc.data if nc.certainty == "COMPUTED_STRICT" else None
    r = draconic_chart.compute(p, c, natal_chart_data=ncd)
    ex = e["draconic_chart"]
    assert r.certainty == ex["certainty"]
    assert r.data["draconic_sun_sign"] == ex["draconic_sun_sign"]
    assert r.data["draconic_moon_sign"] == ex["draconic_moon_sign"]
    assert r.data["draconic_asc_sign"] == ex["draconic_asc_sign"]
    assert r.data["sun_sign_shift"] == ex["sun_sign_shift"]
    assert r.data["moon_sign_shift"] == ex["moon_sign_shift"]
    # Conjunctions is a list with expected count
    assert isinstance(r.data["draconic_natal_conjunctions"], list)
    assert len(r.data["draconic_natal_conjunctions"]) == ex["conjunction_count"]
    # Draconic positions present for key planets
    for planet in ("Sun", "Moon", "Mercury", "Ascendant"):
        assert planet in r.data["draconic_positions"]
        pos = r.data["draconic_positions"][planet]
        assert "sign" in pos
        assert "formatted" in pos
    # North Node should be at 0° Aries (by definition)
    nn = r.data["draconic_positions"].get("North Node", {})
    assert nn.get("sign") == "Aries"
    assert nn.get("degree") == 0


def test_solar_return_deep():
    from modules import solar_return_deep, natal_chart
    c, e, p = _load()
    nc = natal_chart.compute(p, c)
    ncd = nc.data if nc.certainty == "COMPUTED_STRICT" else None
    r = solar_return_deep.compute(p, c, natal_chart_data=ncd)
    ex = e["solar_return_deep"]
    assert r.certainty == ex["certainty"]
    assert r.data["sr_ascendant_sign"] == ex["sr_ascendant_sign"]
    assert r.data["sr_sun_house"] == ex["sr_sun_house"]
    assert r.data["sr_moon_sign"] == ex["sr_moon_sign"]
    assert r.data["sr_moon_house"] == ex["sr_moon_house"]
    assert r.data["sr_asc_ruler"] == ex["sr_asc_ruler"]
    assert r.data["sr_asc_ruler_house"] == ex["sr_asc_ruler_house"]
    assert r.data["activation_count"] == ex["activation_count"]
    assert isinstance(r.data["primary_themes"], list)
    assert len(r.data["primary_themes"]) == ex["primary_themes_count"]
    assert r.data["year_summary"]  # non-empty string
    assert isinstance(r.data["sr_natal_activations"], list)
    assert isinstance(r.data["timing_alignments"], list)
    assert len(r.data["timing_alignments"]) > 0


def test_electional_windows():
    from modules import electional_windows, natal_chart
    c, e, p = _load()
    nc = natal_chart.compute(p, c)
    ncd = nc.data if nc.certainty == "COMPUTED_STRICT" else None
    r = electional_windows.compute(p, c, natal_chart_data=ncd)
    ex = e["electional_windows"]
    assert r.certainty == ex["certainty"]
    assert r.data["reference_date"] == ex["reference_date"]
    assert r.data["window_horizon_days"] == ex["window_horizon_days"]
    # All 5 action categories present
    aw = r.data["action_windows"]
    assert len(aw) == ex["action_categories_count"]
    for cat_key in ("communication_launch", "career_authority",
                    "creative_relationship", "financial_material",
                    "spiritual_inner_work"):
        assert cat_key in aw
        assert isinstance(aw[cat_key]["best_windows"], list)
        assert len(aw[cat_key]["best_windows"]) > 0
    # Next new/full moon
    assert r.data["next_new_moon"] is not None
    assert r.data["next_new_moon"]["sign"] == ex["next_new_moon_sign"]
    assert r.data["next_full_moon"] is not None
    assert r.data["next_full_moon"]["sign"] == ex["next_full_moon_sign"]


def test_muhurta():
    from modules import muhurta, natal_chart
    c, e, p = _load()
    nc = natal_chart.compute(p, c)
    ncd = nc.data if nc.certainty == "COMPUTED_STRICT" else None
    r = muhurta.compute(p, c, natal_chart_data=ncd)
    ex = e["muhurta"]
    assert r.certainty == ex["certainty"]
    assert r.data["date"] == ex["date"]
    assert r.data["location"] == ex["location"]
    assert r.data["day_ruler"] == ex["day_ruler"]
    assert r.data["sunrise_local"] == ex["sunrise_local"]
    assert r.data["sunset_local"] == ex["sunset_local"]
    # Key structures present
    assert "rahu_kalam" in r.data
    assert "start" in r.data["rahu_kalam"]
    assert "end" in r.data["rahu_kalam"]
    assert "abhijit_muhurta" in r.data
    assert "start" in r.data["abhijit_muhurta"]
    assert "gulika_kalam" in r.data
    assert "yamagandam" in r.data
    assert isinstance(r.data["best_muhurtas_today"], list)
    assert len(r.data["best_muhurtas_today"]) > 0
    assert "current_muhurta" in r.data
    assert "name" in r.data["current_muhurta"]


def test_synastry_needs_input():
    from modules import synastry
    c, e, p = _load()
    r = synastry.compute(p, c)
    ex = e["synastry"]
    assert r.certainty == ex["certainty"]
    assert r.data["status"] == ex["status"]



# ── Arabic Linguistic Sciences ──────────────────────────────────────────

def test_arabic_roots():
    c, e, p = _load()
    r = arabic_roots.compute(p, c)
    ex = e["arabic_roots"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["root_count"] == ex["root_count"]
    assert r.data["root_abjad_total"] == ex["root_abjad_total"]
    assert r.data["root_abjad_root"] == ex["root_abjad_root"]
    assert r.data["dominant_field"] == ex["dominant_field"]


def test_arabic_morphology():
    c, e, p = _load()
    r = arabic_morphology.compute(p, c)
    ex = e["arabic_morphology"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["dominant_voice"] == ex["dominant_voice"]
    assert r.data["active_ratio"] == ex["active_ratio"]
    assert r.data["passive_ratio"] == ex["passive_ratio"]


def test_name_semantics():
    c, e, p = _load()
    r = name_semantics.compute(p, c)
    ex = e["name_semantics"]
    assert r.certainty == "LOOKUP_FIXED"
    assert r.data["unit_count"] == ex["unit_count"]
    assert r.data["dominant_cluster"] == ex["dominant_cluster"]
    assert r.data["dominant_cluster_count"] == ex["dominant_cluster_count"]
    assert r.data["dominant_cluster_ratio"] == ex["dominant_cluster_ratio"]
    assert r.data["total_classified"] == ex["total_classified"]


def test_arabic_phonetics():
    c, e, p = _load()
    r = arabic_phonetics.compute(p, c)
    ex = e["arabic_phonetics"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["total_letters"] == ex["total_letters"]
    assert r.data["dominant_makhraj"] == ex["dominant_makhraj"]
    assert r.data["voiced_count"] == ex["voiced_count"]
    assert r.data["voiceless_count"] == ex["voiceless_count"]


def test_arabic_letter_nature():
    c, e, p = _load()
    r = arabic_letter_nature.compute(p, c)
    ex = e["arabic_letter_nature"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["total_letters"] == ex["total_letters"]
    assert r.data["dominant_element"] == ex["dominant_element"]
    assert r.data["dominant_planet"] == ex["dominant_planet"]
    assert r.data["dominant_sign"] == ex["dominant_sign"]
    assert r.data["dominant_temperament"] == ex["dominant_temperament"]
    assert r.data["luminous_ratio"] == ex["luminous_ratio"]
    assert r.data["dominant_color"] == ex["dominant_color"]


# ── Wave 1 — Structural Arabic Deepening ────────────────────────────────

def test_digit_patterns():
    c, e, p = _load()
    r = digit_patterns.compute(p, c)
    ex = e["digit_patterns"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["digit_sum"] == ex["digit_sum"]
    assert r.data["digit_sum_root"] == ex["digit_sum_root"]
    assert r.data["digit_product"] == ex["digit_product"]
    assert r.data["reverse"] == ex["reverse"]
    assert r.data["reverse_root"] == ex["reverse_root"]
    assert r.data["is_palindrome"] == ex["is_palindrome"]
    assert r.data["unique_primes"] == ex["unique_primes"]


def test_lineage_computation():
    c, e, p = _load()
    r = lineage_computation.compute(p, c)
    ex = e["lineage_computation"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["word_count"] == ex["word_count"]
    assert r.data["sequence"] == ex["sequence"]
    assert r.data["compound_groups"] == ex["compound_groups"]
    assert r.data["center_of_weight"] == ex["center_of_weight"]
    assert r.data["root_sequence"] == ex["root_sequence"]


def test_hijri_calendar_encoding():
    c, e, p = _load()
    r = hijri_calendar_encoding.compute(p, c)
    ex = e["hijri_calendar_encoding"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["hijri_year"] == ex["hijri_year"]
    assert r.data["year_digit_root"] == ex["year_digit_root"]
    assert r.data["is_sacred_month"] == ex["is_sacred_month"]
    assert r.data["full_digit_root"] == ex["full_digit_root"]
    assert r.data["combined_root"] == ex["combined_root"]


def test_calligraphy_structure():
    c, e, p = _load()
    r = calligraphy_structure.compute(p, c)
    ex = e["calligraphy_structure"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["total_letters"] == ex["total_letters"]
    assert r.data["ascenders"] == ex["ascenders"]
    assert r.data["descenders"] == ex["descenders"]
    assert r.data["dots_above"] == ex["dots_above"]
    assert r.data["dots_below"] == ex["dots_below"]
    assert r.data["dominant_feature"] == ex["dominant_feature"]


def test_divine_breath():
    c, e, p = _load()
    r = divine_breath.compute(p, c)
    ex = e["divine_breath"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["total_letters"] == ex["total_letters"]
    assert r.data["entropy"] == ex["entropy"]
    assert r.data["normalized_entropy"] == ex["normalized_entropy"]
    assert r.data["dominant_zone"] == ex["dominant_zone"]


def test_letter_position_encoding():
    c, e, p = _load()
    r = letter_position_encoding.compute(p, c)
    ex = e["letter_position_encoding"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["total_letters"] == ex["total_letters"]
    assert r.data["total_weight"] == ex["total_weight"]
    assert r.data["weight_root"] == ex["weight_root"]
    assert r.data["center_of_gravity"] == ex["center_of_gravity"]
    assert r.data["skew"] == ex["skew"]


def test_abjad_visual_architecture():
    c, e, p = _load()
    r = abjad_visual_architecture.compute(p, c)
    ex = e["abjad_visual_architecture"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["dotted_letters"] == ex["dotted_letters"]
    assert r.data["undotted_letters"] == ex["undotted_letters"]
    assert r.data["total_dots"] == ex["total_dots"]
    assert r.data["void_ratio"] == ex["void_ratio"]
    assert r.data["interruptions"] == ex["interruptions"]


def test_name_weight():
    c, e, p = _load()
    r = name_weight.compute(p, c)
    ex = e["name_weight"]
    assert r.certainty == "APPROX"
    assert r.data["total_syllables"] == ex["total_syllables"]
    assert r.data["heavy_ratio"] == ex["heavy_ratio"]
    assert r.data["cadence"] == ex["cadence"]


def test_arabic_rhetoric():
    c, e, p = _load()
    r = arabic_rhetoric.compute(p, c)
    ex = e["arabic_rhetoric"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["has_jinas_tam"] == ex["has_jinas_tam"]
    assert r.data["has_genealogical_echo"] == ex["has_genealogical_echo"]
    assert r.data["has_tibaq"] == ex["has_tibaq"]
    assert r.data["most_common_letter_count"] == ex["most_common_letter_count"]
    assert r.data["total_repetition_score"] == ex["total_repetition_score"]


def test_sonority_curve():
    c, e, p = _load()
    r = sonority_curve.compute(p, c)
    ex = e["sonority_curve"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["mean_sonority"] == ex["mean_sonority"]
    assert r.data["rises"] == ex["rises"]
    assert r.data["falls"] == ex["falls"]
    assert r.data["contour"] == ex["contour"]
    assert r.data["dominant_class"] == ex["dominant_class"]


def test_larger_awfaq():
    c, e, p = _load()
    r = larger_awfaq.compute(p, c)
    ex = e["larger_awfaq"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["constant_3x3"] == ex["constant_3x3"]
    assert r.data["constant_4x4"] == ex["constant_4x4"]
    assert r.data["constant_5x5"] == ex["constant_5x5"]
    assert r.data["buduh_matches_root"] == ex["buduh_matches_root"]


def test_qibla_as_axis():
    c, e, p = _load()
    r = qibla_as_axis.compute(p, c)
    ex = e["qibla_as_axis"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["qibla_angle"] == ex["qibla_angle"]
    assert r.data["qibla_cardinal"] == ex["qibla_cardinal"]
    assert r.data["distance_to_mecca_km"] == ex["distance_to_mecca_km"]


def test_prayer_times_as_timing():
    c, e, p = _load()
    r = prayer_times_as_timing.compute(p, c)
    ex = e["prayer_times_as_timing"]
    assert r.certainty == "COMPUTED_STRICT"
    assert r.data["birth_period"] == ex["birth_period"]
    assert r.data["day_length_hours"] == ex["day_length_hours"]


def test_chronobiology():
    c, e, p = _load()
    r = chronobiology.compute(p, c)
    ex = e["chronobiology"]
    assert r.certainty == "APPROX"
    assert r.data["birth_season"] == ex["birth_season"]
    assert r.data["seasonal_chronotype"] == ex["seasonal_chronotype"]
    assert r.data["circadian_phase"] == ex["circadian_phase"]
    assert r.data["day_of_year"] == ex["day_of_year"]
    assert r.data["nearest_cardinal_point"] == ex["nearest_cardinal_point"]


def _load_output_result(system_id: str) -> dict:
    """Load a specific result from output.json (for comparative module testing)."""
    base = Path(__file__).parent.parent
    data = json.loads((base / "output.json").read_text(encoding="utf-8"))
    for r in data["results"]:
        if r["id"] == system_id:
            return r["data"]
    return {}


def test_void_matrix():
    """Comparative module — test against output.json (needs full pipeline)."""
    c, e, p = _load()
    ex = e["void_matrix"]
    out = _load_output_result("void_matrix")
    assert out["lo_shu_missing"] == ex["lo_shu_missing"]
    assert out["void_center"] == ex["void_center"]
    assert out["total_voids"] == ex["total_voids"]
    assert out["torque"] == ex["torque"]


def test_barzakh_coefficient():
    """Comparative module — test against output.json (needs full pipeline)."""
    c, e, p = _load()
    ex = e["barzakh_coefficient"]
    out = _load_output_result("barzakh_coefficient")
    assert out["coefficient"] == ex["coefficient"]
    assert out["classification"] == ex["classification"]


def test_hermetic_alignment():
    """Comparative module — test against output.json (needs full pipeline)."""
    c, e, p = _load()
    ex = e["hermetic_alignment"]
    out = _load_output_result("hermetic_alignment")
    assert out["axis_count"] == ex["axis_count"]
    assert out["agreements"] == ex["agreements"]
    assert out["alignment_score"] == ex["alignment_score"]
    assert out["dominant_value"] == ex["dominant_value"]


def test_execution_pattern_analysis():
    """Comparative module — test against output.json (needs full pipeline)."""
    c, e, p = _load()
    ex = e["execution_pattern_analysis"]
    out = _load_output_result("execution_pattern_analysis")
    assert out["compound_count"] == ex["compound_count"]
    assert out["pattern"] == ex["pattern"]


def test_minimum_viable_signature():
    """Comparative module — test against output.json (needs full pipeline)."""
    c, e, p = _load()
    ex = e["minimum_viable_signature"]
    out = _load_output_result("minimum_viable_signature")
    assert out["fact_count"] == ex["fact_count"]


# ── Round 5 Wave 1: Decoz Layer ────────────────────────────────────────────


def test_balance_number():
    c, e, p = _load()
    r = balance_number.compute(p, c)
    ex = e["balance_number"]
    assert r.data["raw_sum"] == ex["raw_sum"]
    assert r.data["balance_number"] == ex["balance_number"]
    assert r.certainty == "COMPUTED_STRICT"


def test_rational_thought():
    c, e, p = _load()
    r = rational_thought.compute(p, c)
    ex = e["rational_thought"]
    assert r.data["first_name_sum"] == ex["first_name_sum"]
    assert r.data["birthday_number"] == ex["birthday_number"]
    assert r.data["rational_thought"] == ex["rational_thought"]
    assert r.certainty == "COMPUTED_STRICT"


def test_inclusion_table():
    c, e, p = _load()
    r = inclusion_table.compute(p, c)
    ex = e["inclusion_table"]
    assert r.data["total_letters"] == ex["total_letters"]
    assert r.data["missing_digits"] == ex["missing_digits"]
    assert r.data["karmic_lesson_count"] == ex["karmic_lesson_count"]
    assert r.data["dominant_digits"] == ex["dominant_digits"]
    assert r.data["dominant_frequency"] == ex["dominant_frequency"]
    assert r.certainty == "COMPUTED_STRICT"


def test_special_letters():
    c, e, p = _load()
    r = special_letters.compute(p, c)
    ex = e["special_letters"]
    assert r.data["first_vowel_letter"] == ex["first_vowel_letter"]
    assert r.data["first_vowel_value"] == ex["first_vowel_value"]
    assert r.data["first_consonant_letter"] == ex["first_consonant_letter"]
    assert r.data["first_consonant_value"] == ex["first_consonant_value"]
    assert r.certainty == "COMPUTED_STRICT"


def test_period_cycles():
    c, e, p = _load()
    r = period_cycles.compute(p, c)
    ex = e["period_cycles"]
    assert r.data["period_1"]["number"] == ex["period_1_number"]
    assert r.data["period_2"]["number"] == ex["period_2_number"]
    assert r.data["period_3"]["number"] == ex["period_3_number"]
    assert r.data["current_period"] == ex["current_period"]
    assert r.certainty == "COMPUTED_STRICT"


def test_transit_letters():
    c, e, p = _load()
    r = transit_letters.compute(p, c)
    ex = e["transit_letters"]
    assert r.data["physical"]["letter"] == ex["physical_letter"]
    assert r.data["physical"]["value"] == ex["physical_value"]
    assert r.data["mental"]["letter"] == ex["mental_letter"]
    assert r.data["mental"]["value"] == ex["mental_value"]
    assert r.data["spiritual"]["letter"] == ex["spiritual_letter"]
    assert r.data["spiritual"]["value"] == ex["spiritual_value"]
    assert r.data["transit_sum"] == ex["transit_sum"]
    assert r.certainty == "COMPUTED_STRICT"


def test_yearly_essence_cycle():
    c, e, p = _load()
    r = yearly_essence_cycle.compute(p, c)
    ex = e["yearly_essence_cycle"]
    assert r.data["transit_sum"] == ex["transit_sum"]
    assert r.data["essence_number"] == ex["essence_number"]
    assert r.certainty == "COMPUTED_STRICT"


def test_minor_numbers():
    c, e, p = _load()
    r = minor_numbers.compute(p, c)
    ex = e["minor_numbers"]
    assert r.certainty == ex["certainty"]


# ── Round 5 Wave 2: Tarot + Esoteric + Hellenistic ────────────────────────


def test_tarot_greer_birth_cards():
    c, e, p = _load()
    r = tarot_greer_birth_cards.compute(p, c)
    ex = e["tarot_greer_birth_cards"]
    assert r.data["personality_card"] == ex["personality_card"]
    assert r.data["soul_card"] == ex["soul_card"]
    assert r.data["constellation_root"] == ex["constellation_root"]
    assert r.data["hidden_factor_numbers"] == ex["hidden_factor_numbers"]
    assert r.certainty == "COMPUTED_STRICT"


def test_greer_zodiac_card():
    c, e, p = _load()
    r = greer_zodiac_card.compute(p, c)
    ex = e["greer_zodiac_card"]
    assert r.data["sun_sign"] == ex["sun_sign"]
    assert r.data["zodiac_card_number"] == ex["zodiac_card_number"]
    assert r.data["zodiac_card_name"] == ex["zodiac_card_name"]


def test_prenatal_syzygy():
    c, e, p = _load()
    r = prenatal_syzygy.compute(p, c)
    ex = e["prenatal_syzygy"]
    assert r.data["syzygy_type"] == ex["syzygy_type"]
    assert r.data["syzygy_sign"] == ex["syzygy_sign"]
    assert r.certainty == "COMPUTED_STRICT"


def test_cheiro_extensions():
    c, e, p = _load()
    r = cheiro_extensions.compute(p, c)
    ex = e["cheiro_extensions"]
    assert r.data["chaldean_total"] == ex["chaldean_total"]
    assert r.data["compound_number"] == ex["compound_number"]
    assert r.data["compound_root"] == ex["compound_root"]
    assert r.data["compound_name"] == ex["compound_name"]
    assert r.data["color_key_number"] == ex["color_key_number"]
    assert r.certainty == "LOOKUP_FIXED"


def test_roman_chronogram():
    c, e, p = _load()
    r = roman_chronogram.compute(p, c)
    ex = e["roman_chronogram"]
    assert r.data["chronogram_total"] == ex["chronogram_total"]
    assert r.data["chronogram_root"] == ex["chronogram_root"]
    assert r.data["roman_letter_count"] == ex["roman_letter_count"]
    assert r.certainty == "COMPUTED_STRICT"


def test_hebrew_aiq_beker():
    c, e, p = _load()
    r = hebrew_aiq_beker.compute(p, c)
    ex = e["hebrew_aiq_beker"]
    assert r.data["chamber_sum"] == ex["chamber_sum"]
    assert r.data["chamber_root"] == ex["chamber_root"]
    assert r.data["dominant_chamber"] == ex["dominant_chamber"]
    assert r.data["dominant_count"] == ex["dominant_count"]
    assert r.certainty == "COMPUTED_STRICT"


# ── Round 5 Wave 3: Cross-Tradition ───────────────────────────────────────


def test_tibetan_parkha():
    c, e, p = _load()
    r = tibetan_parkha.compute(p, c)
    ex = e["tibetan_parkha"]
    assert r.data["parkha_name"] == ex["parkha_name"]
    assert r.data["parkha_element"] == ex["parkha_element"]
    assert r.data["tibetan_age"] == ex["tibetan_age"]
    assert r.certainty == "COMPUTED_STRICT"


def test_tibetan_elements():
    c, e, p = _load()
    r = tibetan_elements.compute(p, c)
    ex = e["tibetan_elements"]
    assert r.data["lo_element"] == ex["lo_element"]
    assert r.data["lo_polarity"] == ex["lo_polarity"]
    assert r.data["srog_element"] == ex["srog_element"]
    assert r.data["srog_animal"] == ex["srog_animal"]
    assert r.certainty == "COMPUTED_STRICT"


def test_tamil_panchapakshi():
    """Ephemeris module — test against output.json."""
    c, e, p = _load()
    ex = e["tamil_panchapakshi"]
    out = _load_output_result("tamil_panchapakshi")
    assert out["natal_bird"] == ex["natal_bird"]
    assert out["nakshatra_number"] == ex["nakshatra_number"]
    assert out["paksha"] == ex["paksha"]


def test_chinese_jian_chu():
    c, e, p = _load()
    r = chinese_jian_chu.compute(p, c)
    ex = e["chinese_jian_chu"]
    assert r.data["day_officer"] == ex["day_officer"]
    assert r.data["day_officer_meaning"] == ex["day_officer_meaning"]
    assert r.data["day_officer_quality"] == ex["day_officer_quality"]
    assert r.certainty == "COMPUTED_STRICT"


def test_igbo_market_day():
    c, e, p = _load()
    r = igbo_market_day.compute(p, c)
    ex = e["igbo_market_day"]
    assert r.data["market_day"] == ex["market_day"]
    assert r.data["igbo_element"] == ex["igbo_element"]
    assert r.data["days_from_epoch"] == ex["days_from_epoch"]
    assert r.certainty == "COMPUTED_STRICT"


def test_zoroastrian_day_yazata():
    c, e, p = _load()
    r = zoroastrian_day_yazata.compute(p, c)
    ex = e["zoroastrian_day_yazata"]
    assert r.data["roj_number"] == ex["roj_number"]
    assert r.data["roj_name"] == ex["roj_name"]
    assert r.data["yazata_name"] == ex["yazata_name"]
    assert r.data["yazata_element"] == ex["yazata_element"]
    assert r.certainty == "LOOKUP_FIXED"


def test_vedic_arudha_pada():
    """Ephemeris module — test against output.json."""
    c, e, p = _load()
    ex = e["vedic_arudha_pada"]
    out = _load_output_result("vedic_arudha_pada")
    assert out["arudha_lagna_sign"] == ex["arudha_lagna_sign"]
    assert out["lagna_lord"] == ex["lagna_lord"]


def test_vedic_upapada_lagna():
    """Ephemeris module — test against output.json."""
    c, e, p = _load()
    ex = e["vedic_upapada_lagna"]
    out = _load_output_result("vedic_upapada_lagna")
    assert out["upapada_sign"] == ex["upapada_sign"]
    assert out["twelfth_lord"] == ex["twelfth_lord"]


def test_vedic_pushkara_navamsha():
    """Ephemeris module — test against output.json."""
    c, e, p = _load()
    ex = e["vedic_pushkara_navamsha"]
    out = _load_output_result("vedic_pushkara_navamsha")
    assert out["moon_pushkara"] == ex["moon_pushkara"]
    assert out["pushkara_status"] == ex["pushkara_status"]


def test_bazi_san_he_san_hui():
    """BaZi module — test against output.json (needs bazi_data)."""
    c, e, p = _load()
    ex = e["bazi_san_he_san_hui"]
    out = _load_output_result("bazi_san_he_san_hui")
    assert out["san_he_count"] == ex["san_he_count"]
    assert out["san_hui_count"] == ex["san_hui_count"]


def test_zwds_si_hua_palace():
    c, e, p = _load()
    r = zwds_si_hua_palace.compute(p, c)
    ex = e["zwds_si_hua_palace"]
    assert r.data["year_stem"] == ex["year_stem"]
    assert r.data["lu_star"] == ex["lu_star"]
    assert r.data["quan_star"] == ex["quan_star"]
    assert r.data["ke_star"] == ex["ke_star"]
    assert r.data["ji_star"] == ex["ji_star"]
    assert r.certainty == "COMPUTED_STRICT"


def test_hebrew_mispar_variants():
    c, e, p = _load()
    r = hebrew_mispar_variants.compute(p, c)
    ex = e["hebrew_mispar_variants"]
    assert r.data["gadol_total"] == ex["gadol_total"]
    assert r.data["gadol_root"] == ex["gadol_root"]
    assert r.data["siduri_total"] == ex["siduri_total"]
    assert r.data["siduri_root"] == ex["siduri_root"]
    assert r.data["boneeh_total"] == ex["boneeh_total"]
    assert r.data["boneeh_root"] == ex["boneeh_root"]
    assert r.data["hakadmi_total"] == ex["hakadmi_total"]
    assert r.data["hakadmi_root"] == ex["hakadmi_root"]
    assert r.data["letter_count"] == ex["letter_count"]
    assert r.certainty == "COMPUTED_STRICT"


# ── Round 5 Wave 4: Planes of Expression ──────────────────────────────────


def test_planes_of_expression():
    c, e, p = _load()
    r = planes_of_expression.compute(p, c)
    ex = e["planes_of_expression"]
    assert r.data["physical_count"] == ex["physical_count"]
    assert r.data["physical_root"] == ex["physical_root"]
    assert r.data["mental_count"] == ex["mental_count"]
    assert r.data["mental_root"] == ex["mental_root"]
    assert r.data["emotional_count"] == ex["emotional_count"]
    assert r.data["emotional_root"] == ex["emotional_root"]
    assert r.data["intuitive_count"] == ex["intuitive_count"]
    assert r.data["intuitive_root"] == ex["intuitive_root"]
    assert r.data["dominant_plane"] == ex["dominant_plane"]
    assert r.data["total_letters"] == ex["total_letters"]
    assert r.certainty == "COMPUTED_STRICT"
