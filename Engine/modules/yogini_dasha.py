"""Yogini Dasha — 36-Year Vedic Timing Cycle
A Vedic planetary period system based on 8 Yoginis, each governing a fixed period
(1-8 years, total 36). Derived from birth nakshatra (Moon longitude).
Source: BPHS (Brihat Parashara Hora Shastra).

COMPUTED_STRICT — uses sidereal Moon from Swiss Ephemeris.
"""
from __future__ import annotations
from datetime import date
from sirr_core.types import InputProfile, SystemResult

YOGINI_SEQUENCE = [
    {"yogini": "Mangala",  "planet": "Moon",    "years": 1},
    {"yogini": "Pingala",  "planet": "Sun",     "years": 2},
    {"yogini": "Dhanya",   "planet": "Jupiter", "years": 3},
    {"yogini": "Bhramari", "planet": "Mars",    "years": 4},
    {"yogini": "Bhadrika", "planet": "Mercury", "years": 5},
    {"yogini": "Ulka",     "planet": "Saturn",  "years": 6},
    {"yogini": "Siddha",   "planet": "Venus",   "years": 7},
    {"yogini": "Sankata",  "planet": "Rahu",    "years": 8},
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

CYCLE_LENGTH = 36  # sum of all yogini years

# Vedic benefic/malefic classification for yogini dasha planets
PLANET_QUALITY = {
    "Moon": "benefic", "Sun": "malefic", "Jupiter": "benefic",
    "Mars": "malefic", "Mercury": "neutral", "Saturn": "malefic",
    "Venus": "benefic", "Rahu": "malefic",
}


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


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    moon_deg, has_ephem = _get_sidereal_moon(
        profile.dob,
        profile.birth_time_local or "10:14",
        profile.timezone or "Asia/Riyadh",
    )

    if has_ephem and moon_deg is not None:
        nak_span = 360.0 / 27
        nak_index = int(moon_deg / nak_span)  # 0-based
        nak_num = nak_index + 1               # 1-based
        traversed = moon_deg - (nak_index * nak_span)
        remaining_fraction = 1.0 - (traversed / nak_span)
        certainty = "COMPUTED_STRICT"
    else:
        nak_num = 22
        nak_index = 21
        remaining_fraction = 0.6672
        certainty = "APPROX"

    # Starting Yogini
    start_idx = (nak_num - 1) % 8
    starting = YOGINI_SEQUENCE[start_idx]
    balance_years = remaining_fraction * starting["years"]

    # Build timeline
    timeline = []
    age_cursor = 0.0

    # First (partial) dasha
    timeline.append({
        "yogini": starting["yogini"],
        "planet": starting["planet"],
        "years": round(balance_years, 3),
        "age_start": round(age_cursor, 2),
        "age_end": round(age_cursor + balance_years, 2),
    })
    age_cursor += balance_years

    # Subsequent full dashas: cycle through sequence starting from next yogini
    # Repeat enough times to cover 100+ years
    seq_idx = start_idx + 1
    while age_cursor <= 100:
        yogini = YOGINI_SEQUENCE[seq_idx % 8]
        entry = {
            "yogini": yogini["yogini"],
            "planet": yogini["planet"],
            "years": yogini["years"],
            "age_start": round(age_cursor, 2),
            "age_end": round(age_cursor + yogini["years"], 2),
        }
        timeline.append(entry)
        age_cursor += yogini["years"]
        seq_idx += 1

    # Current age
    today = date.today()
    age_days = (today - profile.dob).days
    age_years = age_days / 365.25

    # Find current dasha
    current = timeline[0]
    for period in timeline:
        if period["age_start"] <= age_years < period["age_end"]:
            current = period
            break

    years_into = round(age_years - current["age_start"], 2)
    years_remaining = round(current["age_end"] - age_years, 2)

    data = {
        "birth_nakshatra": nak_num,
        "birth_nakshatra_name": NAKSHATRA_NAMES[nak_index],
        "moon_longitude": round(moon_deg, 4) if moon_deg is not None else None,
        "starting_yogini": starting["yogini"],
        "starting_planet": starting["planet"],
        "first_dasha_balance_years": round(balance_years, 3),
        "current_yogini": current["yogini"],
        "current_planet": current["planet"],
        "current_dasha_start_age": current["age_start"],
        "current_dasha_end_age": current["age_end"],
        "years_into_current": years_into,
        "years_remaining": years_remaining,
        "cycle_length_years": CYCLE_LENGTH,
        "period_quality": PLANET_QUALITY.get(current["planet"], "neutral"),
        "timeline": timeline[:15],  # Limit to first 15 periods
    }

    return SystemResult(
        id="yogini_dasha",
        name="Yogini Dasha (36-Year Vedic Cycle)",
        certainty=certainty,
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Parashara, Brihat Parashara Hora Shastra — Yogini Dasha chapter",
            "Swiss Ephemeris — Lahiri (Chitrapaksha) ayanamsa",
        ],
        question="Q4_TIMING",
    )
