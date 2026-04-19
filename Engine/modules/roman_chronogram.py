"""Roman Chronogram Name — COMPUTED_STRICT
Sum only letters that are valid Roman numerals: I=1, V=5, X=10, L=50, C=100, D=500, M=1000.
Ignore all other letters. Reduce.
Source: Roman numeral / chronogram tradition (Britannica)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

ROMAN_VALUES = {
    'I': 1, 'V': 5, 'X': 10, 'L': 50,
    'C': 100, 'D': 500, 'M': 1000,
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    name = profile.subject.upper()
    found = []
    for ch in name:
        if ch in ROMAN_VALUES:
            found.append((ch, ROMAN_VALUES[ch]))

    chronogram_total = sum(v for _, v in found)
    chronogram_root = reduce_number(chronogram_total) if chronogram_total > 0 else 0

    # Letter frequency breakdown
    from collections import Counter
    letter_counts = Counter(ch for ch, _ in found)

    return SystemResult(
        id="roman_chronogram",
        name="Roman Chronogram Name",
        certainty="COMPUTED_STRICT",
        data={
            "name_analyzed": profile.subject,
            "roman_letters_found": [{"letter": l, "value": v} for l, v in found],
            "letter_counts": dict(sorted(letter_counts.items())),
            "chronogram_total": chronogram_total,
            "chronogram_root": chronogram_root,
            "roman_letter_count": len(found),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Roman chronogram tradition: sum of Roman numeral letters in a text yields a hidden date/number",
            "Encyclopaedia Britannica: 'Chronogram'",
            "SOURCE_TIER:A — Well-documented historical tradition with clear algorithmic definition.",
        ],
        question="Q1_IDENTITY",
    )
