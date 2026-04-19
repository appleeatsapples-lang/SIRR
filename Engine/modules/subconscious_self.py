"""Subconscious Self — COMPUTED_STRICT
Count of distinct digits 1-9 represented in the full name.
Measures instinctive response breadth.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

PYTH = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper().replace(" ", "")
    digits = {PYTH[c] for c in name if c in PYTH}

    present = sorted(digits)
    missing = sorted(set(range(1, 10)) - digits)
    score = len(present)

    return SystemResult(
        id="subconscious_self",
        name="Subconscious Self",
        certainty="COMPUTED_STRICT",
        data={
            "name_analyzed": profile.subject,
            "digits_present": present,
            "digits_missing": missing,
            "score": score,
            "out_of": 9,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Count of unique Pythagorean digits 1-9 in full name. 9/9 = fully equipped instincts.",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q3_GAPS"
    )
