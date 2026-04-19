"""Hidden Passion — COMPUTED_STRICT
The most frequently occurring digit in the Pythagorean name chart.
Reveals the dominant inner drive.
"""
from __future__ import annotations
from collections import Counter
from sirr_core.types import InputProfile, SystemResult

PYTH = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper().replace(" ", "")
    digits = [PYTH[c] for c in name if c in PYTH]
    counts = Counter(digits)

    if not counts:
        return SystemResult(
            id="hidden_passion", name="Hidden Passion Number",
            certainty="COMPUTED_STRICT", data={"error": "no letters found"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q1_IDENTITY"
        )

    max_count = max(counts.values())
    passions = sorted([d for d, c in counts.items() if c == max_count])

    return SystemResult(
        id="hidden_passion",
        name="Hidden Passion Number",
        certainty="COMPUTED_STRICT",
        data={
            "name_analyzed": profile.subject,
            "digit_counts": dict(sorted(counts.items())),
            "hidden_passion": passions[0] if len(passions) == 1 else passions,
            "frequency": max_count,
            "multiple": len(passions) > 1,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Most frequent Pythagorean digit in full birth name",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q1_IDENTITY"
    )
