"""Essence Cycle — LOOKUP_FIXED"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

def _transit(letters, age):
    cycle = sum(v for _, v in letters)
    pos = age % cycle
    cumul = 0
    for letter, val in letters:
        cumul += val
        if pos < cumul:
            return letter, val
    return letters[-1]

def compute(profile: InputProfile, constants: dict, age: int) -> SystemResult:
    # Standard Pythagorean letter durations (each letter rules for its value in years)
    letter_vals = {
        'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
        'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9,
        'S':1,'T':2,'U':3,'V':4,'W':5,'X':6,'Y':7,'Z':8,
    }
    # Split name into first, middle, last (use first 3 components)
    parts = profile.subject.upper().split()
    first = parts[0] if len(parts) > 0 else ""
    middle = parts[1] if len(parts) > 1 else parts[0]
    last = parts[-1] if len(parts) > 1 else parts[0]

    def _build_durations(name):
        return [[ch, letter_vals.get(ch, 1)] for ch in name if ch in letter_vals]

    fl, fv = _transit(_build_durations(first), age)
    ml, mv = _transit(_build_durations(middle), age)
    ll, lv = _transit(_build_durations(last), age)
    s = fv + mv + lv
    return SystemResult(
        id="essence",
        name="Essence Cycle (letter transit)",
        certainty="LOOKUP_FIXED",
        data={"age": age, "letters": f"{fl}({fv})+{ml}({mv})+{ll}({lv})",
              "sum": s, "reduced": reduce_number(s)},
        interpretation="Deterministic given letter-duration mapping.",
        constants_version=constants["version"],
        references=["Letter-duration mapping in constants.json",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q4_TIMING"
    )
