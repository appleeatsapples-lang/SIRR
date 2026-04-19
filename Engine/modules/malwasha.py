"""Mandaean Malwasha (Zodiacal Baptismal Name Oracle) — LOOKUP_FIXED

From the Sfar Malwašia (Book of the Zodiac), the priest assigns a protective
spirit-name at baptism based on the birth sign, birth hour, and mother's name.
The matrilineal axis is central to Mandaean identity — nasab runs through the
mother, not the father. This module implements a deterministic approximation
of the priestly procedure using the Drower translation (1949).

Sources:
  - Drower, E.S. "The Mandaeans of Iraq and Iran" (1937)
  - Sfar Malwasia, Royal Asiatic Society MS DC 31 (1949)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Tropical zodiac signs (Western month mapping)
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Mandaean names for the 12 signs (from Sfar Malwasia)
MANDAEAN_SIGNS = [
    "Nuna", "Tawra", "Silmania", "Sartana", "Aria", "Shumbulta",
    "Qaina", "Arqba", "Hisya", "Gadya", "Daula", "Nuna-Hira",
]

# Month number → zodiac sign index (0-based, Aries=0)
MONTH_TO_SIGN_INDEX = {
    1: 9, 2: 10, 3: 11, 4: 0, 5: 1, 6: 2,
    7: 3, 8: 4, 9: 5, 10: 6, 11: 7, 12: 8,
}

# Final value (1–12) → protective Mandaean spirit-name
PROTECTIVE_NAMES = {
    1: "Yahia", 2: "Zahrun", 3: "Hibil", 4: "Shitil",
    5: "Anush", 6: "Manda", 7: "Shum", 8: "Ram",
    9: "Nbu", 10: "Dinanukht", 11: "Bihram", 12: "Shislam",
}


def _parse_birth_hour(profile: InputProfile) -> int:
    """Extract hour (0–23) from birth_time_local, default 12 if absent."""
    if profile.birth_time_local:
        try:
            return int(profile.birth_time_local.split(":")[0])
        except (ValueError, IndexError):
            pass
    return 12


def _mother_value(mother_name: str) -> int:
    """Sum of character ordinal positions mod 12 + 1.
    Deterministic substitute for the priest's lookup table."""
    if not mother_name or mother_name == "UNKNOWN":
        return 6  # median default
    char_sum = sum(ord(c) for c in mother_name if c != " ")
    return (char_sum % 12) + 1


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    # Step 1: Birth month → Mandaean zodiac sign
    birth_month = profile.dob.month
    birth_sign_index = MONTH_TO_SIGN_INDEX[birth_month]
    birth_sign = ZODIAC_SIGNS[birth_sign_index]
    birth_sign_mandaean = MANDAEAN_SIGNS[birth_sign_index]
    birth_sign_value = birth_sign_index + 1  # 1–12

    # Step 2: Count forward by birth hour
    birth_hour = _parse_birth_hour(profile)
    result_sign_index = (birth_sign_index + birth_hour) % 12
    result_sign = ZODIAC_SIGNS[result_sign_index]
    result_sign_mandaean = MANDAEAN_SIGNS[result_sign_index]
    result_value = result_sign_index + 1

    # Step 3: Mother's name value
    mother_name = profile.mother_name or "UNKNOWN"
    m_value = _mother_value(mother_name)

    # Step 4: Final value
    final_value = ((result_value - m_value) % 12) + 1

    # Step 5: Protective name
    protective_name = PROTECTIVE_NAMES[final_value]

    # Full baptismal title (matrilineal: bar/bint + mother)
    gender_link = "bar" if profile.gender != "female" else "bint"
    full_title = f"{protective_name} {gender_link} {mother_name}"

    return SystemResult(
        id="malwasha",
        name="Mandaean Malwasha (Baptismal Name Oracle)",
        certainty="LOOKUP_FIXED",
        data={
            "birth_sign": birth_sign,
            "birth_sign_mandaean": birth_sign_mandaean,
            "birth_sign_value": birth_sign_value,
            "birth_hour": birth_hour,
            "result_sign": result_sign,
            "result_sign_mandaean": result_sign_mandaean,
            "result_value": result_value,
            "mother_name": mother_name,
            "mother_value": m_value,
            "final_value": final_value,
            "protective_name": protective_name,
            "full_title": full_title,
            "matrilineal_axis": True,
        },
        interpretation=f"Baptismal spirit-name: {protective_name} — from {birth_sign_mandaean} sign, hour {birth_hour}, matrilineal axis via {mother_name}.",
        constants_version=constants["version"],
        references=[
            "Drower, E.S. The Mandaeans of Iraq and Iran (1937)",
            "Sfar Malwasia, Royal Asiatic Society MS DC 31 (1949)",
        ],
        question="Q1_IDENTITY",
    )
