"""Period Cycles (3 life periods) — COMPUTED_STRICT
Period 1: Reduce birth month → period number. Duration: birth to age (36 - LP).
Period 2: Reduce birth day → period number. Duration: 27 years.
Period 3: Reduce birth year → period number. Duration: remainder of life.
Source: Decoz Period Cycles, WorldNumerology
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    m = profile.dob.month
    d = profile.dob.day
    y = profile.dob.year

    period1 = reduce_number(m)
    period2 = reduce_number(d)
    period3 = reduce_number(sum(int(x) for x in str(y)))

    lp = profile.life_path or reduce_number(
        reduce_number(m) + reduce_number(d) + reduce_number(sum(int(x) for x in str(y)))
    )
    end1 = 36 - lp
    end2 = end1 + 27

    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1

    if age <= end1:
        current = 1
    elif age <= end2:
        current = 2
    else:
        current = 3

    return SystemResult(
        id="period_cycles",
        name="Period Cycles",
        certainty="COMPUTED_STRICT",
        data={
            "period_1": {"number": period1, "ages": f"0-{end1}"},
            "period_2": {"number": period2, "ages": f"{end1 + 1}-{end2}"},
            "period_3": {"number": period3, "ages": f"{end2 + 1}+"},
            "current_period": current,
            "current_age": age,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Decoz: Period 1 = birth month, Period 2 = birth day, Period 3 = birth year (all reduced). First period ends at 36 - Life Path",
            "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented.",
        ],
        question="Q4_TIMING",
    )
