"""Abjad Wusta (Middle Value) — COMPUTED_STRICT
Sequential 1-28 ordering, each letter = its ordinal position.
Used in intermediate-level Hurufism calculations.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    wusta = constants["arabic_letters"]["abjad_wusta"]
    name = profile.arabic.replace(" ", "")

    letter_values = [(ch, wusta[ch]) for ch in name if ch in wusta]
    total = sum(v for _, v in letter_values)
    root = reduce_number(total, keep_masters=())

    return SystemResult(
        id="abjad_wusta",
        name="Abjad Wusta (عدد الأبجد الوسطى)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic,
            "total": total,
            "root": root,
            "letter_count": len(letter_values),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Abjad Wusta: ordinal 1-28. ا=1, ب=2... غ=28. Middle value between Kabir and Saghir."],
        question="Q1_IDENTITY"
    )
