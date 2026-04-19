"""Yearly Essence Cycle — COMPUTED_STRICT
Sum of the 3 active transit letter values for the current birthday-to-birthday year → reduce.
Distinct from personal_year (which uses calendar date, not name transits).
Source: Decoz Essence Cycles article
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

PYTH = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}


def _build_durations(name: str) -> list:
    return [(ch, PYTH[ch]) for ch in name.upper() if ch in PYTH]


def _transit_at_age(letters: list, age: int) -> tuple:
    if not letters:
        return ("?", 0)
    cycle = sum(v for _, v in letters)
    if cycle == 0:
        return letters[0]
    pos = age % cycle
    cumul = 0
    for letter, val in letters:
        cumul += val
        if pos < cumul:
            return (letter, val)
    return letters[-1]


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    parts = profile.subject.upper().split()
    first = parts[0] if len(parts) > 0 else ""
    middle = " ".join(parts[1:-1]) if len(parts) > 2 else parts[1] if len(parts) > 1 else parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else parts[0] if parts else ""

    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1

    phys_l, phys_v = _transit_at_age(_build_durations(first), age)
    ment_l, ment_v = _transit_at_age(_build_durations(middle), age)
    spir_l, spir_v = _transit_at_age(_build_durations(last), age)

    transit_sum = phys_v + ment_v + spir_v
    essence = reduce_number(transit_sum)

    return SystemResult(
        id="yearly_essence_cycle",
        name="Yearly Essence Cycle",
        certainty="COMPUTED_STRICT",
        data={
            "age": age,
            "transits": f"{phys_l}({phys_v})+{ment_l}({ment_v})+{spir_l}({spir_v})",
            "transit_sum": transit_sum,
            "essence_number": essence,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Decoz: Essence Cycle = sum of 3 active transit letter values, reduced. Birthday-to-birthday year",
            "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented.",
        ],
        question="Q4_TIMING",
    )
