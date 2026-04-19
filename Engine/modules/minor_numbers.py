"""Minor Numbers (Expression / Heart's Desire / Personality from current name) — COMPUTED_STRICT
Same algorithms as Expression/Soul Urge/Personality but computed on current/short name
instead of birth name. Requires `current_name` field in profile.
Source: Decoz Minor Numbers reports
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

PYTH = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

VOWELS = set("AEIOU")


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    # Check for current_name in profile or kwargs
    current_name = kwargs.get("current_name") or getattr(profile, "current_name", None)

    if not current_name:
        return SystemResult(
            id="minor_numbers",
            name="Minor Numbers (Current Name)",
            certainty="NEEDS_INPUT",
            data={"note": "Requires current_name field in profile"},
            interpretation=None,
            constants_version=constants["version"],
            references=[
                "Decoz: Minor Numbers = Expression/Soul Urge/Personality on current/short name",
                "SOURCE_TIER:C — Modern system.",
            ],
            question="Q1_IDENTITY",
        )

    name = current_name.upper().replace(" ", "")
    all_vals = [PYTH[c] for c in name if c in PYTH]
    vowel_vals = [PYTH[c] for c in name if c in PYTH and c in VOWELS]
    consonant_vals = [PYTH[c] for c in name if c in PYTH and c not in VOWELS]

    minor_expression = reduce_number(sum(all_vals))
    minor_heart_desire = reduce_number(sum(vowel_vals))
    minor_personality = reduce_number(sum(consonant_vals))

    return SystemResult(
        id="minor_numbers",
        name="Minor Numbers (Current Name)",
        certainty="COMPUTED_STRICT",
        data={
            "current_name": current_name,
            "minor_expression": minor_expression,
            "minor_heart_desire": minor_heart_desire,
            "minor_personality": minor_personality,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Decoz: Minor Expression/Heart's Desire/Personality from current/short name",
            "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented.",
        ],
        question="Q1_IDENTITY",
    )
