"""Day of Week Ruler — COMPUTED_STRICT
Classical planetary ruler of the birth weekday.
Monday=Moon, Tuesday=Mars, Wednesday=Mercury, Thursday=Jupiter,
Friday=Venus, Saturday=Saturn, Sunday=Sun.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Classical Chaldean planetary day rulers (Monday=0 in Python weekday())
DAY_RULERS = {
    0: ("Monday", "Moon", "☽"),
    1: ("Tuesday", "Mars", "♂"),
    2: ("Wednesday", "Mercury", "☿"),
    3: ("Thursday", "Jupiter", "♃"),
    4: ("Friday", "Venus", "♀"),
    5: ("Saturday", "Saturn", "♄"),
    6: ("Sunday", "Sun", "☉"),
}

DAY_QUALITIES = {
    "Moon":    {"element": "Water", "mode": "receptive", "theme": "emotion, intuition, nurturing"},
    "Mars":    {"element": "Fire", "mode": "active", "theme": "drive, courage, conflict"},
    "Mercury": {"element": "Air", "mode": "mutable", "theme": "communication, intellect, commerce"},
    "Jupiter": {"element": "Fire", "mode": "expansive", "theme": "growth, wisdom, abundance"},
    "Venus":   {"element": "Earth/Water", "mode": "receptive", "theme": "love, beauty, harmony"},
    "Saturn":  {"element": "Earth", "mode": "restrictive", "theme": "discipline, structure, mastery"},
    "Sun":     {"element": "Fire", "mode": "active", "theme": "vitality, authority, self-expression"},
}


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    weekday = profile.dob.weekday()  # Monday=0 ... Sunday=6
    day_name, ruler, glyph = DAY_RULERS[weekday]
    qualities = DAY_QUALITIES[ruler]

    return SystemResult(
        id="day_ruler",
        name="Day of Week Planetary Ruler",
        certainty="COMPUTED_STRICT",
        data={
            "birth_weekday": day_name,
            "planetary_ruler": ruler,
            "glyph": glyph,
            "element": qualities["element"],
            "mode": qualities["mode"],
            "theme": qualities["theme"],
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Classical Chaldean planetary day rulership."],
        question="Q3_NATURE"
    )
