"""Lo Shu Grid — COMPUTED_STRICT
Maps DOB digits into the 3x3 Lo Shu magic square to find
present numbers (strengths), missing numbers (gaps), and concentrations.
"""
from __future__ import annotations
from collections import Counter
from sirr_core.types import InputProfile, SystemResult

# Lo Shu grid positions (standard):
#  4 9 2
#  3 5 7
#  8 1 6
GRID_POSITIONS = {
    4: (0, 0), 9: (0, 1), 2: (0, 2),
    3: (1, 0), 5: (1, 1), 7: (1, 2),
    8: (2, 0), 1: (2, 1), 6: (2, 2),
}

ARROWS = {
    "determination": [4, 5, 6],    # diagonal top-left to bottom-right
    "intellect": [4, 9, 2],        # top row
    "emotional": [3, 5, 7],        # middle row
    "practical": [8, 1, 6],        # bottom row
    "thought": [4, 3, 8],          # left column
    "will": [9, 5, 1],             # center column
    "action": [2, 7, 6],           # right column
    "spirituality": [2, 5, 8],     # diagonal top-right to bottom-left
}


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    # Extract all digits from DOB
    dob_str = profile.dob.strftime("%d%m%Y")
    digits = [int(d) for d in dob_str if d != '0']  # 0 has no grid position

    counts = Counter(digits)

    # Build grid display
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for digit, count in counts.items():
        if digit in GRID_POSITIONS:
            r, c = GRID_POSITIONS[digit]
            grid[r][c] = count

    # Missing and concentrated
    present = sorted(set(digits))
    missing = sorted(set(range(1, 10)) - set(digits))
    concentrated = {d: c for d, c in counts.items() if c >= 2}

    # Check arrows (all digits in arrow present)
    active_arrows = []
    for name, nums in ARROWS.items():
        if all(n in present for n in nums):
            active_arrows.append(name)

    return SystemResult(
        id="lo_shu_grid",
        name="Lo Shu Birth Grid",
        certainty="COMPUTED_STRICT",
        data={
            "dob_digits": dob_str,
            "digit_counts": dict(counts),
            "grid": grid,
            "present": present,
            "missing": missing,
            "concentrated": concentrated,
            "active_arrows": active_arrows,
            "total_digits": len(digits),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Lo Shu Grid: DOB digits mapped to 3x3 magic square positions"],
        question="Q3_GAPS"
    )
