"""Balance Number — COMPUTED_STRICT
First letter of each name component → Pythagorean value → sum → reduce to single digit (no masters).
Reveals how one handles challenges and difficult situations.
Source: Decoz, WorldNumerology Balance article
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
    parts = profile.subject.upper().split()
    initials = []
    for part in parts:
        if part and part[0] in PYTH:
            initials.append((part[0], PYTH[part[0]]))

    raw_sum = sum(v for _, v in initials)
    # Balance number reduces to single digit, no master numbers preserved
    balance = reduce_number(raw_sum, keep_masters=())

    return SystemResult(
        id="balance_number",
        name="Balance Number",
        certainty="COMPUTED_STRICT",
        data={
            "name_analyzed": profile.subject,
            "initials": [{"letter": l, "value": v} for l, v in initials],
            "raw_sum": raw_sum,
            "balance_number": balance,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Decoz: Balance Number = sum of first letters of each name component, reduced (no masters)",
            "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented.",
        ],
        question="Q1_IDENTITY",
    )
