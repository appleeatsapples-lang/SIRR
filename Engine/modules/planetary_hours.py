"""Planetary Hours — COMPUTED_STRICT
Each day is ruled by a planet (Day Ruler), and each hour of the day
is ruled by a planet in Chaldean order. Birth hour → planetary ruler.
Uses approximate sunrise at 6:00 AM for simplicity (no location needed).
Source: Medieval astrological tradition, Agrippa
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
DAY_RULERS = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
              4: "Venus", 5: "Saturn", 6: "Sun"}  # Mon=0..Sun=6

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    # Day ruler from weekday
    weekday = profile.dob.weekday()  # Mon=0..Sun=6
    day_ruler = DAY_RULERS[weekday]
    day_ruler_idx = CHALDEAN_ORDER.index(day_ruler)

    # Birth hour (approximate: assume sunrise 6:00 AM)
    hour = 10  # default fallback
    if profile.birth_time_local:
        parts = profile.birth_time_local.split(":")
        hour = int(parts[0])

    # Planetary hour: each hour from sunrise cycles through Chaldean order
    # Hour 1 of the day = day ruler, then cycle
    hours_from_sunrise = (hour - 6) % 24
    hour_ruler_idx = (day_ruler_idx + hours_from_sunrise) % 7
    hour_ruler = CHALDEAN_ORDER[hour_ruler_idx]

    return SystemResult(
        id="planetary_hours", name="Planetary Hours",
        certainty="COMPUTED_STRICT",
        data={
            "birth_weekday": weekday,
            "day_ruler": day_ruler,
            "birth_hour": hour,
            "hours_from_sunrise": hours_from_sunrise,
            "hour_ruler": hour_ruler,
        },
        interpretation=None, constants_version=constants["version"],
        references=["Chaldean planetary hour sequence, sunrise ≈ 6:00 AM approximation"],
        question="Q3_TIMING"
    )
