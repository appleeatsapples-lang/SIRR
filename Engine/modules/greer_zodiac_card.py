"""Greer Zodiac Card — LOOKUP_FIXED
Maps natal Sun sign → Major Arcana card via Golden Dawn correspondences.
Source: Greer's Tarot Profile worksheet, Golden Dawn sign-card table
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

MAJOR_ARCANA = {
    1: "The Magician", 2: "The High Priestess", 3: "The Empress",
    4: "The Emperor", 5: "The Hierophant", 6: "The Lovers",
    7: "The Chariot", 8: "Strength", 9: "The Hermit",
    10: "Wheel of Fortune", 11: "Justice", 12: "The Hanged Man",
    13: "Death", 14: "Temperance", 15: "The Devil",
    16: "The Tower", 17: "The Star", 18: "The Moon",
    19: "The Sun", 20: "Judgement", 21: "The World",
    22: "The Fool",
}

# Golden Dawn sign → Major Arcana correspondences (RWS numbering)
SIGN_TO_CARD = {
    "Aries": 4,       # The Emperor
    "Taurus": 5,      # The Hierophant
    "Gemini": 6,      # The Lovers
    "Cancer": 7,      # The Chariot
    "Leo": 8,         # Strength
    "Virgo": 9,       # The Hermit
    "Libra": 11,      # Justice
    "Scorpio": 13,    # Death
    "Sagittarius": 14, # Temperance
    "Capricorn": 15,  # The Devil
    "Aquarius": 17,   # The Star
    "Pisces": 18,     # The Moon
}

# Fallback: DOB → tropical Sun sign (approximate, boundary dates)
_SIGN_DATES = [
    (1, 20, "Aquarius"), (2, 19, "Pisces"), (3, 21, "Aries"),
    (4, 20, "Taurus"), (5, 21, "Gemini"), (6, 21, "Cancer"),
    (7, 23, "Leo"), (8, 23, "Virgo"), (9, 23, "Libra"),
    (10, 23, "Scorpio"), (11, 22, "Sagittarius"), (12, 22, "Capricorn"),
]


def _sun_sign_from_dob(dob) -> str:
    m, d = dob.month, dob.day
    for start_m, start_d, sign in _SIGN_DATES:
        if m == start_m and d >= start_d:
            return sign
        if m == start_m - 1 and d < start_d:
            # We're in the previous sign still — handled by iteration
            pass
    # Walk backward: find the sign whose start we've passed
    for i in range(len(_SIGN_DATES) - 1, -1, -1):
        sm, sd, sign = _SIGN_DATES[i]
        if (m, d) >= (sm, sd):
            return sign
    return "Capricorn"  # Dec 22+


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal_chart_data = kwargs.get("natal_chart_data")

    sun_sign = None
    source = "dob_approximate"

    if natal_chart_data and "sun_sign" in natal_chart_data:
        sun_sign = natal_chart_data["sun_sign"]
        source = "ephemeris"
    else:
        sun_sign = _sun_sign_from_dob(profile.dob)

    card_number = SIGN_TO_CARD.get(sun_sign, 0)
    card_name = MAJOR_ARCANA.get(card_number, "Unknown")

    certainty = "LOOKUP_FIXED" if source == "ephemeris" else "APPROX"

    return SystemResult(
        id="greer_zodiac_card",
        name="Greer Zodiac Card",
        certainty=certainty,
        data={
            "sun_sign": sun_sign,
            "zodiac_card_number": card_number,
            "zodiac_card_name": card_name,
            "source": source,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Golden Dawn sign-card correspondences: Aries→Emperor, ..., Pisces→Moon",
            "Greer, 'Archetypal Tarot' (2021): Zodiac Card = Sun sign → Major Arcana",
            "SOURCE_TIER:B — Golden Dawn tradition, systematized by Greer.",
        ],
        question="Q1_IDENTITY",
    )
