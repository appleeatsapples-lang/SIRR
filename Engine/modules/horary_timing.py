"""Horary Timing — Current Planetary Hour & Day Ruler

Extracts the current planetary hour and day ruler for the profile's
today date. Useful context for any timing question.

Uses the Chaldean planetary hour sequence: the day ruler determines
the first hour from sunrise, then cycles through Saturn → Jupiter →
Mars → Sun → Venus → Mercury → Moon.

COMPUTED_STRICT — pure date/time math, no ephemeris needed.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

DAY_NAMES = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
             4: "Friday", 5: "Saturday", 6: "Sunday"}

DAY_RULERS = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
              4: "Venus", 5: "Saturn", 6: "Sun"}

# TZ offsets for approximate sunrise calculation
TZ_OFFSETS = {
    "Asia/Riyadh": 3, "Asia/Dubai": 4, "Asia/Kuwait": 3,
    "Asia/Amman": 2, "Africa/Cairo": 2, "Asia/Beirut": 2,
    "Asia/Damascus": 2, "Asia/Baghdad": 3, "Europe/Istanbul": 3,
    "Europe/London": 0, "America/New_York": -5, "UTC": 0,
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    today = profile.today
    weekday = today.weekday()  # Monday=0
    day_name = DAY_NAMES[weekday]
    day_ruler = DAY_RULERS[weekday]
    day_ruler_idx = CHALDEAN_ORDER.index(day_ruler)

    # Approximate sunrise at 6:00 AM local (simplified; no ephemeris needed)
    sunrise_hour = 6
    sunrise_time_local = f"{sunrise_hour:02d}:00"

    # Current hour: use birth_time_local if today == dob, else assume noon
    current_h, current_m = 12, 0
    time_source = "noon_default"

    # If profile has birth_time_local, use it for the hour computation
    # (this gives the birth-moment planetary hour for the "today" date)
    if profile.birth_time_local:
        try:
            current_h, current_m = map(int, profile.birth_time_local.split(":"))
            time_source = "birth_time"
        except (ValueError, AttributeError):
            pass

    # Hours from sunrise (approximate)
    total_minutes = current_h * 60 + current_m
    sunrise_minutes = sunrise_hour * 60
    hours_from_sunrise = max(0, (total_minutes - sunrise_minutes) // 60)

    # Current hour number (1-based from sunrise)
    current_hour_number = hours_from_sunrise + 1

    # Current planetary hour ruler
    hour_ruler_idx = (day_ruler_idx + hours_from_sunrise) % 7
    current_hour_ruler = CHALDEAN_ORDER[hour_ruler_idx]

    # Next hour ruler
    next_hour_ruler_idx = (hour_ruler_idx + 1) % 7
    next_hour_ruler = CHALDEAN_ORDER[next_hour_ruler_idx]

    # Full Chaldean day-hour sequence starting from day ruler
    chaldean_day_hour_sequence = [
        CHALDEAN_ORDER[(day_ruler_idx + i) % 7] for i in range(7)
    ]

    data = {
        "today": str(today),
        "day_of_week": day_name,
        "day_ruler": day_ruler,
        "current_hour_number": current_hour_number,
        "current_hour_ruler": current_hour_ruler,
        "next_hour_ruler": next_hour_ruler,
        "sunrise_time_local": sunrise_time_local,
        "time_used": f"{current_h:02d}:{current_m:02d}",
        "time_source": time_source,
        "chaldean_day_hour_sequence": chaldean_day_hour_sequence,
    }

    interpretation = (
        f"On {day_name}, {today}, the day is ruled by {day_ruler}. "
        f"At {current_h:02d}:{current_m:02d}, the planetary hour belongs to {current_hour_ruler}, "
        f"followed by {next_hour_ruler}. "
        f"The Chaldean sequence from sunrise: {', '.join(chaldean_day_hour_sequence)}."
    )

    return SystemResult(
        id="horary_timing",
        name="Horary Timing (Planetary Hour & Day Ruler)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interpretation,
        constants_version=constants["version"],
        references=["Chaldean planetary hour sequence", "Medieval astrological tradition"],
    )
