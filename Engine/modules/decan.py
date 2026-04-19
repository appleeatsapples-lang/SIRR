"""Decan — COMPUTED_STRICT
Each zodiac sign is divided into 3 decans of 10° each.
Computed from solar longitude (approximate from DOB).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Approximate solar longitude from DOB (tropical zodiac)
# Spring equinox ~March 20 = 0° Aries
SIGN_STARTS = [
    (3, 21), (4, 20), (5, 21), (6, 21), (7, 23), (8, 23),
    (9, 23), (10, 23), (11, 22), (12, 22), (1, 20), (2, 19),
]

# Decan rulers (Chaldean order / triplicity system)
DECAN_RULERS_CHALDEAN = {
    "Aries":       ["Mars", "Sun", "Jupiter"],
    "Taurus":      ["Venus", "Mercury", "Saturn"],
    "Gemini":      ["Mercury", "Venus", "Saturn"],
    "Cancer":      ["Moon", "Pluto/Mars", "Jupiter"],
    "Leo":         ["Sun", "Jupiter", "Mars"],
    "Virgo":       ["Mercury", "Saturn", "Venus"],
    "Libra":       ["Venus", "Saturn", "Mercury"],
    "Scorpio":     ["Pluto/Mars", "Jupiter", "Moon"],
    "Sagittarius": ["Jupiter", "Mars", "Sun"],
    "Capricorn":   ["Saturn", "Venus", "Mercury"],
    "Aquarius":    ["Saturn", "Mercury", "Venus"],
    "Pisces":      ["Jupiter", "Moon", "Pluto/Mars"],
}


def _approx_solar_degree(month, day):
    """Approximate solar longitude (0-360) from birth month/day."""
    from datetime import date
    doy = date(2000, month, day).timetuple().tm_yday
    # Spring equinox ~day 80 (March 20)
    degree = ((doy - 80) % 365) * (360.0 / 365.25)
    if degree < 0:
        degree += 360
    return degree


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    degree = _approx_solar_degree(profile.dob.month, profile.dob.day)
    sign_index = int(degree // 30) % 12
    sign = SIGNS[sign_index]
    degree_in_sign = degree % 30

    decan_num = int(degree_in_sign // 10) + 1  # 1, 2, or 3
    decan_start = (decan_num - 1) * 10
    decan_end = decan_num * 10

    rulers = DECAN_RULERS_CHALDEAN.get(sign, ["?", "?", "?"])
    ruler = rulers[decan_num - 1]

    return SystemResult(
        id="decan",
        name="Decan (10° Division)",
        certainty="COMPUTED_STRICT",
        data={
            "solar_degree_approx": round(degree, 2),
            "sign": sign,
            "degree_in_sign": round(degree_in_sign, 2),
            "decan": decan_num,
            "decan_range": f"{decan_start}-{decan_end}° {sign}",
            "decan_ruler": ruler,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Chaldean decan rulers. Solar degree approximate (±1°) from DOB."],
        question="Q1_IDENTITY"
    )
