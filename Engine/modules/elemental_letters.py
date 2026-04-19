"""Elemental Letter Profile — LOOKUP_FIXED
Fire/Air/Water/Earth classification of Arabic letters.
Based on classical Hurufism (عِلم الحُروف) elemental grouping.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    elem = constants["arabic_letters"]["elemental"]
    # Build reverse lookup
    letter_element = {}
    for element, letters in elem.items():
        for ch in letters:
            letter_element[ch] = element

    name = profile.arabic.replace(" ", "")
    letters = [ch for ch in name if ch in letter_element]

    counts = {"fire": 0, "air": 0, "water": 0, "earth": 0}
    for ch in letters:
        counts[letter_element[ch]] += 1

    total = sum(counts.values())
    percentages = {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in counts.items()}
    dominant = max(counts, key=counts.get) if total > 0 else "unknown"

    # Secondary element
    sorted_elems = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    secondary = sorted_elems[1][0] if len(sorted_elems) > 1 else None

    return SystemResult(
        id="elemental_letters",
        name="Elemental Letter Profile (عناصر الحروف)",
        certainty="LOOKUP_FIXED",
        data={
            "arabic_name": profile.arabic,
            "counts": counts,
            "percentages": percentages,
            "dominant_element": dominant,
            "secondary_element": secondary,
            "total_classified": total,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Classical Hurufism: 7 letters per element. Fire=ا ه ط م ف ش ذ, etc."],
        question="Q3_NATURE"
    )
