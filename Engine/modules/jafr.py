"""Jafr (Comprehensive Jafr Matrix) — COMPUTED_STRICT
Constructs a cyclic letter matrix from the Arabic name.
Maps name letters to the 28-letter abjad sequence, then generates
a rotation matrix where each row shifts by one position.
The diagonal and anti-diagonal reveal hidden correspondences.
Source: Kitab al-Jafr (attr. Imam Ali), systematized 13th century
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# The 28 base Arabic letters in abjad order (no hamza variants)
ABJAD_28 = list("ابجدهوزحطيكلمنسعفصقرشتثخذضظغ")


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    name = profile.arabic.replace(" ", "")
    name_letters = [ch for ch in name if ch in abjad]

    # Map name letters to positions in the 28-letter sequence
    positions = []
    for ch in name_letters:
        # Normalize hamza variants to alif
        lookup = "ا" if ch in ("أ", "إ", "آ") else ch
        if lookup in ABJAD_28:
            positions.append(ABJAD_28.index(lookup))

    # Build the Jafr seed row: the 28 letters rotated by name's first position
    seed_offset = positions[0] if positions else 0
    seed_row = ABJAD_28[seed_offset:] + ABJAD_28[:seed_offset]

    # Generate square matrix: each row shifts by 1
    n = len(ABJAD_28)
    matrix = []
    for i in range(n):
        row = seed_row[i:] + seed_row[:i]
        matrix.append("".join(row))

    # Extract diagonal
    diagonal = [matrix[i][i] for i in range(n)]
    anti_diag = [matrix[i][n - 1 - i] for i in range(n)]

    # Diagonal abjad value
    diag_value = sum(abjad.get(ch, 0) for ch in diagonal)
    anti_value = sum(abjad.get(ch, 0) for ch in anti_diag)

    # Name positions summary
    name_positions_str = [(ch, ABJAD_28.index("ا" if ch in ("أ","إ","آ") else ch)
                           if ("ا" if ch in ("أ","إ","آ") else ch) in ABJAD_28 else -1)
                          for ch in name_letters]

    return SystemResult(
        id="jafr",
        name="Jafr (الجفر الجامع — Comprehensive Jafr Matrix)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic,
            "name_letter_count": len(name_letters),
            "seed_offset": seed_offset,
            "matrix_size": n,
            "matrix_first_3_rows": matrix[:3],
            "matrix_last_row": matrix[-1],
            "diagonal": "".join(diagonal),
            "diagonal_value": diag_value,
            "anti_diagonal": "".join(anti_diag),
            "anti_diagonal_value": anti_value,
            "name_positions": [(ch, pos) for ch, pos in name_positions_str],
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "28×28 cyclic Jafr matrix seeded by name's first letter position.",
            "Diagonal extraction reveals hidden correspondences.",
            "Source: Kitab al-Jafr (attributed to Imam Ali).",
        ],
        question="Q1_IDENTITY"
    )
