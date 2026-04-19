"""Temurah Avgad Cipher — COMPUTED_STRICT
Forward letter-shift cipher: each Hebrew letter → next letter in alephbet.
Applied to Arabic name via transliteration.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    gematria_cfg = constants["hebrew_gematria"]
    avgad_cfg = constants["avgad"]
    values = gematria_cfg["values"]
    a2h = gematria_cfg["arabic_to_hebrew"]
    shift_map = avgad_cfg["map"]

    arabic_name = profile.arabic

    original_letters = []
    shifted_letters = []
    for char in arabic_name:
        if char in a2h:
            heb = a2h[char]
            shifted = shift_map[heb]
            original_letters.append((char, heb, values[heb]))
            shifted_letters.append((heb, shifted, values[shifted]))

    original_sum = sum(v for _, _, v in original_letters)
    avgad_sum = sum(v for _, _, v in shifted_letters)
    original_root = reduce_number(original_sum, keep_masters=(11, 22, 33))
    avgad_root = reduce_number(avgad_sum, keep_masters=(11, 22, 33))
    delta = avgad_sum - original_sum

    return SystemResult(
        id="avgad",
        name="Temurah Avgad (Forward Shift Cipher)",
        certainty="COMPUTED_STRICT",
        data={
            "original_letters": original_letters,
            "shifted_letters": shifted_letters,
            "original_sum": original_sum,
            "original_root": original_root,
            "avgad_sum": avgad_sum,
            "avgad_root": avgad_root,
            "delta": delta,
            "note": "Avgad shifts each letter forward by 1 in the Hebrew alephbet. Reveals the 'next step' or evolutionary potential of the name."
        },
        interpretation=f"Original gematria {original_sum}→Avgad {avgad_sum} (delta {delta:+d}). Root shift: {original_root}→{avgad_root}.",
        constants_version=constants["version"],
        references=["Temurah tradition", "Sefer Yetzirah letter permutations"],
        question="Q1_IDENTITY"
    )
