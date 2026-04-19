"""Luminous/Dark Letter Profile — LOOKUP_FIXED
Nurani (نوراني) vs Zulmani (ظلماني) classification.
Based on the 14 Muqatta'at letters that open certain Quran chapters.
Letters present in Muqatta'at = Luminous. Absent = Dark.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    luminous_set = set(constants["arabic_letters"]["luminous"])
    dark_set = set(constants["arabic_letters"]["dark"])

    name = profile.arabic.replace(" ", "")
    letters = [ch for ch in name if ch in luminous_set or ch in dark_set]

    lum_count = sum(1 for ch in letters if ch in luminous_set)
    dark_count = sum(1 for ch in letters if ch in dark_set)
    total = lum_count + dark_count

    ratio = round(lum_count / total, 2) if total > 0 else 0
    if ratio > 0.6:
        dominant = "luminous"
    elif ratio < 0.4:
        dominant = "dark"
    else:
        dominant = "balanced"

    return SystemResult(
        id="luminous_dark",
        name="Luminous/Dark Letters (نوراني/ظلماني)",
        certainty="LOOKUP_FIXED",
        data={
            "arabic_name": profile.arabic,
            "luminous_count": lum_count,
            "dark_count": dark_count,
            "total_letters": total,
            "luminous_ratio": ratio,
            "dominant": dominant,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["14 Muqatta'at letters = Luminous (نوراني). 14 remaining = Dark (ظلماني). Based on Quranic letter openings."],
        question="Q3_NATURE"
    )
