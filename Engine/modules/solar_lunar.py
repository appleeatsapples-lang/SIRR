"""Solar/Lunar Letter Classification — LOOKUP_FIXED
Based on assimilation behavior with the definite article ال (al-).
Solar letters assimilate the lam, lunar letters don't.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    solar = set(constants["arabic_letters"]["solar"])
    lunar = set(constants["arabic_letters"]["lunar"])
    name = profile.arabic.replace(" ", "")

    letters = [ch for ch in name if ch in solar or ch in lunar]
    s_count = sum(1 for ch in letters if ch in solar)
    l_count = sum(1 for ch in letters if ch in lunar)
    total = s_count + l_count

    ratio = round(s_count / total, 2) if total > 0 else 0
    if ratio > 0.6:
        dominant = "solar"
    elif ratio < 0.4:
        dominant = "lunar"
    else:
        dominant = "balanced"

    return SystemResult(
        id="solar_lunar",
        name="Solar/Lunar Letters (الحروف الشمسية والقمرية)",
        certainty="LOOKUP_FIXED",
        data={
            "arabic_name": profile.arabic,
            "solar_count": s_count,
            "lunar_count": l_count,
            "total_letters": total,
            "solar_ratio": ratio,
            "dominant": dominant,
            "solar_letters_found": [ch for ch in letters if ch in solar],
            "lunar_letters_found": [ch for ch in letters if ch in lunar],
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Solar: assimilate with ال. Lunar: preserve the lam. 14 each."],
        question="Q3_NATURE"
    )
