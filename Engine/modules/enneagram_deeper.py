"""
Enneagram Deeper Analysis (META)
──────────────────────────────────
Extends enneagram_dob with wing, growth/stress directions, instinctual
variant from DOB, and tritypes.

Class C / META — derives from enneagram_dob + core numbers.

Algorithm:
  1. Get Enneagram type from enneagram_dob module
  2. Adjacent types = wings (e.g., Type 4 → wings 3 and 5)
  3. Integration (growth) and disintegration (stress) arrows
  4. Instinctual variant approximation from life_path modulus
  5. Tritype from LP + expression + soul_urge mapped to head/heart/body centers

Source: Oscar Ichazo (Arica); Claudio Naranjo; Don Riso & Russ Hudson
SOURCE_TIER: C (community tradition, no classical lineage)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Integration (growth) and Disintegration (stress) arrows
INTEGRATION = {1: 7, 2: 4, 3: 6, 4: 1, 5: 8, 6: 9, 7: 5, 8: 2, 9: 3}
DISINTEGRATION = {1: 4, 2: 8, 3: 9, 4: 2, 5: 7, 6: 3, 7: 1, 8: 5, 9: 6}

TYPE_NAMES = {
    1: "The Reformer", 2: "The Helper", 3: "The Achiever",
    4: "The Individualist", 5: "The Investigator", 6: "The Loyalist",
    7: "The Enthusiast", 8: "The Challenger", 9: "The Peacemaker",
}

# Centers: Body (8,9,1), Heart (2,3,4), Head (5,6,7)
CENTERS = {
    "Body": {8, 9, 1},
    "Heart": {2, 3, 4},
    "Head": {5, 6, 7},
}

INSTINCTUAL_VARIANTS = ["Self-Preservation (SP)", "Social (SO)", "Sexual/One-to-One (SX)"]

HARMONIC_GROUPS = {
    "Positive Outlook": {2, 7, 9},
    "Competency": {1, 3, 5},
    "Reactive": {4, 6, 8},
}

HORNEVIAN_GROUPS = {
    "Assertive": {3, 7, 8},
    "Compliant": {1, 2, 6},
    "Withdrawn": {4, 5, 9},
}


def _reduce_to_ennea(n: int) -> int:
    """Reduce to 1-9 for Enneagram (no master numbers)."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n if n >= 1 else 9


def _get_center(t: int) -> str:
    for center, types in CENTERS.items():
        if t in types:
            return center
    return "Unknown"


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    # Get base Enneagram type
    all_results = kwargs.get("all_results", [])
    base_type = None
    for r in all_results:
        if r.id == "enneagram_dob" and r.data:
            base_type = r.data.get("enneagram_type")
            break

    if base_type is None:
        # Fallback: compute from DOB digits
        dob = profile.dob
        digit_sum = sum(int(d) for d in f"{dob.year}{dob.month:02d}{dob.day:02d}")
        base_type = _reduce_to_ennea(digit_sum)

    # Wings (adjacent types on enneagram circle)
    wing_a = base_type - 1 if base_type > 1 else 9
    wing_b = base_type + 1 if base_type < 9 else 1

    # Growth and stress directions
    growth = INTEGRATION.get(base_type)
    stress = DISINTEGRATION.get(base_type)

    # Instinctual variant from life_path modulus
    lp = profile.life_path or 1
    iv_idx = (lp - 1) % 3
    instinctual = INSTINCTUAL_VARIANTS[iv_idx]

    # Tritype: one type from each center
    # Body type from birthday_number, Heart from soul_urge, Head from expression
    body_raw = _reduce_to_ennea(profile.birthday_number or profile.dob.day)
    body_type = body_raw if body_raw in CENTERS["Body"] else (1 if body_raw <= 3 else 9 if body_raw <= 6 else 8)

    heart_raw = _reduce_to_ennea(profile.soul_urge or 1)
    heart_type = heart_raw if heart_raw in CENTERS["Heart"] else (2 if heart_raw <= 3 else 3 if heart_raw <= 6 else 4)

    head_raw = _reduce_to_ennea(profile.expression or 1)
    head_type = head_raw if head_raw in CENTERS["Head"] else (5 if head_raw <= 3 else 6 if head_raw <= 6 else 7)

    tritype = sorted([body_type, heart_type, head_type])
    tritype_str = "".join(str(t) for t in [base_type] + [t for t in tritype if t != base_type])

    # Harmonic and Hornevian groups
    harmonic = None
    for group, types in HARMONIC_GROUPS.items():
        if base_type in types:
            harmonic = group
            break
    hornevian = None
    for group, types in HORNEVIAN_GROUPS.items():
        if base_type in types:
            hornevian = group
            break

    center = _get_center(base_type)

    return SystemResult(
        id="enneagram_deeper",
        name="Enneagram Deeper Analysis",
        certainty="META",
        data={
            "base_type": base_type,
            "type_name": TYPE_NAMES.get(base_type, ""),
            "center": center,
            "wings": [wing_a, wing_b],
            "growth_direction": growth,
            "growth_type_name": TYPE_NAMES.get(growth, ""),
            "stress_direction": stress,
            "stress_type_name": TYPE_NAMES.get(stress, ""),
            "instinctual_variant": instinctual,
            "tritype": tritype_str,
            "harmonic_group": harmonic,
            "hornevian_group": hornevian,
            "module_class": "meta",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Oscar Ichazo", "Claudio Naranjo", "Don Riso & Russ Hudson"],
        question="Q1_IDENTITY",
    )
