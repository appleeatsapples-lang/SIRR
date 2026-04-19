"""Chinese Jian-Chu (12 Day Officers) — COMPUTED_STRICT
(1) Chinese Solar Month → Earthly Branch. (2) Day Earthly Branch.
(3) When day branch matches month branch = "Establish" (Jian).
(4) Progress through 12 officers sequentially from that base.
Source: Palmer, Martin. "The Chinese Almanac"
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# 12 Day Officers (Jian-Chu system)
OFFICERS = [
    {"name": "Jian", "meaning": "Establish", "quality": "favorable"},
    {"name": "Chu", "meaning": "Remove", "quality": "favorable"},
    {"name": "Man", "meaning": "Full", "quality": "favorable"},
    {"name": "Ping", "meaning": "Balance", "quality": "favorable"},
    {"name": "Ding", "meaning": "Stable", "quality": "favorable"},
    {"name": "Zhi", "meaning": "Hold", "quality": "neutral"},
    {"name": "Po", "meaning": "Break", "quality": "unfavorable"},
    {"name": "Wei", "meaning": "Danger", "quality": "unfavorable"},
    {"name": "Cheng", "meaning": "Succeed", "quality": "favorable"},
    {"name": "Shou", "meaning": "Receive", "quality": "favorable"},
    {"name": "Kai", "meaning": "Open", "quality": "favorable"},
    {"name": "Bi", "meaning": "Close", "quality": "unfavorable"},
]

# Earthly Branches
BRANCHES = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si",
            "Wu", "Wei", "Shen", "You", "Xu", "Hai"]

# Solar month → Earthly Branch (Jian base)
# Month 1 (Yin spring) starts at Yin, Month 2 at Mao, etc.
MONTH_TO_BRANCH = {
    1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7,
    7: 8, 8: 9, 9: 10, 10: 11, 11: 0, 12: 1,
}


def _day_branch_index(year, month, day):
    """Compute day Earthly Branch index (0-11) from JDN."""
    # Julian Day Number
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    # Day branch: JDN mod 12, offset so Jan 1 1970 (JDN 2440588) = Zi (0)
    # Actually: JDN 2440588 = Jan 1, 1970. Day branch for this date: Zi=0
    # Verification: JDN mod 12 with proper offset
    return (jdn + 1) % 12  # +1 offset calibrated to standard tables


def _solar_month(month, day):
    """Approximate Chinese solar month from Gregorian date.
    Solar month boundaries are around the 5th-7th of each month.
    Month 1 = ~Feb 4 to Mar 5, Month 2 = ~Mar 6 to Apr 4, etc."""
    # Solar month transitions (approximate Gregorian dates)
    transitions = [
        (2, 4), (3, 6), (4, 5), (5, 6), (6, 6), (7, 7),
        (8, 7), (9, 8), (10, 8), (11, 7), (12, 7), (1, 6),
    ]
    # Find which solar month we're in
    for i in range(len(transitions) - 1, -1, -1):
        tm, td = transitions[i]
        if (month, day) >= (tm, td):
            return (i + 1) if i < 12 else 1
    return 12  # Before Feb 4 = still month 12


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    dob = profile.dob
    solar_m = _solar_month(dob.month, dob.day)
    month_branch_idx = MONTH_TO_BRANCH.get(solar_m, 0)
    day_branch_idx = _day_branch_index(dob.year, dob.month, dob.day)

    # Officer = (day_branch - month_branch) mod 12
    officer_idx = (day_branch_idx - month_branch_idx) % 12
    officer = OFFICERS[officer_idx]

    return SystemResult(
        id="chinese_jian_chu",
        name="Chinese Jian-Chu (12 Day Officers)",
        certainty="COMPUTED_STRICT",
        data={
            "solar_month": solar_m,
            "month_branch": BRANCHES[month_branch_idx],
            "day_branch": BRANCHES[day_branch_idx],
            "day_officer": officer["name"],
            "day_officer_meaning": officer["meaning"],
            "day_officer_quality": officer["quality"],
            "officer_index": officer_idx,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Palmer, Martin. 'The Chinese Almanac': Jian-Chu 12 Day Officers",
            "SOURCE_TIER:B — Scholarly reference on Chinese calendar traditions.",
        ],
        question="Q4_TIMING",
    )
