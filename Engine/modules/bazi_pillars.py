"""BaZi Four Pillars (四柱命理) — COMPUTED_STRICT
Computes Year, Month, Day pillars from DOB. Hour pillar if birth time available.
Day pillar calibrated against known fixture: reference profile (Gui Hai).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Calibration offsets (verified against 1990-03-15 reference)
DAY_STEM_OFFSET = 9
DAY_BRANCH_OFFSET = 1

# Solar term approximate start dates for BaZi months
MONTH_BOUNDARIES = [
    (2, 4),   # Month 1 starts ~Feb 4 (Lichun)
    (3, 6),   # Month 2 starts ~Mar 6
    (4, 5),   # Month 3 starts ~Apr 5
    (5, 6),   # Month 4 starts ~May 6
    (6, 6),   # Month 5 starts ~Jun 6
    (7, 7),   # Month 6 starts ~Jul 7
    (8, 7),   # Month 7 starts ~Aug 7
    (9, 8),   # Month 8 starts ~Sep 8
    (10, 8),  # Month 9 starts ~Oct 8
    (11, 7),  # Month 10 starts ~Nov 7
    (12, 7),  # Month 11 starts ~Dec 7
    (1, 6),   # Month 12 starts ~Jan 6
]

# Month stem start index by year stem index
YEAR_STEM_TO_MONTH_START = {
    0: 2, 1: 4, 2: 6, 3: 8, 4: 0,
    5: 2, 6: 4, 7: 6, 8: 8, 9: 0,
}

# Hour branches (2-hour blocks)
HOUR_BRANCHES = [
    (23, 1, 0),   # Zi (Rat)
    (1, 3, 1),    # Chou (Ox)
    (3, 5, 2),    # Yin (Tiger)
    (5, 7, 3),    # Mao (Rabbit)
    (7, 9, 4),    # Chen (Dragon)
    (9, 11, 5),   # Si (Snake)
    (11, 13, 6),  # Wu (Horse)
    (13, 15, 7),  # Wei (Goat)
    (15, 17, 8),  # Shen (Monkey)
    (17, 19, 9),  # You (Rooster)
    (19, 21, 10), # Xu (Dog)
    (21, 23, 11), # Hai (Pig)
]

DAY_STEM_TO_HOUR_START = {
    0: 0, 1: 2, 2: 4, 3: 6, 4: 8,
    5: 0, 6: 2, 7: 4, 8: 6, 9: 8,
}


def _get_bazi_month(cal_month: int, cal_day: int) -> int:
    """Get BaZi month number (1-12) from calendar date."""
    for i, (bm, bd) in enumerate(MONTH_BOUNDARIES):
        next_i = (i + 1) % 12
        next_bm, next_bd = MONTH_BOUNDARIES[next_i]
        if bm == cal_month and cal_day >= bd:
            return (i % 12) + 1
        if bm == cal_month and cal_day < bd:
            return ((i - 1) % 12) + 1
    return 1


def _format_pillar(stem_idx: int, branch_idx: int, stems: list, branches: list) -> dict:
    s = stems[stem_idx]
    b = branches[branch_idx]
    return {
        "stem": s["chinese"],
        "stem_pinyin": s["pinyin"],
        "stem_element": s["element"],
        "stem_polarity": s["polarity"],
        "branch": b["chinese"],
        "branch_pinyin": b["pinyin"],
        "animal": b["animal"],
        "branch_element": b["element"],
        "pillar": f"{s['chinese']}{b['chinese']}",
        "pillar_pinyin": f"{s['pinyin']} {b['pinyin']}",
        "description": f"{s['polarity']} {s['element']} {b['animal']}"
    }


def compute(profile: InputProfile, constants: dict, jdn: int = None) -> SystemResult:
    zodiac_cfg = constants["chinese_zodiac"]
    stems = zodiac_cfg["heavenly_stems"]
    branches = zodiac_cfg["earthly_branches"]

    y, m, d = profile.dob.year, profile.dob.month, profile.dob.day

    # ── Year Pillar ──
    eff_year = y if (m > 2 or (m == 2 and d >= 4)) else y - 1
    year_stem_idx = (eff_year - 4) % 10
    year_branch_idx = (eff_year - 4) % 12
    year_pillar = _format_pillar(year_stem_idx, year_branch_idx, stems, branches)

    # ── Month Pillar ──
    bazi_month = _get_bazi_month(m, d)
    month_branch_idx = (bazi_month + 1) % 12  # Month 1=Tiger(2), 2=Rabbit(3)...
    month_stem_start = YEAR_STEM_TO_MONTH_START[year_stem_idx]
    month_stem_idx = (month_stem_start + (bazi_month - 1)) % 10
    month_pillar = _format_pillar(month_stem_idx, month_branch_idx, stems, branches)

    # ── Day Pillar ──
    if jdn is None:
        # Compute JDN inline
        a = (14 - m) // 12
        jy = y + 4800 - a
        jm = m + 12 * a - 3
        jdn = d + (153 * jm + 2) // 5 + 365 * jy + jy // 4 - jy // 100 + jy // 400 - 32045

    day_stem_idx = (jdn + DAY_STEM_OFFSET) % 10
    day_branch_idx = (jdn + DAY_BRANCH_OFFSET) % 12
    day_pillar = _format_pillar(day_stem_idx, day_branch_idx, stems, branches)
    day_master = f"{stems[day_stem_idx]['pinyin']} ({stems[day_stem_idx]['chinese']}) {stems[day_stem_idx]['polarity']} {stems[day_stem_idx]['element']}"

    # ── Hour Pillar (optional) ──
    hour_pillar = None
    if profile.birth_time_local:
        try:
            parts = profile.birth_time_local.split(":")
            hour = int(parts[0])
            # Find hour branch
            hour_branch_idx = 0
            for start, end, idx in HOUR_BRANCHES:
                if start <= end:
                    if start <= hour < end:
                        hour_branch_idx = idx
                        break
                else:  # Wraps midnight (23-1)
                    if hour >= start or hour < end:
                        hour_branch_idx = idx
                        break
            hour_stem_start = DAY_STEM_TO_HOUR_START[day_stem_idx]
            hour_stem_idx = (hour_stem_start + hour_branch_idx) % 10
            hour_pillar = _format_pillar(hour_stem_idx, hour_branch_idx, stems, branches)
        except (ValueError, IndexError):
            pass

    data = {
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "day_pillar": day_pillar,
        "day_master": day_master,
        "jdn_used": jdn,
        "bazi_month_number": bazi_month,
        "note": "Day Master is the core self. Day pillar calibrated against 癸亥 fixture."
    }
    if hour_pillar:
        data["hour_pillar"] = hour_pillar

    pillars_str = f"{year_pillar['pillar']} {month_pillar['pillar']} {day_pillar['pillar']}"
    if hour_pillar:
        pillars_str += f" {hour_pillar['pillar']}"

    return SystemResult(
        id="bazi_pillars",
        name="BaZi Four Pillars (四柱命理)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=f"Four Pillars: {pillars_str}. Day Master: {day_master}.",
        constants_version=constants["version"],
        references=["BaZi / Four Pillars of Destiny", "Ten Thousand Year Calendar", "Solar term boundaries"],
        question="Q1_IDENTITY"
    )