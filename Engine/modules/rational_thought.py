"""Rational Thought Number — COMPUTED_STRICT
Sum of Pythagorean values of first name + birthday number → reduce.
Reveals the thought process and how one approaches problem-solving.
Source: Decoz, WorldNumerology Rational Thought article
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

PYTH = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    first_name = profile.subject.upper().split()[0] if profile.subject.split() else ""
    first_name_sum = sum(PYTH.get(c, 0) for c in first_name)

    birthday_number = reduce_number(profile.dob.day)

    raw = first_name_sum + birthday_number
    rational_thought = reduce_number(raw)

    return SystemResult(
        id="rational_thought",
        name="Rational Thought Number",
        certainty="COMPUTED_STRICT",
        data={
            "first_name": first_name,
            "first_name_sum": first_name_sum,
            "birthday_number": birthday_number,
            "raw_sum": raw,
            "rational_thought": rational_thought,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Decoz: Rational Thought = Pythagorean sum of first name + birthday number, reduced",
            "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented.",
        ],
        question="Q1_IDENTITY",
    )
