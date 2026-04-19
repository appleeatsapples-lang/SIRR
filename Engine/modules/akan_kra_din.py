"""Akan Kra Din (Soul Day Name) — LOOKUP_FIXED
Assigns a Kra (soul/spirit) name based on birth weekday per Akan tradition (Ghana).
Source (Tier B): Meyerowitz, E.L.R. *The Akan of Ghana* (1958), Faber & Faber.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]

AKAN_TABLE = {
    0: {  # Monday
        "day_akan": "Dwowda",
        "kra_male": "Kojo",
        "kra_female": "Adwoa",
        "archetype": "Calm, peaceful",
        "traits": ["patient", "diplomatic", "reflective", "loyal"],
        "element": "Water",
    },
    1: {  # Tuesday
        "day_akan": "Benada",
        "kra_male": "Kwabena",
        "kra_female": "Abena",
        "archetype": "Bold, restless",
        "traits": ["energetic", "assertive", "courageous", "impatient"],
        "element": "Fire",
    },
    2: {  # Wednesday
        "day_akan": "Wukuada",
        "kra_male": "Kwaku",
        "kra_female": "Akua",
        "archetype": "Versatile, adaptable",
        "traits": ["communicative", "flexible", "quick-thinking", "scattered"],
        "element": "Air",
    },
    3: {  # Thursday
        "day_akan": "Yawada",
        "kra_male": "Yaw",
        "kra_female": "Yaa",
        "archetype": "Tenacious, independent",
        "traits": ["stubborn", "brave", "self-reliant", "persistent"],
        "element": "Earth",
    },
    4: {  # Friday
        "day_akan": "Fiada",
        "kra_male": "Kofi",
        "kra_female": "Afia",
        "archetype": "Restless, exploratory",
        "traits": ["wanderer", "curious", "creative", "freedom-seeking"],
        "element": "Air",
    },
    5: {  # Saturday
        "day_akan": "Memeneda",
        "kra_male": "Kwame",
        "kra_female": "Ama",
        "archetype": "Spiritually gifted, contemplative",
        "traits": ["intuitive", "spiritual", "introspective", "visionary"],
        "element": "Water",
    },
    6: {  # Sunday
        "day_akan": "Kwasida",
        "kra_male": "Kwasi",
        "kra_female": "Akosua",
        "archetype": "Priestly, leadership-oriented",
        "traits": ["authoritative", "charismatic", "generous", "dominant"],
        "element": "Fire",
    },
}


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    weekday = profile.dob.weekday()  # 0=Monday, 6=Sunday
    entry = AKAN_TABLE[weekday]
    gender = (profile.gender or "male").lower()
    kra_key = "kra_female" if gender == "female" else "kra_male"

    return SystemResult(
        id="akan_kra_din",
        name="Akan Kra Din (Soul Day Name)",
        certainty="LOOKUP_FIXED",
        data={
            "birth_weekday": weekday,
            "birth_weekday_name": WEEKDAY_NAMES[weekday],
            "day_akan": entry["day_akan"],
            "kra_name": entry[kra_key],
            "gender_used": gender,
            "archetype": entry["archetype"],
            "traits": entry["traits"],
            "element": entry["element"],
            "tradition": "Akan (Ghana)",
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Meyerowitz, E.L.R. The Akan of Ghana (1958), Faber & Faber",
            "SOURCE_TIER:B/INVESTIGATE — Akan oral tradition. Verify specific table attribution.",
        ],
        question="Q1_IDENTITY",
    )
