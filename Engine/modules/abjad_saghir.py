"""Abjad Saghir (Small Value) — COMPUTED_STRICT
Each letter reduced to single digit (mod-9 cycle).
Used in simplified Jafr calculations.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    saghir = constants["arabic_letters"]["abjad_saghir"]
    name = profile.arabic.replace(" ", "")

    letter_values = [(ch, saghir[ch]) for ch in name if ch in saghir]
    total = sum(v for _, v in letter_values)
    root = reduce_number(total, keep_masters=())

    # Digit frequency in saghir values
    from collections import Counter
    freq = Counter(v for _, v in letter_values)

    return SystemResult(
        id="abjad_saghir",
        name="Abjad Saghir (عدد الأبجد الصغير)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic,
            "total": total,
            "root": root,
            "digit_frequency": dict(sorted(freq.items())),
            "dominant_digit": max(freq, key=freq.get) if freq else None,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Abjad Saghir: cyclical 1-9 reduction (ي=1, ك=2... غ=1). Simplified Jafr tradition."],
        question="Q1_IDENTITY"
    )
