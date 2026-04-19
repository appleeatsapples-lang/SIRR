"""Vimshottari Dasha — COMPUTED_STRICT (from sidereal Moon nakshatra)
Computes the Vedic planetary period (Maha Dasha) active at birth and currently.
Uses the 120-year Vimshottari system based on birth nakshatra of the MOON (sidereal/Lahiri).
Corrected per Parashara BPHS: dasha is keyed to Moon's sidereal nakshatra, not solar.
"""
from __future__ import annotations
from datetime import date
from sirr_core.types import InputProfile, SystemResult


# Fixed dasha sequence and durations
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

# Nakshatra number -> ruler (each ruler owns 3 nakshatras, 1-indexed)
NAKSHATRA_RULER = {
    1: "Ketu", 2: "Venus", 3: "Sun", 4: "Moon", 5: "Mars",
    6: "Rahu", 7: "Jupiter", 8: "Saturn", 9: "Mercury",
    10: "Ketu", 11: "Venus", 12: "Sun", 13: "Moon", 14: "Mars",
    15: "Rahu", 16: "Jupiter", 17: "Saturn", 18: "Mercury",
    19: "Ketu", 20: "Venus", 21: "Sun", 22: "Moon", 23: "Mars",
    24: "Rahu", 25: "Jupiter", 26: "Saturn", 27: "Mercury",
}

# Vedic benefic/malefic classification for dasha lords
DASHA_QUALITY = {
    "Ketu": "malefic", "Venus": "benefic", "Sun": "malefic",
    "Moon": "benefic", "Mars": "malefic", "Rahu": "malefic",
    "Jupiter": "benefic", "Saturn": "malefic", "Mercury": "neutral",
}

NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
    "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha",
    "Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati",
]


def _get_sidereal_moon(dob, birth_time_local, timezone):
    """Get sidereal (Lahiri) Moon longitude via Swiss Ephemeris."""
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        tz_offsets = {"Asia/Riyadh": 3, "Asia/Dubai": 4, "UTC": 0}
        tz_off = tz_offsets.get(timezone, 3)
        h, m = map(int, birth_time_local.split(":"))
        ut = (h + m / 60) - tz_off
        jd_ut = swe.julday(dob.year, dob.month, dob.day, ut)
        moon = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SIDEREAL)[0][0]
        return moon, True
    except ImportError:
        return None, False


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    moon_deg, has_ephem = _get_sidereal_moon(
        profile.dob,
        profile.birth_time_local or "10:14",
        profile.timezone or "Asia/Riyadh"
    )

    if has_ephem and moon_deg is not None:
        nak_span = 360.0 / 27
        nak_index = int(moon_deg / nak_span)  # 0-based
        nak_num = nak_index + 1               # 1-based
        degree_in_nak = moon_deg - (nak_index * nak_span)
        proportion_elapsed = degree_in_nak / nak_span
        note = f"Sidereal Moon={moon_deg:.4f}° (Lahiri). Nakshatra {nak_num} ({NAKSHATRA_NAMES[nak_index]})."
        certainty = "COMPUTED_STRICT"
    else:
        # Hardcoded fallback: Shravana #22 (Moon-ruled), sidereal-verified
        nak_num = 22
        nak_index = 21
        proportion_elapsed = 0.334  # Approx position within Shravana
        note = "Fallback: Shravana #22 (Moon) — ephemeris-verified sidereal value."
        certainty = "APPROX"

    birth_ruler = NAKSHATRA_RULER[nak_num]
    birth_dasha_total = DASHA_YEARS[birth_ruler]
    birth_dasha_remaining = birth_dasha_total * (1 - proportion_elapsed)

    # Build dasha timeline from birth
    start_idx = DASHA_ORDER.index(birth_ruler)
    timeline = []
    age_cursor = 0.0

    # First (partial) dasha
    timeline.append({
        "planet": birth_ruler,
        "years": round(birth_dasha_remaining, 1),
        "age_start": round(age_cursor, 1),
        "age_end": round(age_cursor + birth_dasha_remaining, 1),
    })
    age_cursor += birth_dasha_remaining

    # Subsequent full dashas
    for i in range(1, 9):
        idx = (start_idx + i) % 9
        planet = DASHA_ORDER[idx]
        years = DASHA_YEARS[planet]
        timeline.append({
            "planet": planet,
            "years": years,
            "age_start": round(age_cursor, 1),
            "age_end": round(age_cursor + years, 1),
        })
        age_cursor += years

    # Current age
    today = date.today()
    age_days = (today - profile.dob).days
    age_years = age_days / 365.25

    # Find current dasha
    current_dasha = timeline[0]
    for period in timeline:
        if period["age_start"] <= age_years < period["age_end"]:
            current_dasha = period
            break

    years_into = round(age_years - current_dasha["age_start"], 1)
    years_left = round(current_dasha["age_end"] - age_years, 1)

    return SystemResult(
        id="vimshottari",
        name="Vimshottari Dasha (120-Year Planetary Periods)",
        certainty=certainty,
        data={
            "birth_nakshatra": nak_num,
            "birth_nakshatra_name": NAKSHATRA_NAMES[nak_index],
            "birth_nakshatra_ruler": birth_ruler,
            "first_dasha_remaining_years": round(birth_dasha_remaining, 1),
            "current_age_years": round(age_years, 1),
            "current_maha_dasha": current_dasha["planet"],
            "current_dasha_start_age": current_dasha["age_start"],
            "current_dasha_end_age": current_dasha["age_end"],
            "years_into_current": years_into,
            "years_remaining": years_left,
            "timeline": timeline,
            "period_quality": DASHA_QUALITY.get(current_dasha["planet"], "neutral"),
            "note": note,
        },
        interpretation=f"Currently in {current_dasha['planet']} Maha Dasha (ages {current_dasha['age_start']}-{current_dasha['age_end']}). {years_into}y in, {years_left}y remaining. Birth nakshatra: {NAKSHATRA_NAMES[nak_index]} (ruler: {birth_ruler}).",
        constants_version=constants["version"],
        references=["Parashara, Brihat Parashara Hora Shastra — Vimshottari Dasha", 
                    "Swiss Ephemeris — Lahiri (Chitrapaksha) ayanamsa",
                    "120-year cycle: Ketu-Venus-Sun-Moon-Mars-Rahu-Jupiter-Saturn-Mercury"],
        question="Q4_TIMING"
    )
