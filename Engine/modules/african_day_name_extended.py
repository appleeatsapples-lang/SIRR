"""
African Day Name Extended (Multi-Tradition)
─────────────────────────────────────────────
Extends akan_kra_din with Yoruba, Igbo market-cycle, and Swahili
day-name systems.

Algorithm (from chinese_african_lookups.json):
  1. Akan: DOB weekday → male/female soul name + quality
  2. Yoruba: DOB weekday → Ojo name + meaning
  3. Igbo: JDN mod 4 → market day (Eke/Orie/Afo/Nkwo) using 1 Jan 1970 = Eke
  4. Swahili: DOB weekday → Swahili name (Arabic-derived)

Source: Akan naming tradition; Yoruba Ojo system; Igbo Izu market calendar
SOURCE_TIER: A (primary cultural practice, documented by ethnographers)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


AKAN = {
    0: {"male": "Kojo / Kwadwo", "female": "Adwoa", "quality": "peaceful, quiet"},
    1: {"male": "Kobina / Kwabena", "female": "Abenaa", "quality": "energetic, passionate"},
    2: {"male": "Kweku / Kwaku", "female": "Akua", "quality": "agile, communicative"},
    3: {"male": "Yaw", "female": "Yaa", "quality": "stubborn, principled"},
    4: {"male": "Kofi", "female": "Afua", "quality": "adventurous, magnetic"},
    5: {"male": "Kwame", "female": "Amma", "quality": "spiritual, destined"},
    6: {"male": "Kwasi", "female": "Akosua", "quality": "creative, independent"},
}

YORUBA = {
    0: {"name": "Ojo Aje", "meaning": "Day of Wealth", "english": "Monday"},
    1: {"name": "Ojo Awo", "meaning": "Day of Secrecy", "english": "Tuesday"},
    2: {"name": "Ojo Isegun", "meaning": "Day of Victory", "english": "Wednesday"},
    3: {"name": "Ojo Ojobo", "meaning": "Day of Business", "english": "Thursday"},
    4: {"name": "Ojo Eti", "meaning": "Day of Listening", "english": "Friday"},
    5: {"name": "Ojo Abameta", "meaning": "Day of Three Faces", "english": "Saturday"},
    6: {"name": "Ojo Aiku", "meaning": "Day of Immortality", "english": "Sunday"},
}

SWAHILI = {
    0: "Jumatatu",
    1: "Jumanne",
    2: "Jumatano",
    3: "Alhamisi",
    4: "Ijumaa",
    5: "Jumamosi",
    6: "Jumapili",
}

IGBO_DAYS = ["Eke", "Orie", "Afo", "Nkwo"]
IGBO_QUALITIES = {
    "Eke": "creativity, new beginnings",
    "Orie": "commerce, social connection",
    "Afo": "wisdom, spiritual reflection",
    "Nkwo": "rest, completion",
}

# JDN for epoch: 1 Jan 1970 = JDN 2440588, and that day = Eke (index 0)
IGBO_EPOCH_JDN = 2440588


def _compute_jdn(year: int, month: int, day: int) -> int:
    """Julian Day Number computation."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    weekday = profile.dob.weekday()  # 0=Monday ... 6=Sunday

    gender = profile.gender or "male"

    # Akan
    akan = AKAN.get(weekday, {})
    akan_name = akan.get(gender, akan.get("male", ""))
    akan_quality = akan.get("quality", "")

    # Yoruba
    yoruba = YORUBA.get(weekday, {})

    # Swahili
    swahili_day = SWAHILI.get(weekday, "")

    # Igbo (4-day market cycle)
    jdn = _compute_jdn(profile.dob.year, profile.dob.month, profile.dob.day)
    igbo_idx = (jdn - IGBO_EPOCH_JDN) % 4
    if igbo_idx < 0:
        igbo_idx += 4
    igbo_day = IGBO_DAYS[igbo_idx]
    igbo_quality = IGBO_QUALITIES.get(igbo_day, "")

    return SystemResult(
        id="african_day_name_extended",
        name="African Day Name Extended",
        certainty="COMPUTED_STRICT",
        data={
            "weekday_index": weekday,
            "akan_name": akan_name,
            "akan_quality": akan_quality,
            "yoruba_name": yoruba.get("name"),
            "yoruba_meaning": yoruba.get("meaning"),
            "swahili_day": swahili_day,
            "igbo_market_day": igbo_day,
            "igbo_quality": igbo_quality,
            "igbo_jdn": jdn,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Akan naming tradition", "Yoruba Ojo system",
                     "Igbo Izu market calendar", "chinese_african_lookups.json"],
        question="Q1_IDENTITY",
    )
