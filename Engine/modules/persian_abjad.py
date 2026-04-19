"""Persian Extended Abjad — LOOKUP_FIXED / COMPUTED_STRICT
Extends standard Arabic Abjad Kabir with 4 Persian-exclusive letters (پ/چ/ژ/گ).
Source (Tier B): Persian chronogram and Huruf poetry tradition (10th–15th century).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Persian-exclusive letter values (not in standard Arabic alphabet)
PERSIAN_EXTENSION = {
    '\u067e': 2,   # پ Pe — same value as ب (Ba)
    '\u0686': 3,   # چ Che — same value as ج (Jim)
    '\u0698': 7,   # ژ Zhe — same value as ز (Zayn)
    '\u06af': 3,   # گ Gaf — disputed: 3 (common) vs 400 (Kaf-extension)
}

PERSIAN_CHARS = set(PERSIAN_EXTENSION.keys())


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]

    # Merge: standard Arabic + Persian extension
    full_table = dict(abjad)
    full_table.update(PERSIAN_EXTENSION)

    name = profile.arabic
    name_stripped = name.replace(" ", "")

    # Compute with full table (standard + Persian)
    total = 0
    letter_count = 0
    persian_found = []
    has_gaf = False

    for ch in name_stripped:
        if ch in full_table:
            total += full_table[ch]
            letter_count += 1
            if ch in PERSIAN_CHARS:
                persian_found.append(ch)
                if ch == '\u06af':  # گ
                    has_gaf = True

    # Compute standard-only total (without Persian extension)
    standard_total = sum(abjad.get(ch, 0) for ch in name_stripped if ch in abjad)
    extension_delta = total - standard_total
    persian_used = len(persian_found) > 0

    root = reduce_number(total, keep_masters=())

    # Per-word breakdown
    words = name.split()
    word_sums = {}
    for w in words:
        ws = sum(full_table.get(ch, 0) for ch in w)
        word_sums[w] = ws

    # Certainty: COMPUTED_STRICT if Persian letters applied, LOOKUP_FIXED otherwise
    certainty = "COMPUTED_STRICT" if persian_used else "LOOKUP_FIXED"

    return SystemResult(
        id="persian_abjad",
        name="Persian Extended Abjad (ابجد فارسی)",
        certainty=certainty,
        data={
            "arabic_name": profile.arabic,
            "total": total,
            "root": root,
            "letter_count": letter_count,
            "persian_letters_found": persian_found,
            "persian_letters_used": persian_used,
            "standard_abjad_total": standard_total,
            "extension_delta": extension_delta,
            "gaf_dispute_flag": has_gaf,
            "word_sums": word_sums,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Persian chronogram/Huruf tradition (10th-15th century manuscripts)",
            "Gaf value disputed: 3 (positional) vs 400 (Kaf-extension). Uses 3.",
        ],
        question="Q1_IDENTITY",
    )
