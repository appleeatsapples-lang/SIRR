"""Maramataka — Māori Lunar Calendar — COMPUTED_STRICT

The Maramataka is the traditional Māori lunar calendar of Aotearoa (New Zealand),
dividing the synodic month into 30 named nights. Each night carries specific
quality tags (fishing, planting, rest, harvesting, ceremony) derived from
tribal oral traditions passed through iwi (tribes) across generations.

Algorithm:
  1. Compute days since a known new moon epoch (Jan 6, 2000 18:14 UTC)
  2. lunar_day = floor(days_since_epoch % 29.53059) + 1 → 1-30
  3. Map to one of 30 Māori night-names with quality tags
  4. Compute lunar_phase_pct and Tangaroa proximity (peak fishing days)

Sources: Matariki and the Maramataka (Te Papa Tongarewa),
         Dr. Rangi Mātāmua, Matariki: Te Whetū Tapu o te Tau (2017),
         Traditional iwi calendars (Ngāi Tahu, Tainui, Ngāpuhi variants)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Reference new moon: January 6, 2000 at 18:14 UTC
# Julian Day Number for this epoch
EPOCH_JDN = 2451550.26  # JD for 2000-01-06 18:14 UTC

SYNODIC_MONTH = 29.53059  # days

# 30 Māori night-names with quality tags
# Based on composite iwi traditions (Ngāi Tahu / Tainui / Ngāpuhi)
NIGHTS = [
    ("Whiro", ["rest", "reflection"]),
    ("Tirea", ["planting", "fishing"]),
    ("Hoata", ["planting", "fishing"]),
    ("Oue", ["planting"]),
    ("Okoro", ["planting"]),
    ("Tamatea-a-ngana", ["rest", "caution"]),
    ("Tamatea-aio", ["rest", "caution"]),
    ("Tamatea-kai-ariki", ["rest", "caution"]),
    ("Tamatea-tuhaha", ["rest", "caution"]),
    ("Huna", ["planting"]),
    ("Ari-roa", ["planting", "fishing"]),
    ("Hotu", ["planting"]),
    ("Maure", ["harvesting", "fishing"]),
    ("Atua-whakahaehae", ["ceremony", "reflection"]),
    ("Turu", ["planting", "fishing"]),
    ("Rakau-nui", ["planting", "fishing", "harvesting"]),
    ("Rakau-matohi", ["planting", "fishing", "harvesting"]),
    ("Takirau", ["fishing", "harvesting"]),
    ("Oika", ["fishing"]),
    ("Korekore-te-whiwhia", ["rest"]),
    ("Korekore-te-rawea", ["rest"]),
    ("Korekore-piri-ki-Tangaroa", ["fishing", "preparation"]),
    ("Tangaroa-a-mua", ["fishing", "ceremony"]),
    ("Tangaroa-a-roto", ["fishing", "ceremony"]),
    ("Tangaroa-kiokio", ["fishing"]),
    ("Otane", ["planting", "harvesting"]),
    ("Orongonui", ["planting", "harvesting"]),
    ("Mauri", ["planting", "ceremony"]),
    ("Mutuwhenua", ["rest", "reflection"]),
    ("Tirea-whaka-mau", ["rest"]),
]

# Tangaroa nights (peak fishing) are nights 23-25 (indices 22-24)
TANGAROA_INDICES = {22, 23, 24}  # 0-based


def _jdn_from_date(year: int, month: int, day: int) -> float:
    """Compute Julian Day Number from a Gregorian date (noon)."""
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5


def _moon_phase_name(phase_pct: float) -> str:
    """Determine moon phase name from phase percentage."""
    if phase_pct < 0.0625 or phase_pct >= 0.9375:
        return "New Moon"
    elif phase_pct < 0.1875:
        return "Waxing Crescent"
    elif phase_pct < 0.3125:
        return "First Quarter"
    elif phase_pct < 0.4375:
        return "Waxing Gibbous"
    elif phase_pct < 0.5625:
        return "Full Moon"
    elif phase_pct < 0.6875:
        return "Waning Gibbous"
    elif phase_pct < 0.8125:
        return "Last Quarter"
    else:
        return "Waning Crescent"


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    birth = profile.dob
    jdn = _jdn_from_date(birth.year, birth.month, birth.day)

    # Days since reference new moon
    days_since = jdn - EPOCH_JDN
    cycle_position = days_since % SYNODIC_MONTH

    # Lunar day (1-30)
    lunar_day = int(cycle_position) + 1
    if lunar_day > 30:
        lunar_day = 30

    # Night name and quality (0-indexed)
    night_idx = lunar_day - 1
    night_name, night_quality = NIGHTS[night_idx]

    # Lunar phase percentage
    phase_pct = cycle_position / SYNODIC_MONTH
    phase_name = _moon_phase_name(phase_pct)

    # Tangaroa proximity: distance to nearest Tangaroa night (23-25)
    tangaroa_distances = [abs(night_idx - ti) for ti in TANGAROA_INDICES]
    tangaroa_proximity = min(tangaroa_distances)
    is_tangaroa = night_idx in TANGAROA_INDICES

    data = {
        "method": "maramataka_lunar_v1",
        "lunar_day": lunar_day,
        "night_name": night_name,
        "night_quality": night_quality,
        "lunar_phase_pct": round(phase_pct, 4),
        "moon_phase_name": phase_name,
        "tangaroa_proximity": tangaroa_proximity,
        "is_tangaroa_night": is_tangaroa,
    }

    return SystemResult(
        id="maramataka",
        name="Maramataka (Māori Lunar Calendar)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Dr. Rangi Mātāmua, Matariki: Te Whetū Tapu o te Tau (2017)",
            "Te Papa Tongarewa — Matariki and the Maramataka",
            "Traditional iwi calendars (Ngāi Tahu, Tainui, Ngāpuhi)",
        ],
        question="Q3_NATURE",
    )
