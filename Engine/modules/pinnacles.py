"""Pinnacle Cycles — COMPUTED_STRICT
4 life phases with peak energies, derived purely from DOB digits.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    m = profile.dob.month
    d = profile.dob.day
    y = profile.dob.year

    rm = reduce_number(m)
    rd = reduce_number(d)
    ry = reduce_number(sum(int(x) for x in str(y)))

    # Pinnacle values
    p1 = reduce_number(rm + rd)
    p2 = reduce_number(rd + ry)
    p3 = reduce_number(p1 + p2)
    p4 = reduce_number(rm + ry)

    # Timing: first pinnacle ends at 36 - life_path
    lp = profile.life_path or reduce_number(rm + rd + ry)
    end1 = 36 - lp
    end2 = end1 + 9
    end3 = end2 + 9

    return SystemResult(
        id="pinnacles",
        name="Pinnacle Cycles",
        certainty="COMPUTED_STRICT",
        data={
            "pinnacle_1": {"value": p1, "ages": f"0-{end1}"},
            "pinnacle_2": {"value": p2, "ages": f"{end1}-{end2}"},
            "pinnacle_3": {"value": p3, "ages": f"{end2}-{end3}"},
            "pinnacle_4": {"value": p4, "ages": f"{end3}+"},
            "current_pinnacle": (
                1 if (profile.today.year - profile.dob.year) <= end1 else
                2 if (profile.today.year - profile.dob.year) <= end2 else
                3 if (profile.today.year - profile.dob.year) <= end3 else 4
            ),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Standard Pythagorean pinnacle calculation: 36 - LP for first cycle",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q4_TIMING"
    )
