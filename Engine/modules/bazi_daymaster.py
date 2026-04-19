"""BaZi Day Master Strength (日主强弱) — COMPUTED_STRICT
Classifies the Day Master as STRONG, WEAK, or SPECIAL based on seasonal
strength and support/drain counts across all pillars.

Algorithm:
1. Day Master element = Heavenly Stem of Day Pillar
2. Seasonal strength from Month Branch element
3. Count supporting vs draining elements across all 8 characters
4. Classify: STRONG if seasonal + ≥2 support, WEAK if seasonal weak + <2 support,
   SPECIAL "Follow the Leader" if zero support and 90%+ one other element

Sources: Zi Ping Zhen Quan; San Ming Tong Hui
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Five Element production cycle: producer → produced
PRODUCES = {
    "Wood": "Fire", "Fire": "Earth", "Earth": "Metal",
    "Metal": "Water", "Water": "Wood"
}

# Reverse: what produces this element
PRODUCED_BY = {v: k for k, v in PRODUCES.items()}

# Five Element control cycle: controller → controlled
CONTROLS = {
    "Wood": "Earth", "Fire": "Metal", "Earth": "Water",
    "Metal": "Wood", "Water": "Fire"
}

# Branch animal → season element mapping for seasonal strength
SEASON_ELEMENT = {
    "Tiger": "Wood", "Rabbit": "Wood",
    "Snake": "Fire", "Horse": "Fire",
    "Monkey": "Metal", "Rooster": "Metal",
    "Pig": "Water", "Rat": "Water",
    "Ox": "Earth", "Dragon": "Earth", "Goat": "Earth", "Dog": "Earth",
}


def _seasonal_strength(dm_element: str, month_animal: str) -> str:
    """Determine seasonal strength of Day Master from Month Branch."""
    season_el = SEASON_ELEMENT.get(month_animal, "Earth")
    if season_el == dm_element:
        return "PROSPEROUS"
    if PRODUCED_BY.get(dm_element) == season_el:
        return "SUPPORTED"
    if PRODUCES.get(dm_element) == season_el:
        return "EXHAUSTED"
    if CONTROLS.get(dm_element) == season_el:
        return "CONTROLLED"
    # season_el controls dm_element
    return "CONSTRAINED"


def _is_supporting(element: str, dm_element: str) -> bool:
    """Is this element supporting the Day Master? (same element or resource)"""
    if element == dm_element:
        return True
    if PRODUCED_BY.get(dm_element) == element:
        return True
    return False


def compute(profile: InputProfile, constants: dict, bazi_data: dict = None) -> SystemResult:
    if bazi_data is None:
        return SystemResult(
            id="bazi_daymaster",
            name="BaZi Day Master Strength (日主强弱)",
            certainty="NEEDS_INPUT",
            data={"error": "bazi_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY"
        )

    # Extract Day Master element from day pillar stem
    dm_element = bazi_data["day_pillar"]["stem_element"]
    dm_stem = bazi_data["day_pillar"]["stem"]
    dm_polarity = bazi_data["day_pillar"]["stem_polarity"]

    # Month branch animal for seasonal strength
    month_animal = bazi_data["month_pillar"]["animal"]
    seasonal = _seasonal_strength(dm_element, month_animal)

    # Collect all elements from stems and branches across pillars
    all_elements = []
    pillar_names = ["year_pillar", "month_pillar", "day_pillar"]
    if "hour_pillar" in bazi_data:
        pillar_names.append("hour_pillar")

    for pname in pillar_names:
        p = bazi_data[pname]
        all_elements.append(p["stem_element"])
        all_elements.append(p["branch_element"])

    # Count support vs drain (exclude Day Master stem itself from count)
    support_count = 0
    drain_count = 0
    for i, el in enumerate(all_elements):
        if i == 4:  # Day stem (index 4 = day_pillar stem) — skip self
            continue
        if _is_supporting(el, dm_element):
            support_count += 1
        else:
            drain_count += 1

    total_chars = len(all_elements) - 1  # minus self

    # Classify
    is_seasonal_strong = seasonal in ("PROSPEROUS", "SUPPORTED")

    # Check for SPECIAL "Follow the Leader" pattern
    if support_count == 0 and total_chars > 0:
        # Count dominant element
        element_counts = {}
        for i, el in enumerate(all_elements):
            if i == 4:
                continue
            element_counts[el] = element_counts.get(el, 0) + 1
        max_el = max(element_counts, key=element_counts.get)
        if element_counts[max_el] / total_chars >= 0.9:
            classification = "SPECIAL"
            special_note = f"Follow the Leader: {max_el} dominates ({element_counts[max_el]}/{total_chars})"
        else:
            classification = "WEAK"
            special_note = None
    elif is_seasonal_strong and support_count >= 2:
        classification = "STRONG"
        special_note = None
    elif not is_seasonal_strong and support_count < 2:
        classification = "WEAK"
        special_note = None
    else:
        # Borderline — use support ratio
        if support_count >= drain_count:
            classification = "STRONG"
        else:
            classification = "WEAK"
        special_note = None

    data = {
        "day_master_stem": dm_stem,
        "day_master_element": dm_element,
        "day_master_polarity": dm_polarity,
        "month_animal": month_animal,
        "seasonal_strength": seasonal,
        "support_count": support_count,
        "drain_count": drain_count,
        "classification": classification,
    }
    if special_note:
        data["special_note"] = special_note

    return SystemResult(
        id="bazi_daymaster",
        name="BaZi Day Master Strength (日主强弱)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=["Zi Ping Zhen Quan", "San Ming Tong Hui"],
        question="Q1_IDENTITY"
    )
