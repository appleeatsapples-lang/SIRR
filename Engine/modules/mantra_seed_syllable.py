"""
Mantra Seed Syllable (बीज मन्त्र)
───────────────────────────────────
Derives the mantra seed syllable (bija) from the birth nakshatra pada.

Algorithm:
  1. Get Moon's sidereal longitude from natal chart
  2. Compute nakshatra (0-26) and pada (1-4)
  3. Look up bija syllable from vedic_lookups.json nakshatra_bija table

Source: BPHS; Muhurta Chintamani; Jyotish naming tradition
SOURCE_TIER: A (primary Vedic text — used for traditional name selection)
"""
from __future__ import annotations
import math
from sirr_core.types import InputProfile, SystemResult


# Nakshatra names in order (0-26)
NAKSHATRAS = [
    "ashwini", "bharani", "krittika", "rohini", "mrigashira",
    "ardra", "punarvasu", "pushya", "ashlesha", "magha",
    "purva_phalguni", "uttara_phalguni", "hasta", "chitra",
    "swati", "vishakha", "anuradha", "jyeshtha", "mula",
    "purva_ashadha", "uttara_ashadha", "shravana", "dhanishta",
    "shatabhisha", "purva_bhadrapada", "uttara_bhadrapada", "revati",
]

# Bija table from vedic_lookups.json
NAKSHATRA_BIJA = {
    "ashwini": {"pada_1": "Chu", "pada_2": "Che", "pada_3": "Cho", "pada_4": "La"},
    "bharani": {"pada_1": "Li", "pada_2": "Lu", "pada_3": "Le", "pada_4": "Lo"},
    "krittika": {"pada_1": "A", "pada_2": "I", "pada_3": "U", "pada_4": "E"},
    "rohini": {"pada_1": "O", "pada_2": "Va", "pada_3": "Vi", "pada_4": "Vu"},
    "mrigashira": {"pada_1": "Ve", "pada_2": "Vo", "pada_3": "Ka", "pada_4": "Ki"},
    "ardra": {"pada_1": "Ku", "pada_2": "Gha", "pada_3": "Ng", "pada_4": "Jha"},
    "punarvasu": {"pada_1": "Ke", "pada_2": "Ko", "pada_3": "Ha", "pada_4": "Hi"},
    "pushya": {"pada_1": "Hu", "pada_2": "He", "pada_3": "Ho", "pada_4": "Da"},
    "ashlesha": {"pada_1": "Di", "pada_2": "Du", "pada_3": "De", "pada_4": "Do"},
    "magha": {"pada_1": "Ma", "pada_2": "Mi", "pada_3": "Mu", "pada_4": "Me"},
    "purva_phalguni": {"pada_1": "Mo", "pada_2": "Ta", "pada_3": "Ti", "pada_4": "Tu"},
    "uttara_phalguni": {"pada_1": "Te", "pada_2": "To", "pada_3": "Pa", "pada_4": "Pi"},
    "hasta": {"pada_1": "Pu", "pada_2": "Sha", "pada_3": "Na", "pada_4": "Tha"},
    "chitra": {"pada_1": "Pe", "pada_2": "Po", "pada_3": "Ra", "pada_4": "Ri"},
    "swati": {"pada_1": "Ru", "pada_2": "Re", "pada_3": "Ro", "pada_4": "Ta"},
    "vishakha": {"pada_1": "Ti", "pada_2": "Tu", "pada_3": "Te", "pada_4": "To"},
    "anuradha": {"pada_1": "Na", "pada_2": "Ni", "pada_3": "Nu", "pada_4": "Ne"},
    "jyeshtha": {"pada_1": "No", "pada_2": "Ya", "pada_3": "Yi", "pada_4": "Yu"},
    "mula": {"pada_1": "Ye", "pada_2": "Yo", "pada_3": "Bha", "pada_4": "Bhi"},
    "purva_ashadha": {"pada_1": "Bhu", "pada_2": "Dha", "pada_3": "Pha", "pada_4": "Dha"},
    "uttara_ashadha": {"pada_1": "Bhe", "pada_2": "Bho", "pada_3": "Ja", "pada_4": "Ji"},
    "shravana": {"pada_1": "Ju", "pada_2": "Je", "pada_3": "Jo", "pada_4": "Gha"},
    "dhanishta": {"pada_1": "Ga", "pada_2": "Gi", "pada_3": "Gu", "pada_4": "Ge"},
    "shatabhisha": {"pada_1": "Go", "pada_2": "Sa", "pada_3": "Si", "pada_4": "Su"},
    "purva_bhadrapada": {"pada_1": "Se", "pada_2": "So", "pada_3": "Da", "pada_4": "Di"},
    "uttara_bhadrapada": {"pada_1": "Du", "pada_2": "Tha", "pada_3": "Jha", "pada_4": "Na"},
    "revati": {"pada_1": "De", "pada_2": "Do", "pada_3": "Cha", "pada_4": "Chi"},
}

# Lahiri ayanamsa approximate for modern dates
AYANAMSA_2000 = 23.856
AYANAMSA_RATE = 50.3 / 3600.0  # arcseconds per year


def _get_sidereal_moon(natal: dict) -> float | None:
    """Extract sidereal Moon longitude from natal chart data."""
    planets = natal.get("planets", {})
    moon = planets.get("Moon")
    if moon is None:
        return None
    tropical_lon = moon if isinstance(moon, (int, float)) else moon.get("longitude", moon.get("lon"))
    if tropical_lon is None:
        return None
    # Check if chart already provides sidereal
    if natal.get("zodiac") == "sidereal":
        return float(tropical_lon) % 360.0
    # Convert tropical → sidereal using Lahiri
    ayanamsa = natal.get("ayanamsa")
    if ayanamsa is None:
        # Approximate Lahiri for birth year
        try:
            import swisseph as swe
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            # Use JD if available
            jd = natal.get("jd_ut")
            if jd:
                ayanamsa = swe.get_ayanamsa_ut(jd)
            else:
                ayanamsa = AYANAMSA_2000
        except ImportError:
            ayanamsa = AYANAMSA_2000
    return (float(tropical_lon) - ayanamsa) % 360.0


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal = kwargs.get("natal_chart_data")
    if not natal:
        return SystemResult(
            id="mantra_seed_syllable",
            name="Mantra Seed Syllable (Bija)",
            certainty="NEEDS_EPHEMERIS",
            data={"bija": None, "reason": "No natal chart data"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["BPHS", "Muhurta Chintamani"],
            question="Q1_IDENTITY",
        )

    sid_moon = _get_sidereal_moon(natal)
    if sid_moon is None:
        return SystemResult(
            id="mantra_seed_syllable",
            name="Mantra Seed Syllable (Bija)",
            certainty="NEEDS_EPHEMERIS",
            data={"bija": None, "reason": "Moon longitude not available"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["BPHS", "Muhurta Chintamani"],
            question="Q1_IDENTITY",
        )

    # Each nakshatra spans 13°20' = 13.3333°
    nak_span = 360.0 / 27.0
    nak_idx = int(sid_moon / nak_span)
    if nak_idx >= 27:
        nak_idx = 26
    nak_name = NAKSHATRAS[nak_idx]

    # Each pada spans 3°20' = 3.3333°
    pada_span = nak_span / 4.0
    within_nak = sid_moon - (nak_idx * nak_span)
    pada = min(int(within_nak / pada_span) + 1, 4)

    # Look up bija syllable
    pada_key = f"pada_{pada}"
    bija_entry = NAKSHATRA_BIJA.get(nak_name, {})
    bija = bija_entry.get(pada_key, "?")

    return SystemResult(
        id="mantra_seed_syllable",
        name="Mantra Seed Syllable (Bija)",
        certainty="COMPUTED_STRICT",
        data={
            "nakshatra": nak_name,
            "nakshatra_index": nak_idx,
            "pada": pada,
            "bija_syllable": bija,
            "sidereal_moon_longitude": round(sid_moon, 4),
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["BPHS", "Muhurta Chintamani", "vedic_lookups.json"],
        question="Q1_IDENTITY",
    )
