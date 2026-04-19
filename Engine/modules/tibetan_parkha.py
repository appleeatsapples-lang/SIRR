"""Tibetan Parkha — COMPUTED_STRICT
Compute age (Current Year - Birth Year + 1). Males start at Li, progress clockwise
through 8 trigrams. Females start at Kham, progress counter-clockwise. Modulo 8.
Source: Cornu, Philippe. "Tibetan Astrology", Shambhala, p.112
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# 8 Parkha trigrams with associations
PARKHA = [
    {"name": "Li", "element": "Fire", "direction": "South", "quality": "Brilliance"},
    {"name": "Khon", "element": "Earth", "direction": "Southwest", "quality": "Receptivity"},
    {"name": "Dwa", "element": "Metal", "direction": "West", "quality": "Joyousness"},
    {"name": "Khen", "element": "Metal", "direction": "Northwest", "quality": "Creativity"},
    {"name": "Kham", "element": "Water", "direction": "North", "quality": "Depth"},
    {"name": "Gin", "element": "Earth", "direction": "Northeast", "quality": "Stillness"},
    {"name": "Zin", "element": "Wood", "direction": "East", "quality": "Arousing"},
    {"name": "Zon", "element": "Wood", "direction": "Southeast", "quality": "Gentleness"},
]


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    gender = profile.gender

    if not gender:
        return SystemResult(
            id="tibetan_parkha", name="Tibetan Parkha",
            certainty="NEEDS_INPUT",
            data={"note": "Requires gender field in profile (male/female)"},
            interpretation=None, constants_version=constants["version"],
            references=["Cornu, 'Tibetan Astrology', Shambhala, p.112"],
            question="Q1_IDENTITY",
        )

    # Tibetan age = current year - birth year + 1
    tibetan_age = profile.today.year - profile.dob.year + 1

    if gender.lower() == "male":
        # Males: start at Li (index 0), progress clockwise (forward)
        idx = (tibetan_age - 1) % 8
    else:
        # Females: start at Kham (index 4), progress counter-clockwise (backward)
        idx = (4 - (tibetan_age - 1)) % 8

    parkha = PARKHA[idx]

    return SystemResult(
        id="tibetan_parkha",
        name="Tibetan Parkha",
        certainty="COMPUTED_STRICT",
        data={
            "tibetan_age": tibetan_age,
            "gender": gender,
            "parkha_name": parkha["name"],
            "parkha_element": parkha["element"],
            "parkha_direction": parkha["direction"],
            "parkha_quality": parkha["quality"],
            "parkha_index": idx,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Cornu, Philippe. 'Tibetan Astrology', Shambhala, p.112",
            "SOURCE_TIER:B — Scholarly translation of Tibetan astrological tradition.",
        ],
        question="Q1_IDENTITY",
    )
