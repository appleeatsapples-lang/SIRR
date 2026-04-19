"""Abjad Kabir (Full Name) — COMPUTED_STRICT
Full Abjad summation of all letters in Arabic name, not just initials.
The classical Ilm al-Huruf primary calculation.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
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
        id="abjad_kabir",
        name="Abjad Kabir (عدد الأبجد الكبير)",
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
        references=["Abjad Kabir: ا=1 through غ=1000. Full name sum, classical ordering."],
        question="Q1_IDENTITY"
    )
