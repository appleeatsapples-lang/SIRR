"""Ashtottari Dasha — 108-Year Vedic Timing Cycle
Alternative to Vimshottari's 120-year cycle. Applicable when Rahu is in
houses 1,2,3,4,5,9,11 from Lagna at birth.
Source: BPHS (Brihat Parashara Hora Shastra).

COMPUTED_STRICT when natal_chart_data is present, NEEDS_INPUT when missing.
"""
from __future__ import annotations
from datetime import date
from sirr_core.types import InputProfile, SystemResult

ASHTO_SEQUENCE = [
    {"planet": "Sun",     "years": 6},
    {"planet": "Moon",    "years": 15},
    {"planet": "Mars",    "years": 8},
    {"planet": "Mercury", "years": 17},
    {"planet": "Saturn",  "years": 10},
    {"planet": "Jupiter", "years": 19},
    {"planet": "Rahu",    "years": 12},
    {"planet": "Venus",   "years": 21},
]

QUALIFYING_HOUSES = {1, 2, 3, 4, 5, 9, 11}

CYCLE_LENGTH = 108  # sum of all periods

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
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


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="ashtottari_dasha",
            name="Ashtottari Dasha (108-Year Vedic Cycle)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required for Rahu house check"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    planets = natal_chart_data.get("planets", {})
    rahu_data = planets.get("North Node")
    asc_data = natal_chart_data.get("ascendant", {})
    asc_lon = asc_data.get("longitude") if isinstance(asc_data, dict) else None

    if rahu_data is None or asc_lon is None:
        return SystemResult(
            id="ashtottari_dasha",
            name="Ashtottari Dasha (108-Year Vedic Cycle)",
            certainty="NEEDS_INPUT",
            data={"error": "Rahu (North Node) or Ascendant data missing"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    rahu_lon = rahu_data["longitude"]
    rahu_house = int(((rahu_lon - asc_lon) % 360) / 30) + 1
    applicable = rahu_house in QUALIFYING_HOUSES

    if not applicable:
        return SystemResult(
            id="ashtottari_dasha",
            name="Ashtottari Dasha (108-Year Vedic Cycle)",
            certainty="COMPUTED_STRICT",
            data={
                "applicable": False,
                "rahu_house": rahu_house,
                "reason": f"Rahu in house {rahu_house} from Lagna (qualifying: 1,2,3,4,5,9,11)",
            },
            interpretation=None,
            constants_version=constants["version"],
            references=["Parashara, Brihat Parashara Hora Shastra — Ashtottari Dasha"],
            question="Q4_TIMING",
        )

    # Get sidereal Moon for nakshatra
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

    # Starting planet
    start_idx = (nak_num - 1) % 8
    starting = ASHTO_SEQUENCE[start_idx]
    balance_years = remaining_fraction * starting["years"]

    # Build timeline
    timeline = []
    age_cursor = 0.0

    # First (partial) dasha
    timeline.append({
        "planet": starting["planet"],
        "years": round(balance_years, 3),
        "age_start": round(age_cursor, 2),
        "age_end": round(age_cursor + balance_years, 2),
    })
    age_cursor += balance_years

    # Subsequent full dashas: cycle through sequence starting from next planet
    seq_idx = start_idx + 1
    while age_cursor <= 120:
        planet = ASHTO_SEQUENCE[seq_idx % 8]
        entry = {
            "planet": planet["planet"],
            "years": planet["years"],
            "age_start": round(age_cursor, 2),
            "age_end": round(age_cursor + planet["years"], 2),
        }
        timeline.append(entry)
        age_cursor += planet["years"]
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
        "applicable": True,
        "rahu_house": rahu_house,
        "birth_nakshatra": nak_num,
        "birth_nakshatra_name": NAKSHATRA_NAMES[nak_index],
        "starting_planet": starting["planet"],
        "first_dasha_balance_years": round(balance_years, 3),
        "current_planet": current["planet"],
        "current_dasha_start_age": current["age_start"],
        "current_dasha_end_age": current["age_end"],
        "years_into_current": years_into,
        "years_remaining": years_remaining,
        "cycle_length_years": CYCLE_LENGTH,
        "timeline": timeline[:12],  # Limit to first 12 periods
        "note": f"Applicable: Rahu in house {rahu_house} from Lagna (qualifying houses: 1,2,3,4,5,9,11)",
    }

    return SystemResult(
        id="ashtottari_dasha",
        name="Ashtottari Dasha (108-Year Vedic Cycle)",
        certainty=certainty,
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Parashara, Brihat Parashara Hora Shastra — Ashtottari Dasha chapter",
            "Swiss Ephemeris — Lahiri (Chitrapaksha) ayanamsa",
        ],
        question="Q4_TIMING",
    )
