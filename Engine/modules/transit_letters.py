"""Transit Letters (Physical / Mental / Spiritual) — COMPUTED_STRICT
Letters cycle through name components; each letter stays active for years equal to its
Pythagorean value, then advances. Loop when exhausted.
- Physical transit: first name component
- Mental transit: second name component
- Spiritual transit: last name component
Source: Decoz Transits article, WorldNumerology
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

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

    return SystemResult(
        id="transit_letters",
        name="Transit Letters (Physical / Mental / Spiritual)",
        certainty="COMPUTED_STRICT",
        data={
            "age": age,
            "physical": {"name_source": first, "letter": phys_l, "value": phys_v},
            "mental": {"name_source": middle, "letter": ment_l, "value": ment_v},
            "spiritual": {"name_source": last, "letter": spir_l, "value": spir_v},
            "transit_sum": phys_v + ment_v + spir_v,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Decoz: Transit Letters cycle through name components. Each letter rules for years = its Pythagorean value",
            "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented.",
        ],
        question="Q4_TIMING",
    )
