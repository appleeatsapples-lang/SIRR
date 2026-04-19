"""
Module Taxonomy — Section 1 ↔ Product Surface Mapping
======================================================
Maps engine module ids to one of four product-surface domains and a
display tier. Used by runner.py post-compute to inject `domain` + `tier`
fields into each result's output dict, activating unified_view.py's
render_domain path.

Target distribution matches the product brief:
  Numerology          : ~28 modules  (Balliett family)
  Name Intelligence   : ~40 modules  (gematria + Arabic letter science + cognate sums)
  Astro Timing        : ~30 modules  (Swiss Ephemeris + Vedic + timing)
  Convergence         : ~12 modules  (psych_composite synthesis)
  ── Product surface total: ~110
  ── Remaining ~128 modules stay domain=None → engine debug view showcase only

Tiers drive render_domain sort order (HERO → STANDARD → COMPRESSED).
HEROes surface first within each domain. Each domain gets ~1-3 HEROes.

Sources:
  - SIRR_MASTER_REGISTRY.md §4.1 (scholarship fidelity → domain alignment)
  - Product brief: "43 visible rows per profile" across 4 domains
  - Reference engine debug view showcase (v12.2 artifact) for tier hints
"""
from __future__ import annotations
from typing import Dict, Optional

# Domain literals match unified_view.DOMAIN_ORDER
NUMEROLOGY        = "numerology"
NAME_INTELLIGENCE = "name_intelligence"
ASTRO_TIMING      = "astro_timing"
CONVERGENCE       = "convergence"

# Tier literals match unified_view.render_domain sort order
HERO       = "HERO"
STANDARD   = "STANDARD"
COMPRESSED = "COMPRESSED"


# ─── NUMEROLOGY (28) — Balliett/Cheiro family ──────────────────────────────
_NUMEROLOGY = {
    # HEROes — the reader's anchor core-numbers
    "life_purpose":       HERO,
    "personal_year":      HERO,
    "pinnacles":          HERO,
    # STANDARD — secondary structural readings
    "balance_number":     STANDARD,
    "hidden_passion":     STANDARD,
    "subconscious_self":  STANDARD,
    "maturity":           STANDARD,
    "cornerstone":        STANDARD,
    "bridges":            STANDARD,
    "challenges":         STANDARD,
    "essence":            STANDARD,
    "period_cycles":      STANDARD,
    "attitude":           STANDARD,
    "karmic_debt":        STANDARD,
    "chaldean":           STANDARD,
    "compound":           STANDARD,
    "cheiro_extensions":  STANDARD,
    "rational_thought":   STANDARD,
    "inclusion_table":    STANDARD,
    "planes_of_expression": STANDARD,
    "enneagram_dob":      STANDARD,
    # COMPRESSED — derived/supporting
    "minor_numbers":              COMPRESSED,
    "minimum_viable_signature":   COMPRESSED,
    "yearly_essence_cycle":       COMPRESSED,
    "digit_patterns":             COMPRESSED,
    "void_matrix":                COMPRESSED,
    "execution_pattern_analysis": COMPRESSED,
    "lineage_computation":        COMPRESSED,
}

# ─── NAME INTELLIGENCE (40) — gematria + Arabic letter science ─────────────
_NAME_INTELLIGENCE = {
    # HEROes — Abjad Kabir is THE name-number anchor
    "abjad_kabir":              HERO,
    "gematria_word_matches":    HERO,
    "name_weight":              HERO,
    # STANDARD — classical abjad family
    "abjad_saghir":             STANDARD,
    "abjad_wusta":              STANDARD,
    "abjad_maghribi":           STANDARD,
    "abjad_visual_architecture": STANDARD,
    "jafr":                     STANDARD,
    "buduh":                    STANDARD,
    "taksir":                   STANDARD,
    "bast_kasr":                STANDARD,
    "larger_awfaq":             STANDARD,
    "zakat_huruf":              STANDARD,
    "istikhara_adad":           STANDARD,
    "wafq":                     STANDARD,
    "elemental_letters":        STANDARD,
    "luminous_dark":            STANDARD,
    "solar_lunar":              STANDARD,
    "arabic_letter_nature":     STANDARD,
    "arabic_morphology":        STANDARD,
    "arabic_phonetics":         STANDARD,
    "arabic_rhetoric":          STANDARD,
    "arabic_roots":             STANDARD,
    "divine_breath":            STANDARD,
    "name_semantics":           STANDARD,
    "persian_abjad":            STANDARD,
    # STANDARD — cognate sums (§4.5 rule 2 compliant)
    "mandaean_gematria":        HERO,
    "ethiopian_asmat":          HERO,
    "hebrew_gematria":          HERO,
    # STANDARD — non-Arabic classical gematria
    "greek_isopsephy":          STANDARD,
    "coptic_isopsephy":         STANDARD,
    "armenian_gematria":        STANDARD,
    "georgian_gematria":        STANDARD,
    # COMPRESSED — letter-science supporting
    "special_letters":          COMPRESSED,
    "sonority_curve":           COMPRESSED,
    "calligraphy_structure":    COMPRESSED,
    "mantra_seed_syllable":     COMPRESSED,
    "qibla_as_axis":            COMPRESSED,
    # COMPRESSED — Hebrew ciphers on Arabic (§4.1 CLASSICAL_METHOD_MODERN_APPLICATION)
    "atbash":                   COMPRESSED,
    "albam":                    COMPRESSED,
    "avgad":                    COMPRESSED,
    "notarikon":                COMPRESSED,
}

# ─── ASTRO TIMING (30) — Swiss Ephemeris natal + timing ────────────────────
_ASTRO_TIMING = {
    # HEROes — the chart anchors
    "natal_chart":              HERO,
    "bazi_pillars":             HERO,
    "vimshottari":              HERO,
    # STANDARD — Hellenistic / medieval Islamic natal
    "aspects":                  STANDARD,
    "house_system":             STANDARD,
    "sect":                     STANDARD,
    "essential_dignities":      STANDARD,
    "almuten":                  STANDARD,
    "reception":                STANDARD,
    "temperament":              STANDARD,
    "prenatal_syzygy":          STANDARD,
    # STANDARD — timing
    "profection":               STANDARD,
    "firdaria":                 STANDARD,
    "solar_return":             STANDARD,
    "progressions":             STANDARD,
    "solar_arc":                STANDARD,
    "zodiacal_releasing":       STANDARD,
    "tasyir":                   STANDARD,
    # STANDARD — Vedic
    "nakshatra":                STANDARD,
    "vedic_tithi":              STANDARD,
    "yogini_dasha":             STANDARD,
    "kp_system":                STANDARD,
    "panchamahabhuta":          STANDARD,
    # STANDARD — Chinese
    "bazi_daymaster":           STANDARD,
    "bazi_luck_pillars":        STANDARD,
    "four_pillars_balance":     STANDARD,
    "flying_star":              STANDARD,
    # STANDARD — cycle theory (renamed per §4.5)
    "biorhythm":                STANDARD,
    "chronobiology":            STANDARD,
    "circadian_medicine":       STANDARD,
}

# ─── CONVERGENCE (12) — psych_composite synthesis ──────────────────────────
_CONVERGENCE = {
    # HEROes — the signal-aggregating layers
    "archetype_consensus":        HERO,
    "element_consensus":          HERO,
    "timing_consensus":           HERO,
    # STANDARD — structural synthesis
    "planetary_ruler_consensus":  STANDARD,
    "barzakh_coefficient":        STANDARD,
    "hermetic_alignment":         STANDARD,
    "hermetic_element_balance":   STANDARD,
    # STANDARD — cross-tradition touchpoints
    "zairja":                     STANDARD,
    "cross_scripture":            STANDARD,
    # COMPRESSED — tradition-local signatures that co-occur
    "god_of_day":                 COMPRESSED,
    "quranic_figures":            COMPRESSED,
    "malwasha":                   COMPRESSED,
}


# ─── Consolidated lookup tables ────────────────────────────────────────────
MODULE_DOMAIN: Dict[str, str] = {}
MODULE_TIER: Dict[str, str] = {}

for _dom_id, _modules in (
    (NUMEROLOGY, _NUMEROLOGY),
    (NAME_INTELLIGENCE, _NAME_INTELLIGENCE),
    (ASTRO_TIMING, _ASTRO_TIMING),
    (CONVERGENCE, _CONVERGENCE),
):
    for _mid, _tier in _modules.items():
        MODULE_DOMAIN[_mid] = _dom_id
        MODULE_TIER[_mid] = _tier


# ─── §4.5-compliant display names (engine-source override) ──────────────────
# These are applied by apply_taxonomy() so the engine output JSON ships
# honest module names for every profile. Mirrors and extends
# unified_view.py's _ID_LABEL_REWRITES (which remains as a render-time
# safety net for any module not listed here).
#
# Rule 1 — modern systems must carry era/author context
# Rule 2 — cognate-mapping modules must admit identity-by-construction
# Rule 4 — Zairja names Ibn Khaldun's critique
# Rule 5 — SIRR-invented composite layers named as such

MODULE_NAME_OVERRIDE = {
    # Rule 2 — cognate-mapping (10 modules already self-declare at source;
    # these are for apply_taxonomy fallback parity)
    # (mandaean/ethiopian/hebrew_gematria, chaldean, zairja self-declare)

    # Rule 1 — Western numerology / occult revival (MODERN_SYNTHESIS)
    "biorhythm":                   "Daily cycle index (Biorhythm, modern cycle theory)",
    "compound":                    "Compound number meanings (Cheiro, 20th c.)",
    "cheiro_extensions":           "Cheiro compound + color (20th c.)",
    "agrippan":                    "Agrippan ciphers (Western occult revival)",
    "thelemic_gematria":           "Thelemic ALW cipher (Crowley, 1904)",
    "trithemius":                  "Trithemius steganographic cipher (1499)",
    "gd_correspondences":          "Golden Dawn 777 correspondences (1890s)",
    "rose_cross_sigil":            "Rose Cross sigil (Golden Dawn)",
    "sephirotic_path_analysis":    "Sephirot path reading (modern Kabbalah application)",
    "tree_of_life":                "Tree of Life path (modern Kabbalah synthesis)",
    "hermetic_alignment":          "SIRR comparative axes (hermetic framing)",
    "ars_magna":                   "Ars Magna (Llull, c. 1274 — Lullian combinatorics)",
    "solomonic_correspondences":   "Solomonic correspondences (modern occult compilation)",

    # Rule 1 — Tarot family (18th-c. esoteric revival)
    "tarot_birth":                 "Tarot Birth Cards (esoteric revival, 18th c.)",
    "tarot_year":                  "Tarot Year Card (esoteric revival, 18th c.)",
    "tarot_name":                  "Tarot Name Cards (esoteric revival, 18th c.)",
    "tarot_greer_birth_cards":     "Tarot Birth-Card constellation (Mary Greer, modern)",
    "greer_zodiac_card":           "Zodiac card method (Greer, modern)",
    "cardology":                   "Cardology birth card (Olney Richmond, 1893)",

    # Rule 1 — 20th-c. invented systems
    "human_design":                "Human Design (Ra Uru Hu, 1987)",
    "gene_keys":                   "Gene Keys (Richard Rudd, 2007)",
    "dreamspell":                  "Dreamspell / Galactic Signature (Argüelles, 1990)",
    "enneagram_dob":               "Enneagram from DOB (modern application)",
    "enneagram_deeper":            "Enneagram deeper analysis (modern)",
    "chronobiology":               "Chronobiology — modern biological rhythms (الأحياء الزمنية)",
    "circadian_medicine":          "Circadian medicine — birth-hour organ clock (modern)",
    "seasonal_psychology":         "Seasonal psychology — birth-season correlates (modern)",
    "steiner_cycles":              "Steiner 7-year cycles (anthroposophic, 20th c.)",
    "latin_ordinal":               "Latin ordinal gematria (A=1..Z=26, modern cipher)",
    "roman_chronogram":            "Roman chronogram name (medieval Latin device, modern application)",
    "letter_position_encoding":    "Letter position encoding (SIRR analysis, ترميز المواقع)",
    "transit_letters":             "Transit letters (physical/mental/spiritual — modern numerology)",
    "tonalpohualli":               "Aztec Tonalpohualli day-count (classical)",

    # Rule 5 — SIRR-invented composite layers (name as SIRR synthesis)
    "archetype_consensus":         "Archetype Consensus — SIRR cross-tradition synthesis",
    "element_consensus":           "Element Consensus — SIRR cross-tradition synthesis",
    "timing_consensus":            "Timing Consensus — SIRR cross-tradition synthesis",
    "planetary_ruler_consensus":   "Planetary Ruler Consensus — SIRR cross-tradition synthesis",
    "lineage_computation":         "Lineage Computation — SIRR multi-generational synthesis (حساب النسب)",
    "barzakh_coefficient":         "Barzakh Coefficient — SIRR composite metric (معامل البرزخ)",
    "temperament":                 "Four Temperaments — classical + Unani blend",
}


def domain_for(module_id: str) -> Optional[str]:
    """Return the product-surface domain for a module id, or None if the
    module is engine debug view-only (not surfaced in the live product view)."""
    return MODULE_DOMAIN.get(module_id)


def tier_for(module_id: str) -> Optional[str]:
    """Return HERO/STANDARD/COMPRESSED for a module id, or None if not
    classified (module will not render in domain tables)."""
    return MODULE_TIER.get(module_id)


def apply_taxonomy(result_dict: dict) -> dict:
    """Mutate a serialized result dict to add domain + tier + scholarship_fidelity.

    Domain + tier activate unified_view.render_domain (unclassified modules get
    None and are not surfaced).

    scholarship_fidelity is injected into result["data"] if not already present
    — modules that declare it explicitly at module source (currently 10) keep
    their self-declared value. Result: the §4.6 crosswalk becomes
    engine-derived for all 238 modules, not just 10.
    """
    mid = result_dict.get("id")
    if not mid:
        return result_dict

    result_dict["domain"] = MODULE_DOMAIN.get(mid)
    result_dict["tier"]   = MODULE_TIER.get(mid)

    # §4.5-compliant name override (taxonomy layer is the source of truth)
    # Module-level `name` is treated as legacy — we swap in the curated
    # honest display name. The module source `name` is still available via
    # the `name_legacy` field for debugging / full provenance.
    name_override = MODULE_NAME_OVERRIDE.get(mid)
    if name_override and name_override != result_dict.get("name"):
        result_dict["name_legacy"] = result_dict.get("name")
        result_dict["name"] = name_override

    # scholarship_fidelity fallback (module source takes precedence)
    data = result_dict.get("data")
    if isinstance(data, dict) and "scholarship_fidelity" not in data:
        fid = fidelity_for(mid)
        if fid is not None:
            data["scholarship_fidelity"] = fid
            # Only add a terse classifier-derived note if the module didn't
            # already provide scholarship_note at module source
            if "scholarship_note" not in data:
                data["scholarship_note"] = (
                    f"Classified {fid} via §4.6 crosswalk classifier "
                    "(module source did not declare explicitly)."
                )
    return result_dict




# ─── Scholarship Fidelity classifier (§4.6 crosswalk rules) ─────────────────
# This provides a FALLBACK for modules whose source doesn't explicitly set
# data["scholarship_fidelity"]. Modules that DO set it explicitly (currently
# 10: mandaean/ethiopian/hebrew_gematria, chaldean, zairja, quranic/torah/nt
# figures, cross_scripture, god_of_day) keep their source-declared value.
#
# Classifier rules mirror §4.1 registry:
#   CLASSICAL                           = source-attested tradition
#   CLASSICAL_METHOD_MODERN_APPLICATION = classical method applied outside
#                                         classical scope
#   MODERN_SYNTHESIS                    = invented/elaborated 18th-c. onward

_EXPLICIT_FIDELITY = {
    "quranic_figures":     "CLASSICAL_METHOD_MODERN_APPLICATION",
    "torah_figures":       "CLASSICAL_METHOD_MODERN_APPLICATION",
    "nt_figures":          "CLASSICAL_METHOD_MODERN_APPLICATION",
    "cross_scripture":     "CLASSICAL_METHOD_MODERN_APPLICATION",
    "zairja":              "CLASSICAL_METHOD_MODERN_APPLICATION",
    "atbash":              "CLASSICAL_METHOD_MODERN_APPLICATION",
    "albam":               "CLASSICAL_METHOD_MODERN_APPLICATION",
    "avgad":               "CLASSICAL_METHOD_MODERN_APPLICATION",
    "notarikon":           "CLASSICAL_METHOD_MODERN_APPLICATION",
    "hebrew_aiq_beker":    "CLASSICAL_METHOD_MODERN_APPLICATION",
    "hebrew_mispar_variants": "CLASSICAL_METHOD_MODERN_APPLICATION",

    "mandaean_gematria":   "MODERN_SYNTHESIS",
    "ethiopian_asmat":     "MODERN_SYNTHESIS",
    "hebrew_gematria":     "MODERN_SYNTHESIS",
    "chaldean":            "MODERN_SYNTHESIS",
    "god_of_day":          "CLASSICAL",
}

_MODERN_SYNTHESIS_IDS = frozenset({
    # Balliett / Chaldean numerology family
    "life_purpose", "name_weight", "balance_number", "hidden_passion",
    "subconscious_self", "maturity", "bridges", "challenges", "pinnacles",
    "rational_thought", "inclusion_table", "cornerstone",
    "planes_of_expression", "karmic_debt", "personal_year", "essence",
    "period_cycles", "attitude", "compound", "cheiro_extensions",
    "minor_numbers", "minimum_viable_signature", "digit_patterns",
    "yearly_essence_cycle", "void_matrix", "execution_pattern_analysis",
    # Tarot family (18th-c. esoteric)
    "tarot_birth", "tarot_year", "tarot_name", "tarot_greer_birth_cards",
    "greer_zodiac_card", "cardology",
    # Western occult revival
    "tree_of_life", "gd_correspondences", "rose_cross_sigil",
    "thelemic_gematria", "agrippan", "trithemius", "ars_magna",
    "solomonic_correspondences", "sephirotic_path_analysis",
    "hermetic_alignment",
    # Late-20th-c. invented systems
    "human_design", "gene_keys", "dreamspell",
    # Other modern-synthesis one-offs
    "biorhythm", "roman_chronogram", "steiner_cycles",
    "seasonal_psychology", "chronobiology", "circadian_medicine",
    "tonalpohualli", "enneagram_dob", "enneagram_deeper",
    "transit_letters", "latin_ordinal", "letter_position_encoding",
    # SIRR/modern composite synthesis layers
    "archetype_consensus", "element_consensus", "timing_consensus",
    "planetary_ruler_consensus", "lineage_computation",
    "barzakh_coefficient", "temperament",
})

_ASTRO_CLASSICAL_PREFIXES = (
    "bazi", "zwds", "zi_wei", "solar_", "lunar_", "natal_", "vedic_",
    "jaimini", "nakshatra", "navamsha", "shodashavarga", "ashtakavarga",
    "shadbala", "tajika", "kalachakra", "vimshottari", "yogini_dasha",
    "ashtottari_dasha", "chara_dasha", "kala_sarpa", "kp_", "ayurvedic",
    "panchamahabhuta", "sabian", "planetary_", "house_system", "sect",
    "essential_dignities", "almuten", "bonification", "dorothean",
    "zodiacal_releasing", "profection", "firdaria", "solar_arc",
    "progressions", "tasyir", "horary_timing", "rectification",
    "babylonian_horoscope", "aspects", "midpoints", "declinations",
    "reception", "astrocartography", "harmonic_charts", "synastry",
    "prenatal_syzygy", "primary_directions", "antiscia", "uranian",
    "fixed_stars", "draconic_chart", "decan", "dwad", "day_ruler",
    "egyptian_decan", "electional_windows", "muhurta", "manazil",
    "mahabote", "nadi_amsa", "prashna_natal", "sarvatobhadra",
    "sudarshana", "tamil_panchapakshi", "four_pillars_balance",
    "hermetic_element_balance", "arabic_parts",
)

_OTHER_CLASSICAL_IDS = frozenset({
    # Chinese metaphysics
    "flying_star", "bazhai", "nine_star_ki", "lo_shu_grid",
    "qimen", "liu_ren", "meihua", "taiyi",
    # Divinatory / oracle
    "ifa", "iching", "geomancy",
    # Non-Arabic classical gematria
    "greek_isopsephy", "coptic_isopsephy", "armenian_gematria",
    "georgian_gematria", "chinese_zodiac",
    # Calendar conversions
    "hijri", "hebrew_calendar", "mayan", "pawukon", "weton", "julian",
    "maramataka", "primbon", "nayin",
    "chinese_jian_chu", "zoroastrian_day_yazata",
    "celtic_tree", "ogham", "birth_rune", "onmyodo",
    "tibetan_mewa", "tibetan_parkha", "tibetan_elements",
    "african_day_name_extended",
    # Arabic classical letter-science
    "abjad_kabir", "abjad_saghir", "abjad_wusta", "abjad_maghribi",
    "abjad_visual_architecture", "jafr", "buduh", "taksir", "bast_kasr",
    "larger_awfaq", "zakat_huruf", "istikhara_adad", "wafq",
    "elemental_letters", "luminous_dark", "solar_lunar",
    "arabic_letter_nature", "arabic_morphology", "arabic_phonetics",
    "arabic_rhetoric", "arabic_roots", "divine_breath", "special_letters",
    "sonority_curve", "calligraphy_structure",
    "mantra_seed_syllable", "name_semantics", "qibla_as_axis",
    "persian_abjad", "gematria_word_matches",
    "hijri_calendar_encoding", "akan_kra_din", "igbo_market_day",
    "prayer_times_as_timing", "malwasha",
})


def fidelity_for(module_id: str):
    """Classify a module id into its §4.1 scholarship-fidelity label.
    Returns one of: CLASSICAL | CLASSICAL_METHOD_MODERN_APPLICATION |
    MODERN_SYNTHESIS | None (if unknown)."""
    if module_id in _EXPLICIT_FIDELITY:
        return _EXPLICIT_FIDELITY[module_id]
    if module_id in _MODERN_SYNTHESIS_IDS:
        return "MODERN_SYNTHESIS"
    for p in _ASTRO_CLASSICAL_PREFIXES:
        if module_id.startswith(p):
            return "CLASSICAL"
    if module_id in _OTHER_CLASSICAL_IDS:
        return "CLASSICAL"
    return None


# ─── Self-test: distribution + total counts ────────────────────────────────
def _self_test():
    from collections import Counter
    dom_counts = Counter(MODULE_DOMAIN.values())
    tier_counts = Counter(MODULE_TIER.values())
    print(f"Total classified: {len(MODULE_DOMAIN)}")
    print("Domain distribution:")
    for d, n in dom_counts.most_common():
        print(f"  {d:<22} {n}")
    print("Tier distribution:")
    for t, n in tier_counts.most_common():
        print(f"  {t:<12} {n}")


if __name__ == "__main__":
    _self_test()
