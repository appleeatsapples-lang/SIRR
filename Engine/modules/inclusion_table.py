"""Inclusion Table (Karmic Lessons) — COMPUTED_STRICT
Maps every letter in full birth name to Pythagorean digit (1-9).
Counts frequency of each digit. Missing digits = karmic lessons.
Source: Decoz Karmic Lessons chart
"""
from __future__ import annotations
from collections import Counter
from sirr_core.types import InputProfile, SystemResult

PYTH = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    name = profile.subject.upper().replace(" ", "")
    digits = [PYTH[c] for c in name if c in PYTH]
    counts = Counter(digits)

    # Build inclusion table: counts for digits 1-9
    table = {d: counts.get(d, 0) for d in range(1, 10)}
    missing = sorted([d for d in range(1, 10) if counts.get(d, 0) == 0])
    total_letters = len(digits)

    # Dominant digits (highest frequency)
    if counts:
        max_count = max(counts.values())
        dominant = sorted([d for d, c in counts.items() if c == max_count])
    else:
        max_count = 0
        dominant = []

    return SystemResult(
        id="inclusion_table",
        name="Inclusion Table (Karmic Lessons)",
        certainty="COMPUTED_STRICT",
        data={
            "name_analyzed": profile.subject,
            "total_letters": total_letters,
            "table": table,
            "missing_digits": missing,
            "karmic_lesson_count": len(missing),
            "dominant_digits": dominant,
            "dominant_frequency": max_count,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Decoz: Inclusion Table = Pythagorean letter frequency distribution. Missing digits = Karmic Lessons",
            "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented.",
        ],
        question="Q1_IDENTITY",
    )
