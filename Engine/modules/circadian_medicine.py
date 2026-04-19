"""
Circadian Medicine (Birth Hour Organ Clock)
─────────────────────────────────────────────
Maps birth hour to the Traditional Chinese Medicine organ clock
and Western chronobiology peak/trough windows.

Algorithm:
  1. Map birth hour → TCM 2-hour organ window (12 organs)
  2. Identify peak performance and vulnerability windows
  3. Map to chronotype tendency (from birth hour cluster)

Source: Huangdi Neijing (Yellow Emperor's Classic); modern chronobiology
SOURCE_TIER: A (primary TCM text) + modern scientific overlay (APPROX)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# TCM Organ Clock: 2-hour windows
ORGAN_CLOCK = {
    (3, 5): {"organ": "Lung", "element": "Metal", "quality": "distribution, breath, grief processing"},
    (5, 7): {"organ": "Large Intestine", "element": "Metal", "quality": "release, elimination, letting go"},
    (7, 9): {"organ": "Stomach", "element": "Earth", "quality": "nourishment, reception, digestion"},
    (9, 11): {"organ": "Spleen", "element": "Earth", "quality": "transformation, thought, analysis"},
    (11, 13): {"organ": "Heart", "element": "Fire", "quality": "joy, communication, circulation"},
    (13, 15): {"organ": "Small Intestine", "element": "Fire", "quality": "sorting, discernment, assimilation"},
    (15, 17): {"organ": "Bladder", "element": "Water", "quality": "storage, fear processing, reservoir"},
    (17, 19): {"organ": "Kidney", "element": "Water", "quality": "vitality, willpower, ancestral essence"},
    (19, 21): {"organ": "Pericardium", "element": "Fire", "quality": "protection, intimacy, emotional boundary"},
    (21, 23): {"organ": "Triple Burner", "element": "Fire", "quality": "thermoregulation, social harmony"},
    (23, 25): {"organ": "Gallbladder", "element": "Wood", "quality": "decision, courage, planning"},
    (1, 3): {"organ": "Liver", "element": "Wood", "quality": "detox, vision, strategic planning"},
}

# Chronotype tendencies
CHRONOTYPES = {
    "early_bird": {"hours": range(4, 8), "label": "Morning Lark", "peak_hours": "6am-10am"},
    "mid_morning": {"hours": range(8, 12), "label": "Third Bird (Morning-leaning)", "peak_hours": "9am-1pm"},
    "afternoon": {"hours": range(12, 17), "label": "Third Bird (Afternoon-leaning)", "peak_hours": "11am-3pm"},
    "evening": {"hours": range(17, 22), "label": "Night Owl", "peak_hours": "4pm-12am"},
    "night": {"hours": list(range(22, 24)) + list(range(0, 4)), "label": "Wolf (Late Night)", "peak_hours": "8pm-2am"},
}


def _parse_hour(time_str: str) -> float | None:
    """Parse HH:MM to decimal hour."""
    if not time_str:
        return None
    parts = time_str.split(":")
    try:
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        return h + m / 60.0
    except (ValueError, IndexError):
        return None


def _get_organ(hour: float) -> dict:
    """Get TCM organ for given hour."""
    h = int(hour) % 24
    for (start, end), info in ORGAN_CLOCK.items():
        if start <= end:
            if start <= h < end:
                return info
        else:  # wraps midnight
            if h >= start or h < end:
                return info
    # Midnight default
    return ORGAN_CLOCK[(23, 25)]


def _get_chronotype(hour: float) -> dict:
    """Get chronotype from birth hour."""
    h = int(hour) % 24
    for key, info in CHRONOTYPES.items():
        if h in info["hours"]:
            return {"type": key, "label": info["label"], "peak_hours": info["peak_hours"]}
    return {"type": "mid_morning", "label": "Third Bird", "peak_hours": "9am-1pm"}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    birth_hour = _parse_hour(profile.birth_time_local)
    if birth_hour is None:
        # Fallback: use solar noon approximation
        birth_hour = 12.0
        certainty = "APPROX"
        note = "Birth time unavailable — using solar noon approximation"
    else:
        certainty = "APPROX"
        note = "Birth time mapped to TCM organ clock"

    organ = _get_organ(birth_hour)
    chronotype = _get_chronotype(birth_hour)

    # Opposite organ (12 hours away) = vulnerability window
    opposite_hour = (birth_hour + 12) % 24
    opposite_organ = _get_organ(opposite_hour)

    # Season of birth → additional element
    month = profile.dob.month
    if month in (3, 4, 5):
        birth_season = "Spring"
        season_element = "Wood"
    elif month in (6, 7, 8):
        birth_season = "Summer"
        season_element = "Fire"
    elif month in (9, 10, 11):
        birth_season = "Autumn"
        season_element = "Metal"
    else:
        birth_season = "Winter"
        season_element = "Water"

    return SystemResult(
        id="circadian_medicine",
        name="Circadian Medicine (Birth Hour Organ Clock)",
        certainty=certainty,
        data={
            "birth_hour": round(birth_hour, 2),
            "birth_organ": organ.get("organ"),
            "birth_organ_element": organ.get("element"),
            "birth_organ_quality": organ.get("quality"),
            "vulnerability_organ": opposite_organ.get("organ"),
            "vulnerability_element": opposite_organ.get("element"),
            "chronotype": chronotype.get("label"),
            "chronotype_key": chronotype.get("type"),
            "peak_hours": chronotype.get("peak_hours"),
            "birth_season": birth_season,
            "season_element": season_element,
            "note": note,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Huangdi Neijing", "Modern chronobiology"],
        question="Q3_GUIDANCE",
    )
