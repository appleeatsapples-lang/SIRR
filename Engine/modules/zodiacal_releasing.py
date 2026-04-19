"""Zodiacal Releasing — Hellenistic Timing Technique — COMPUTED_STRICT
The premier Hellenistic timing system, releasing from the Lot of Fortune (material life)
and Lot of Spirit (career/purpose). Each sign is activated in zodiacal order from
the Lot's sign, with period lengths determined by the sign's planetary ruler.

Period lengths (in years) per planetary ruler:
  Sun: 19, Moon: 25, Mercury: 20, Venus: 8,
  Mars: 15, Jupiter: 12, Saturn: 27

Level 1 (major periods) use full years.
Level 2 (sub-periods) subdivide each L1 period into 12 signs proportionally
using months (total L1 years × 12 months / 12 signs, weighted by ruler).

A "loosing of the bond" occurs when the L1 period ruler is in a sign that
hands off to the next sign — a major life transition indicator.

Sources: Vettius Valens (Anthology, Book IV),
         Chris Brennan (Hellenistic Astrology)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Sign → ruling planet
SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Period length in years per ruling planet
PERIOD_YEARS = {
    "Sun": 19, "Moon": 25, "Mercury": 20, "Venus": 8,
    "Mars": 15, "Jupiter": 12, "Saturn": 27,
}


def _lot_longitude(asc: float, a: float, b: float, is_diurnal: bool) -> float:
    if is_diurnal:
        return (asc + a - b) % 360
    return (asc + b - a) % 360


def _compute_periods(start_sign_idx: int, age_years: float) -> dict:
    """Compute L1 periods from a starting sign, find current period at given age."""
    periods = []
    cumulative = 0.0

    for i in range(12):
        sign_idx = (start_sign_idx + i) % 12
        sign = SIGNS[sign_idx]
        ruler = SIGN_RULERS[sign]
        years = PERIOD_YEARS[ruler]
        periods.append({
            "sign": sign,
            "ruler": ruler,
            "years": years,
            "start_age": round(cumulative, 1),
            "end_age": round(cumulative + years, 1),
        })
        cumulative += years

    # Find current L1 period
    current_l1 = None
    current_l1_idx = 0
    age_acc = 0.0
    for idx, p in enumerate(periods):
        if age_acc + p["years"] > age_years:
            current_l1 = p
            current_l1_idx = idx
            break
        age_acc += p["years"]

    if current_l1 is None:
        # Age exceeds first 12-sign cycle — wrap
        total_cycle = sum(p["years"] for p in periods)
        wrapped_age = age_years % total_cycle
        age_acc = 0.0
        for idx, p in enumerate(periods):
            if age_acc + p["years"] > wrapped_age:
                current_l1 = p
                current_l1_idx = idx
                break
            age_acc += p["years"]

    # L2 sub-periods within current L1
    l1_years = current_l1["years"]
    years_into_l1 = age_years - current_l1["start_age"]
    l2_sub_months = l1_years * 12  # Total months in this L1 period

    # L2 sub-periods cycle through 12 signs from the L1 sign
    l1_sign_idx = SIGNS.index(current_l1["sign"])
    l2_periods = []
    l2_cumulative_months = 0.0

    for i in range(12):
        sub_sign_idx = (l1_sign_idx + i) % 12
        sub_sign = SIGNS[sub_sign_idx]
        sub_ruler = SIGN_RULERS[sub_sign]
        # Sub-period months proportional to ruler's years
        total_ruler_years = sum(PERIOD_YEARS[SIGN_RULERS[SIGNS[(l1_sign_idx + j) % 12]]] for j in range(12))
        sub_months = (PERIOD_YEARS[sub_ruler] / total_ruler_years) * l2_sub_months
        l2_periods.append({
            "sign": sub_sign,
            "ruler": sub_ruler,
            "months": round(sub_months, 1),
            "start_month": round(l2_cumulative_months, 1),
        })
        l2_cumulative_months += sub_months

    # Find current L2
    months_into_l1 = years_into_l1 * 12
    current_l2 = l2_periods[0]
    l2_acc = 0.0
    for lp in l2_periods:
        if l2_acc + lp["months"] > months_into_l1:
            current_l2 = lp
            break
        l2_acc += lp["months"]

    return {
        "periods": periods[:6],  # First 6 for compact output
        "current_l1": current_l1,
        "current_l1_index": current_l1_idx,
        "current_l2": current_l2,
        "years_into_l1": round(years_into_l1, 1),
    }


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="zodiacal_releasing", name="Zodiacal Releasing",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q4_TIMING",
        )

    planets = natal_chart_data.get("planets", {})
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    sun_lon = planets["Sun"]["longitude"]
    moon_lon = planets["Moon"]["longitude"]
    desc_lon = (asc_lon + 180) % 360
    is_diurnal = ((sun_lon - desc_lon) % 360) < 180

    fortune_lon = _lot_longitude(asc_lon, moon_lon, sun_lon, is_diurnal)
    spirit_lon = _lot_longitude(asc_lon, sun_lon, moon_lon, is_diurnal)

    fortune_sign_idx = int(fortune_lon // 30) % 12
    spirit_sign_idx = int(spirit_lon // 30) % 12

    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1
    age_years = age + (profile.today.month - profile.dob.month) / 12.0

    fortune_release = _compute_periods(fortune_sign_idx, age_years)
    spirit_release = _compute_periods(spirit_sign_idx, age_years)

    data = {
        "fortune_sign": SIGNS[fortune_sign_idx],
        "spirit_sign": SIGNS[spirit_sign_idx],
        "is_diurnal": is_diurnal,
        "fortune_release": fortune_release,
        "spirit_release": spirit_release,
        "current_fortune_l1_sign": fortune_release["current_l1"]["sign"],
        "current_fortune_l1_ruler": fortune_release["current_l1"]["ruler"],
        "current_spirit_l1_sign": spirit_release["current_l1"]["sign"],
        "current_spirit_l1_ruler": spirit_release["current_l1"]["ruler"],
    }

    return SystemResult(
        id="zodiacal_releasing",
        name="Zodiacal Releasing",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Vettius Valens, Anthology Book IV — zodiacal releasing",
            "Chris Brennan, Hellenistic Astrology — modern reconstruction",
        ],
        question="Q4_TIMING",
    )
