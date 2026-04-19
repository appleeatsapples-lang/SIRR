"""
Seasonal Psychology (Birth Season Personality Correlates)
──────────────────────────────────────────────────────────
Maps birth month/season to documented psychological correlations
from peer-reviewed research (not astrology — empirical studies).

Algorithm:
  1. Map birth month → season (Northern Hemisphere default)
  2. Look up documented personality correlates from research
  3. Map to Big Five tendencies and chronotype associations
  4. Include dopamine/serotonin seasonal variation hypothesis

Source: Xenia Gonda et al. (2016) — birth season and temperament;
        Natale & Adan (1999) — seasonality of birth and chronotype
SOURCE_TIER: A (peer-reviewed research, APPROX due to population-level stats)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Birth season personality correlates (Northern Hemisphere)
# Based on Gonda et al. (2016), Natale & Adan (1999), Chotai (2000)
SEASON_PROFILES = {
    "Spring": {
        "months": [3, 4, 5],
        "temperament_tendency": "hyperthymic",
        "description": "Higher novelty seeking, optimistic bias, tendency toward exuberance",
        "big5_lean": {"openness": "+", "extraversion": "+", "agreeableness": "=", "conscientiousness": "=", "neuroticism": "="},
        "dopamine_note": "Spring births show slightly elevated novelty-seeking scores (Chotai 2000)",
        "chronotype_tendency": "moderate_morning",
    },
    "Summer": {
        "months": [6, 7, 8],
        "temperament_tendency": "cyclothymic",
        "description": "Mood variability, rapid shifting between high and low states",
        "big5_lean": {"openness": "+", "extraversion": "+", "agreeableness": "+", "conscientiousness": "-", "neuroticism": "+"},
        "dopamine_note": "Summer births correlate with highest cyclothymic scores (Gonda 2016)",
        "chronotype_tendency": "evening",
    },
    "Autumn": {
        "months": [9, 10, 11],
        "temperament_tendency": "depressive-low",
        "description": "Lower irritability, lower tendency toward depressive temperament",
        "big5_lean": {"openness": "=", "extraversion": "-", "agreeableness": "+", "conscientiousness": "+", "neuroticism": "-"},
        "dopamine_note": "Autumn births show lowest depressive temperament scores (Gonda 2016)",
        "chronotype_tendency": "moderate_evening",
    },
    "Winter": {
        "months": [12, 1, 2],
        "temperament_tendency": "irritable-low",
        "description": "Lower irritability and cyclothymia than summer births",
        "big5_lean": {"openness": "-", "extraversion": "-", "agreeableness": "=", "conscientiousness": "+", "neuroticism": "+"},
        "dopamine_note": "Winter births show higher harm avoidance (Chotai 2000)",
        "chronotype_tendency": "morning",
    },
}

# Month-specific nuances (from multiple studies)
MONTH_NOTES = {
    1: "January: associated with higher creativity scores in some studies",
    2: "February: slightly elevated artistic temperament indicators",
    3: "March: spring equinox births — transitional, adaptable",
    4: "April: peak novelty-seeking month (Chotai 2000)",
    5: "May: highest optimism scores in spring cohort",
    6: "June: summer solstice — peak light exposure in utero",
    7: "July: highest cyclothymic scores (Gonda 2016)",
    8: "August: elevated extraversion scores",
    9: "September: equinox births — balanced light exposure profile",
    10: "October: lowest depressive temperament in autumn cohort",
    11: "November: increasing darkness — higher persistence scores",
    12: "December: winter solstice — highest harm avoidance",
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    month = profile.dob.month

    # Determine season
    season = None
    for s, data in SEASON_PROFILES.items():
        if month in data["months"]:
            season = s
            break
    if season is None:
        season = "Spring"

    sp = SEASON_PROFILES[season]
    month_note = MONTH_NOTES.get(month, "")

    # Hemisphere check (basic: latitude < 0 → flip seasons)
    latitude = getattr(profile, 'latitude', None)
    hemisphere = "Northern"
    adjusted_season = season
    if latitude is not None and latitude < 0:
        hemisphere = "Southern"
        flip = {"Spring": "Autumn", "Summer": "Winter", "Autumn": "Spring", "Winter": "Summer"}
        adjusted_season = flip.get(season, season)
        sp = SEASON_PROFILES[adjusted_season]

    return SystemResult(
        id="seasonal_psychology",
        name="Seasonal Psychology (Birth Season Correlates)",
        certainty="APPROX",
        data={
            "birth_month": month,
            "birth_season": season,
            "adjusted_season": adjusted_season,
            "hemisphere": hemisphere,
            "temperament_tendency": sp["temperament_tendency"],
            "description": sp["description"],
            "big5_lean": sp["big5_lean"],
            "dopamine_note": sp["dopamine_note"],
            "chronotype_tendency": sp["chronotype_tendency"],
            "month_note": month_note,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Gonda et al. (2016)", "Natale & Adan (1999)", "Chotai (2000)"],
        question="Q1_IDENTITY",
    )
