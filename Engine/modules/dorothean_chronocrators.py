"""Dorothean Chronocrators — Life-Period Triplicity Rulers — COMPUTED_STRICT
Divides life into three major periods governed by the triplicity rulers of the
Sun's sign (in a day chart) or Moon's sign (in a night chart), following
Dorotheus of Sidon.

The three chronocrators are:
  1st period (youth/foundation): Day triplicity ruler
  2nd period (middle/maturity):  Night triplicity ruler
  3rd period (final/wisdom):     Participating triplicity ruler

Period boundaries follow the traditional Dorothean scheme where the total
lifespan is divided into approximate thirds, but the precise boundaries
are adjusted by the planetary period lengths of the rulers.

The chronocrator's natal condition (dignified, debilitated, sect status)
describes the quality of that life period.

Sources: Dorotheus of Sidon (Carmen Astrologicum),
         Vettius Valens (Anthology), Al-Biruni
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_ELEMENTS = {
    "Aries": "Fire", "Taurus": "Earth", "Gemini": "Air", "Cancer": "Water",
    "Leo": "Fire", "Virgo": "Earth", "Libra": "Air", "Scorpio": "Water",
    "Sagittarius": "Fire", "Capricorn": "Earth", "Aquarius": "Air", "Pisces": "Water",
}

# Dorothean triplicity rulers
TRIPLICITY = {
    "Fire":  {"day": "Sun",    "night": "Jupiter", "participating": "Saturn"},
    "Earth": {"day": "Venus",  "night": "Moon",    "participating": "Mars"},
    "Air":   {"day": "Saturn", "night": "Mercury", "participating": "Jupiter"},
    "Water": {"day": "Venus",  "night": "Mars",    "participating": "Moon"},
}

# Period lengths associated with each planet (Firmicus Maternus / Valens)
PLANET_PERIOD = {
    "Sun": 19, "Moon": 25, "Mercury": 20, "Venus": 8,
    "Mars": 15, "Jupiter": 12, "Saturn": 30,
}

DOMICILE = {
    "Sun": ["Leo"], "Moon": ["Cancer"],
    "Mercury": ["Gemini", "Virgo"], "Venus": ["Taurus", "Libra"],
    "Mars": ["Aries", "Scorpio"], "Jupiter": ["Sagittarius", "Pisces"],
    "Saturn": ["Capricorn", "Aquarius"],
}

EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo",
    "Venus": "Pisces", "Mars": "Capricorn", "Jupiter": "Cancer",
    "Saturn": "Libra",
}


def _condition(planet: str, sign: str) -> str:
    if sign in DOMICILE.get(planet, []):
        return "domicile"
    if EXALTATION.get(planet) == sign:
        return "exaltation"
    return "peregrine"


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="dorothean_chronocrators", name="Dorothean Chronocrators",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q4_TIMING",
        )

    planets = natal_chart_data.get("planets", {})
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    sun_lon = planets["Sun"]["longitude"]
    desc_lon = (asc_lon + 180) % 360
    is_diurnal = ((sun_lon - desc_lon) % 360) < 180

    # Sect light: Sun for day, Moon for night
    sect_light = "Sun" if is_diurnal else "Moon"
    sect_sign = planets[sect_light]["sign"]
    element = SIGN_ELEMENTS[sect_sign]
    trip = TRIPLICITY[element]

    rulers = [
        ("first",  trip["day"],           "youth/foundation"),
        ("second", trip["night"],         "middle/maturity"),
        ("third",  trip["participating"], "final/wisdom"),
    ]

    # Compute period boundaries using planetary periods
    total_years = sum(PLANET_PERIOD.get(r[1], 25) for r in rulers)
    periods = []
    cumulative = 0.0

    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1

    current_period = None
    current_ruler = None

    for label, ruler, meaning in rulers:
        years = PLANET_PERIOD.get(ruler, 25)
        start = cumulative
        end = cumulative + years
        natal_sign = planets[ruler]["sign"] if ruler in planets else "?"
        cond = _condition(ruler, natal_sign) if ruler in planets else "unknown"

        period = {
            "period": label,
            "ruler": ruler,
            "meaning": meaning,
            "years": years,
            "start_age": round(start, 0),
            "end_age": round(end, 0),
            "natal_sign": natal_sign,
            "natal_condition": cond,
        }
        periods.append(period)

        if start <= age < end:
            current_period = label
            current_ruler = ruler

        cumulative += years

    if current_period is None:
        current_period = "third"
        current_ruler = rulers[2][1]

    data = {
        "sect_light": sect_light,
        "sect_sign": sect_sign,
        "element": element,
        "is_diurnal": is_diurnal,
        "periods": periods,
        "current_period": current_period,
        "current_ruler": current_ruler,
        "total_years": total_years,
    }

    return SystemResult(
        id="dorothean_chronocrators",
        name="Dorothean Chronocrators",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Dorotheus of Sidon, Carmen Astrologicum — triplicity chronocrators",
            "Vettius Valens, Anthology — life-period rulers",
            "Al-Biruni, The Book of Instruction — triplicity period lengths",
        ],
        question="Q4_TIMING",
    )
