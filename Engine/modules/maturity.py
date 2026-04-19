"""Maturity Number — COMPUTED_STRICT
Life Path + Expression, reduced. Represents the integrated self
that emerges in the second half of life (typically after age 35-40).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    lp = profile.life_path
    expr = profile.expression

    if lp is None or expr is None:
        return SystemResult(
            id="maturity", name="Maturity Number",
            certainty="NEEDS_INPUT",
            data={"error": "Requires life_path and expression in profile"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q5_ARC"
        )

    raw = lp + expr
    maturity = reduce_number(raw)

    return SystemResult(
        id="maturity",
        name="Maturity Number",
        certainty="COMPUTED_STRICT",
        data={
            "life_path": lp,
            "expression": expr,
            "raw_sum": raw,
            "maturity_number": maturity,
            "activation_age": "35-40",
            "note": "Emerges as dominant energy in second half of life"
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Maturity = Life Path + Expression, reduced. Active from mid-30s onward.",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q5_ARC"
    )
