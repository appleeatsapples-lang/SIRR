"""Abjad Maghribi (North African Abjad) — COMPUTED_STRICT
Maghribi ordering differs from Mashriqi (Eastern) for 6 letters:
  س=300 (not 60), ص=60 (not 90), ش=1000 (not 300),
  ض=90 (not 800), ظ=800 (not 900), غ=900 (not 1000).
Source: Ibn Khaldun, The Muqaddimah (Chapter VI).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_maghribi"]
    name = profile.arabic.replace(" ", "")

    letter_values = []
    for ch in name:
        if ch in abjad:
            letter_values.append((ch, abjad[ch]))

    total = sum(v for _, v in letter_values)
    root = reduce_number(total, keep_masters=())

    # Per-word breakdown
    words = profile.arabic.split()
    word_sums = {}
    for w in words:
        ws = sum(abjad.get(ch, 0) for ch in w)
        word_sums[w] = ws

    return SystemResult(
        id="abjad_maghribi",
        name="Abjad Maghribi (عدد الأبجد المغربي)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic,
            "total": total,
            "root": root,
            "word_sums": word_sums,
            "letter_count": len(letter_values),
            "letter_breakdown": [(ch, v) for ch, v in letter_values],
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Abjad Maghribi: Ibn Khaldun Muqaddimah Ch. VI. 6 letters differ from Mashriqi ordering."],
        question="Q1_IDENTITY"
    )
