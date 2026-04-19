"""Hermetic Alignment — Cross-Axis Agreement Matrix — COMPUTED_STRICT (comparative)
Compares dominant roots across axes (name, sky, digit, elemental, cyclic)
and computes pairwise agreement. "As above, so below" — tested structurally.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    results = kwargs.get("all_results", [])

    # Collect dominant values from each axis
    axes = {}

    # Name axis: abjad root
    for r in results:
        if r.id == "abjad_kabir":
            axes["name_abjad"] = r.data.get("root", 0)
        elif r.id == "arabic_roots":
            axes["name_root_abjad"] = r.data.get("root_abjad_root", 0)

    # Digit axis: life path, birthday
    axes["digit_life_path"] = profile.life_path or 0
    axes["digit_expression"] = profile.expression or 0
    axes["digit_birthday"] = profile.birthday_number or 0

    # Sky axis: from natal chart (sign → number mapping is loose, use house)
    for r in results:
        if r.id == "natal_chart":
            axes["sky_sun_degree"] = r.data.get("sun_degree", 0)

    # Elemental axis: dominant element from Al-Buni
    for r in results:
        if r.id == "arabic_letter_nature":
            elem = r.data.get("dominant_element", "")
            elem_map = {"fire": 1, "earth": 4, "air": 3, "water": 2}
            axes["elemental_number"] = elem_map.get(elem, 0)

    # Cyclic axis: personal year
    for r in results:
        if r.id == "personal_year":
            axes["cyclic_personal_year"] = r.data.get("personal_year", 0)

    # Chaldean root
    for r in results:
        if r.id == "chaldean":
            axes["chaldean_root"] = r.data.get("chaldean_root", 0)

    # Pairwise agreement matrix
    axis_keys = sorted(axes.keys())
    agreements = 0
    comparisons = 0
    agreement_pairs = []

    for i in range(len(axis_keys)):
        for j in range(i + 1, len(axis_keys)):
            k1, k2 = axis_keys[i], axis_keys[j]
            v1, v2 = axes[k1], axes[k2]
            comparisons += 1
            if v1 == v2 and v1 != 0:
                agreements += 1
                agreement_pairs.append(f"{k1}={k2}={v1}")

    alignment_score = round(agreements / comparisons * 100, 1) if comparisons > 0 else 0

    # Dominant value (most frequent across axes)
    value_counts = {}
    for v in axes.values():
        if v != 0:
            value_counts[v] = value_counts.get(v, 0) + 1
    dominant_value = max(value_counts, key=value_counts.get) if value_counts else 0
    dominant_count = value_counts.get(dominant_value, 0)

    return SystemResult(
        id="hermetic_alignment",
        name="Hermetic Alignment (التوافق الهرمسي)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "comparative",
            "axes": axes,
            "axis_count": len(axes),
            "comparisons": comparisons,
            "agreements": agreements,
            "alignment_score": alignment_score,
            "agreement_pairs": agreement_pairs,
            "dominant_value": dominant_value,
            "dominant_count": dominant_count,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Hermetic correspondence — 'As above, so below' tested structurally across axes"],
        question="Q6_SYNTHESIS"
    )
