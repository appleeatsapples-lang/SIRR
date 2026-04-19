"""Void Matrix — Structural Absence Analysis — COMPUTED_STRICT (comparative)
Maps what is MISSING across multiple bodies: Lo Shu missing digits,
absent elements, absent makhraj categories, absent semantic fields.
Makes absence computable.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


ALL_ELEMENTS = {"fire", "air", "water", "earth"}
ALL_MAKHRAJ = {"guttural", "velar", "palatal", "lateral", "alveolar",
               "dental", "sibilant", "interdental", "labio-dental", "bilabial"}
ALL_SEMANTIC_FIELDS = {"veneration_awe", "time_cultivation", "theophory_audition",
                       "stillness_devotion", "praise_recognition", "definition_form",
                       "chemistry_synthesis"}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    results = kwargs.get("all_results", [])

    # 1. Lo Shu missing digits
    lo_shu_missing = []
    for r in results:
        if r.id == "lo_shu_grid":
            lo_shu_missing = r.data.get("missing", [])
            break

    has_center = 5 not in lo_shu_missing
    void_center = not has_center

    # 2. Element voids (from elemental_letters)
    element_present = set()
    for r in results:
        if r.id == "elemental_letters":
            counts = r.data.get("counts", {})
            element_present = {k for k, v in counts.items() if v > 0}
            break
    element_absent = sorted(ALL_ELEMENTS - element_present)

    # 3. Makhraj voids (from arabic_phonetics)
    makhraj_present = set()
    for r in results:
        if r.id == "arabic_phonetics":
            dist = r.data.get("makhraj_distribution", {})
            makhraj_present = set(dist.keys())
            break
    makhraj_absent = sorted(ALL_MAKHRAJ - makhraj_present)

    # 4. Semantic field voids (from name_semantics)
    semantic_present = set()
    for r in results:
        if r.id == "name_semantics":
            for ws in r.data.get("word_semantics", []):
                f = ws.get("semantic_field")
                if f and f != "unclassified":
                    semantic_present.add(f)
            break
    semantic_absent = sorted(ALL_SEMANTIC_FIELDS - semantic_present)

    # Void count
    total_voids = len(lo_shu_missing) + len(element_absent) + len(makhraj_absent) + len(semantic_absent)

    # Torque score: how asymmetric is the void pattern
    # Higher score = more concentrated absence
    void_counts = [len(lo_shu_missing), len(element_absent), len(makhraj_absent), len(semantic_absent)]
    max_void = max(void_counts) if void_counts else 0
    min_void = min(void_counts) if void_counts else 0
    torque = max_void - min_void

    return SystemResult(
        id="void_matrix",
        name="Void Matrix (مصفوفة الفراغ)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "comparative",
            "lo_shu_missing": lo_shu_missing,
            "void_center": void_center,
            "element_absent": element_absent,
            "makhraj_absent": makhraj_absent,
            "semantic_absent": semantic_absent,
            "total_voids": total_voids,
            "torque": torque,
            "void_summary": {
                "digits": len(lo_shu_missing),
                "elements": len(element_absent),
                "makhraj": len(makhraj_absent),
                "semantics": len(semantic_absent),
            },
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Structural absence analysis — making voids computable across all bodies"],
        question="Q6_SYNTHESIS"
    )
