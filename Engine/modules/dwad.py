"""Zodiac Dwad (Dwadashamsha) — COMPUTED_STRICT
Each sign is divided into 12 micro-signs of 2.5° each.
The dwad sign starts with the sign itself and proceeds through the zodiac.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from datetime import date

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def _approx_solar_degree(month: int, day: int) -> float:
    doy = date(2000, month, day).timetuple().tm_yday
    degree = ((doy - 80) % 365) * (360.0 / 365.25)
    if degree < 0:
        degree += 360
    return degree


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    degree = _approx_solar_degree(profile.dob.month, profile.dob.day)
    sign_index = int(degree // 30) % 12
    sign = SIGNS[sign_index]
    degree_in_sign = degree % 30

    # Dwad: each 2.5° = one micro-sign
    dwad_num = int(degree_in_sign / 2.5)  # 0-11
    dwad_sign_index = (sign_index + dwad_num) % 12
    dwad_sign = SIGNS[dwad_sign_index]

    dwad_start = dwad_num * 2.5
    dwad_end = dwad_start + 2.5

    return SystemResult(
        id="dwad",
        name="Zodiac Dwad (Dwadashamsha / 2.5° Micro-Sign)",
        certainty="COMPUTED_STRICT",
        data={
            "solar_degree_approx": round(degree, 2),
            "sun_sign": sign,
            "degree_in_sign": round(degree_in_sign, 2),
            "dwad_number": dwad_num + 1,  # 1-12 for display
            "dwad_sign": dwad_sign,
            "dwad_range": f"{dwad_start:.1f}-{dwad_end:.1f}° {sign}",
            "micro_position": f"{sign} / {dwad_sign} dwad",
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Hindu/Vedic dwadashamsha. 12 micro-divisions per sign, 2.5° each."],
        question="Q1_IDENTITY"
    )
