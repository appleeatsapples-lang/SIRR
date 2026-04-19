"""Taksir (Letter Permutation) — COMPUTED_STRICT
Classical Ilm al-Huruf algorithm: splits letters into odd/even positions,
recombines, repeats until original sequence reappears.
The resulting Satar (matrix) reveals hidden letter patterns.
Source: Kashf al-Asrar, early Jafr texts (10th-12th century)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def _taksir_cycle(letters: list[str]) -> list[list[str]]:
    """Run one full taksir cycle until original row reappears."""
    if len(letters) < 2:
        return [letters]

    original = list(letters)
    matrix = [original]
    current = list(letters)

    for _ in range(len(letters) * len(letters)):  # safety cap
        # Split: odd positions (0,2,4...) then even positions (1,3,5...)
        odd = [current[i] for i in range(0, len(current), 2)]
        even = [current[i] for i in range(1, len(current), 2)]
        current = odd + even

        if current == original:
            break
        matrix.append(list(current))

    return matrix


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    name_letters = [ch for ch in profile.arabic.replace(" ", "") if ch in abjad]

    matrix = _taksir_cycle(name_letters)
    depth = len(matrix)

    # Extract vertical columns (first letter of each row = the "hidden name" column)
    first_col = [row[0] for row in matrix]
    last_col = [row[-1] for row in matrix]

    # Compute abjad value of first column (hidden identity)
    hidden_value = sum(abjad.get(ch, 0) for ch in first_col)

    # Per-word breakdown of original
    words = profile.arabic.split()

    return SystemResult(
        id="taksir",
        name="Taksir (تكسير — Letter Permutation)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic,
            "letter_count": len(name_letters),
            "depth": depth,
            "matrix": ["".join(row) for row in matrix],
            "first_column": "".join(first_col),
            "first_column_value": hidden_value,
            "last_column": "".join(last_col),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Taksir: Odd/even split permutation (Zimam method).",
            "Source: Kashf al-Asrar, classical Jafr tradition.",
        ],
        question="Q1_IDENTITY"
    )
