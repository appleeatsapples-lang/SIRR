"""Chronobiology — Seasonal + Circadian Analysis — APPROX
Maps birth date to season and birth time to circadian phase.
Approximation: circadian typing requires genetic/behavioral data.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Northern hemisphere seasons by month/day
SEASONS = [
    ((3, 20), (6, 20), "spring", "الربيع"),
    ((6, 21), (9, 22), "summer", "الصيف"),
    ((9, 23), (12, 20), "autumn", "الخريف"),
    ((12, 21), (3, 19), "winter", "الشتاء"),
]

# Circadian phases by hour
CIRCADIAN_PHASES = [
    (0, 4, "deep_sleep", "Core body temperature minimum, melatonin peak"),
    (4, 6, "pre_dawn", "Cortisol surge begins, body warming"),
    (6, 9, "early_morning", "Cortisol peak, alertness rising, testosterone peak"),
    (9, 12, "late_morning", "Peak cognitive function, working memory optimal"),
    (12, 14, "midday", "Post-prandial dip, circadian alertness trough"),
    (14, 17, "afternoon", "Cardiovascular efficiency peak, muscle strength peak"),
    (17, 19, "early_evening", "Body temperature peak, reaction time optimal"),
    (19, 21, "evening", "Melatonin onset, body cooling begins"),
    (21, 24, "night", "Deep sleep pressure building, growth hormone surge"),
]

# Seasonal chronotypes (research-based tendencies)
SEASONAL_CHRONOTYPE = {
    "spring": {"tendency": "intermediate", "light_exposure": "increasing", "energy": "rising"},
    "summer": {"tendency": "early", "light_exposure": "maximum", "energy": "peak"},
    "autumn": {"tendency": "intermediate", "light_exposure": "decreasing", "energy": "consolidating"},
    "winter": {"tendency": "late", "light_exposure": "minimum", "energy": "conserving"},
}


def _get_season(month: int, day: int) -> tuple[str, str]:
    md = (month, day)
    if (3, 20) <= md <= (6, 20):
        return "spring", "الربيع"
    elif (6, 21) <= md <= (9, 22):
        return "summer", "الصيف"
    elif (9, 23) <= md <= (12, 20):
        return "autumn", "الخريف"
    else:
        return "winter", "الشتاء"


def _get_circadian_phase(hour: float) -> dict:
    for start, end, phase, desc in CIRCADIAN_PHASES:
        if start <= hour < end:
            return {"phase": phase, "description": desc}
    return {"phase": "night", "description": "Deep sleep pressure building"}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    season, season_ar = _get_season(profile.dob.month, profile.dob.day)
    seasonal_data = SEASONAL_CHRONOTYPE[season]

    # Birth time analysis
    birth_hour = None
    circadian = {"phase": "unknown", "description": "Birth time not provided"}
    if profile.birth_time_local:
        parts = profile.birth_time_local.split(":")
        birth_hour = int(parts[0]) + int(parts[1]) / 60
        circadian = _get_circadian_phase(birth_hour)

    # Day of year (position in annual cycle)
    doy = profile.dob.timetuple().tm_yday
    annual_position = round(doy / 365 * 100, 1)

    # Equinox/solstice proximity
    cardinal_days = {
        "vernal_equinox": 80, "summer_solstice": 172,
        "autumnal_equinox": 266, "winter_solstice": 356
    }
    nearest_cardinal = min(cardinal_days, key=lambda k: abs(cardinal_days[k] - doy))
    cardinal_distance = abs(cardinal_days[nearest_cardinal] - doy)

    return SystemResult(
        id="chronobiology",
        name="Chronobiology (الأحياء الزمنية)",
        certainty="APPROX",
        data={
            "module_class": "primary",
            "birth_season": season,
            "birth_season_ar": season_ar,
            "seasonal_chronotype": seasonal_data["tendency"],
            "seasonal_energy": seasonal_data["energy"],
            "light_exposure": seasonal_data["light_exposure"],
            "circadian_phase": circadian["phase"],
            "circadian_description": circadian["description"],
            "birth_hour": birth_hour,
            "day_of_year": doy,
            "annual_position_pct": annual_position,
            "nearest_cardinal_point": nearest_cardinal,
            "cardinal_distance_days": cardinal_distance,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Chronobiology — seasonal birth effects on circadian tendency",
            "Circadian rhythm phases — cortisol/melatonin cycles",
        ],
        question="Q4_TIMING"
    )
