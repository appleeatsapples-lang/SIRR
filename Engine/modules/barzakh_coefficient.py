"""Barzakh Coefficient — Fixed vs Kinetic Signal Ratio — COMPUTED_STRICT (comparative)
Measures the ratio of fixed structural vectors (abjad, life path, expression)
to kinetic timing vectors (firdaria, vimshottari, biorhythm, personal year).
The barzakh is the structural boundary between permanent identity and temporal flow.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    results = kwargs.get("all_results", [])

    # Fixed vectors: values that never change
    fixed = {}
    fixed["life_path"] = profile.life_path or 0
    fixed["expression"] = profile.expression or 0
    fixed["soul_urge"] = profile.soul_urge or 0
    fixed["personality"] = profile.personality or 0
    fixed["birthday_number"] = profile.birthday_number or 0
    fixed["abjad_first"] = profile.abjad_first or 0

    # From module outputs
    for r in results:
        if r.id == "abjad_kabir":
            fixed["abjad_total"] = r.data.get("total", 0)
            fixed["abjad_root"] = r.data.get("root", 0)

    fixed_sum = sum(fixed.values())
    fixed_count = len(fixed)

    # Kinetic vectors: values that change with time
    kinetic = {}
    for r in results:
        if r.id == "personal_year":
            kinetic["personal_year"] = r.data.get("personal_year", 0)
            kinetic["personal_month"] = r.data.get("personal_month", 0)
        elif r.id == "biorhythm":
            # Use absolute percentages
            for key in ("physical_pct", "emotional_pct", "intellectual_pct"):
                val = r.data.get(key, 0)
                kinetic[key] = abs(val) if val else 0
        elif r.id == "profection":
            kinetic["profection_house"] = r.data.get("house", 0)
        elif r.id == "essence":
            kinetic["essence"] = r.data.get("reduced", 0)

    kinetic_sum = sum(kinetic.values())
    kinetic_count = len(kinetic)

    # Barzakh coefficient: fixed / (fixed + kinetic)
    total = fixed_sum + kinetic_sum
    if total > 0:
        coefficient = round(fixed_sum / total, 4)
    else:
        coefficient = 0.5

    # Classification
    if coefficient > 0.8:
        classification = "structurally_dominant"
    elif coefficient > 0.6:
        classification = "structure_leaning"
    elif coefficient > 0.4:
        classification = "balanced"
    elif coefficient > 0.2:
        classification = "kinetic_leaning"
    else:
        classification = "kinetically_dominant"

    return SystemResult(
        id="barzakh_coefficient",
        name="Barzakh Coefficient (معامل البرزخ)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "comparative",
            "fixed_sum": fixed_sum,
            "fixed_count": fixed_count,
            "kinetic_sum": kinetic_sum,
            "kinetic_count": kinetic_count,
            "coefficient": coefficient,
            "classification": classification,
            "fixed_vectors": fixed,
            "kinetic_vectors": kinetic,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Barzakh: the boundary between fixed identity and temporal flow"],
        question="Q6_SYNTHESIS"
    )
