"""Larger Awfaq — 4×4 and 5×5 Magic Squares — COMPUTED_STRICT
Generates personalized 4×4 and 5×5 magic squares from the abjad total,
with symmetry analysis and center-weight comparison.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def _make_4x4(n: int) -> list[list[int]]:
    """Generate a 4×4 magic square with magic constant = n.
    Uses the Dürer-type construction with offset from standard n=34 square."""
    # Standard 4×4 magic square (constant = 34)
    base = [
        [16, 3, 2, 13],
        [5, 10, 11, 8],
        [9, 6, 7, 12],
        [4, 15, 14, 1],
    ]
    offset = (n - 34) / 4
    return [[cell + offset for cell in row] for row in base]


def _make_5x5(n: int) -> list[list[int]]:
    """Generate a 5×5 magic square with magic constant = n.
    Uses the Siamese method offset from standard n=65 square."""
    # Standard 5×5 magic square (constant = 65)
    base = [
        [17, 24, 1, 8, 15],
        [23, 5, 7, 14, 16],
        [4, 6, 13, 20, 22],
        [10, 12, 19, 21, 3],
        [11, 18, 25, 2, 9],
    ]
    offset = (n - 65) / 5
    return [[cell + offset for cell in row] for row in base]


def _check_symmetry(sq: list[list[int]]) -> str:
    """Check if square has diagonal symmetry."""
    n = len(sq)
    # Check if center-symmetric (180° rotation)
    is_center_sym = True
    for i in range(n):
        for j in range(n):
            if abs(sq[i][j] + sq[n-1-i][n-1-j] - sq[0][0] - sq[n-1][n-1]) > 0.01:
                is_center_sym = False
                break
    return "center_symmetric" if is_center_sym else "asymmetric"


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    name = profile.arabic.replace(" ", "")
    total = sum(abjad.get(ch, 0) for ch in name)
    root = reduce_number(total, keep_masters=())

    # 3×3 from existing wafq (for comparison)
    base_3x3 = constants["wafq"]["loshu_base"]
    offset_3x3 = (total // 3) - 5
    sq_3x3 = [[cell + offset_3x3 for cell in row] for row in base_3x3]
    constant_3x3 = sum(sq_3x3[0])

    # 4×4: constant = total (each row sums to total)
    # For a 4×4, we want the constant to be total/4 per cell average
    # But magic constant = n means row sum = n
    # Use abjad root * a scaling factor for meaningful constant
    constant_4x4 = total  # Row sum = total (each row of 4 sums to the abjad total)
    sq_4x4 = _make_4x4(constant_4x4)
    center_4x4 = round((sq_4x4[1][1] + sq_4x4[1][2] + sq_4x4[2][1] + sq_4x4[2][2]) / 4, 2)

    # 5×5: constant = total
    constant_5x5 = total
    sq_5x5 = _make_5x5(constant_5x5)
    center_5x5 = sq_5x5[2][2]  # True center of 5×5

    # Buduh check: does the 3×3 center match the root?
    buduh_center = sq_3x3[1][1]
    buduh_matches_root = (reduce_number(buduh_center, keep_masters=()) == root)

    # Constant progression: 3×3 → 4×4 → 5×5
    constant_progression = [constant_3x3, constant_4x4, constant_5x5]

    return SystemResult(
        id="larger_awfaq",
        name="Larger Awfaq (الأوفاق الكبرى)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "abjad_total": total,
            "abjad_root": root,
            "square_3x3": sq_3x3,
            "constant_3x3": constant_3x3,
            "center_3x3": buduh_center,
            "square_4x4": sq_4x4,
            "constant_4x4": constant_4x4,
            "center_4x4": center_4x4,
            "symmetry_4x4": _check_symmetry(sq_4x4),
            "square_5x5": sq_5x5,
            "constant_5x5": constant_5x5,
            "center_5x5": center_5x5,
            "symmetry_5x5": _check_symmetry(sq_5x5),
            "buduh_matches_root": buduh_matches_root,
            "constant_progression": constant_progression,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Al-Buni — Shams al-Ma'arif (wafq construction)",
            "Dürer 4×4 construction adapted for abjad",
            "Siamese method for 5×5 (de la Loubère)",
        ],
        question="Q1_IDENTITY"
    )
