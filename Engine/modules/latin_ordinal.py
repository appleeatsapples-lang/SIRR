"""Latin Ordinal Gematria (A=1..Z=26) — COMPUTED_STRICT
Simple ordinal mapping: A=1, B=2, ... Z=26.
Sum and reduce. Also computes reverse ordinal (A=26, Z=1).
Source: English Qabalah / Simple Gematria tradition
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [ch for ch in name if ch.isalpha()]

    ordinal_vals = [ord(ch) - 64 for ch in letters]  # A=1..Z=26
    reverse_vals = [27 - (ord(ch) - 64) for ch in letters]  # A=26..Z=1

    ordinal_sum = sum(ordinal_vals)
    reverse_sum = sum(reverse_vals)
    ordinal_root = reduce_number(ordinal_sum, keep_masters=(11, 22, 33))
    reverse_root = reduce_number(reverse_sum, keep_masters=(11, 22, 33))

    # Per-word breakdown
    words = profile.subject.upper().split()
    word_sums = {}
    for w in words:
        ws = sum(ord(ch) - 64 for ch in w if ch.isalpha())
        word_sums[w] = ws

    return SystemResult(
        id="latin_ordinal",
        name="Latin Ordinal Gematria (A=1..Z=26)",
        certainty="COMPUTED_STRICT",
        data={
            "name": profile.subject,
            "ordinal_sum": ordinal_sum,
            "ordinal_root": ordinal_root,
            "reverse_sum": reverse_sum,
            "reverse_root": reverse_root,
            "letter_count": len(letters),
            "word_sums": word_sums,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Simple English Gematria: A=1..Z=26 ordinal + reverse (A=26..Z=1)",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q1_IDENTITY"
    )
