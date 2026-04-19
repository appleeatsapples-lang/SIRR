"""Buduh Matrix (Personal Buduh Square) — COMPUTED_STRICT
The Buduh (بدوح) is the foundational 3×3 magic square of Islamic esotericism.
Letters Ba-Dal-Waw-Ha map to 2-4-6-8, forming the even skeleton of Lo Shu.
Personal Buduh integrates the name's abjad root into the matrix center,
shifting all cells to maintain the magic constant.
This differs from wafq (which offsets from a given number) by using
the BDWH letter mapping and producing letter+number dual output.
Source: Pre-Islamic origins, codified by Al-Buni (12th century)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Classic Buduh base (Lo Shu): magic constant = 15, center = 5
LOSHU_BASE = [[2, 7, 6], [9, 5, 1], [4, 3, 8]]

# BDWH letter positions (even numbers in Lo Shu)
BDWH = {"ب": 2, "د": 4, "و": 6, "ح": 8}
BDWH_POSITIONS = {2: "ب", 4: "د", 6: "و", 8: "ح"}


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    name = profile.arabic.replace(" ", "")
    total = sum(abjad.get(ch, 0) for ch in name)
    root = reduce_number(total, keep_masters=())

    # Personal offset: shift center from 5 to the name's root
    offset = root - 5
    personal_square = [[cell + offset for cell in row] for row in LOSHU_BASE]
    magic_constant = 15 + (3 * offset)

    # Map BDWH letters in the personal square
    letter_grid = []
    for row in personal_square:
        letter_row = []
        for val in row:
            # Check if original (pre-offset) cell was a BDWH position
            original_val = val - offset
            if original_val in BDWH_POSITIONS:
                letter_row.append(f"{BDWH_POSITIONS[original_val]}({val})")
            else:
                letter_row.append(str(val))
        letter_grid.append(letter_row)

    # BDWH personal values (what B, D, W, H become after offset)
    personal_bdwh = {
        "ب (Ba)": 2 + offset,
        "د (Dal)": 4 + offset,
        "و (Waw)": 6 + offset,
        "ح (Ha)": 8 + offset,
    }

    return SystemResult(
        id="buduh",
        name="Buduh (بدوح — Personal Buduh Matrix)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic,
            "abjad_total": total,
            "abjad_root": root,
            "center_offset": offset,
            "personal_square": personal_square,
            "magic_constant": magic_constant,
            "letter_grid": letter_grid,
            "personal_bdwh": personal_bdwh,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Buduh بدوح: B=2, D=4, W=6, H=8 — even skeleton of Lo Shu.",
            "Personal offset shifts center to name's abjad root.",
            "Source: Pre-Islamic, codified in Shams al-Ma'arif.",
        ],
        question="Q3_PRACTICE"
    )
