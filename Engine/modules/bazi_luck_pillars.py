"""BaZi Luck Pillars / Da Yun (大运) — COMPUTED_STRICT
Computes 10-year luck pillars by stepping through the 60 Jiazi cycle
from the Month Pillar. Direction depends on gender + Year Stem polarity.
Onset age from DOB to nearest Jie (sectional solar term), divided by 3.
If gender not provided, outputs BOTH male and female pillar sets.

NOTE: Solar term dates are fixed approximations. For STRICT ephemeris
upgrade, use actual solar longitude calculation per birth year.

Source: Standard BaZi practice (Zi Ping method).
"""
from __future__ import annotations
from datetime import date
from sirr_core.types import InputProfile, SystemResult

# Approximate Jie (sectional) solar term start dates
# These are the 12 Jie boundaries that start each BaZi month
SOLAR_TERMS = [
    (2, 4),   # Lichun (Start of Spring) — Month 1
    (3, 6),   # Jingzhe — Month 2
    (4, 5),   # Qingming — Month 3
    (5, 6),   # Lixia — Month 4
    (6, 6),   # Mangzhong — Month 5
    (7, 7),   # Xiaoshu — Month 6
    (8, 7),   # Liqiu — Month 7
    (9, 8),   # Bailu — Month 8
    (10, 8),  # Hanlu — Month 9
    (11, 7),  # Lidong — Month 10
    (12, 7),  # Daxue — Month 11
    (1, 6),   # Xiaohan — Month 12
]


def _days_between(d1: date, d2: date) -> int:
    return abs((d2 - d1).days)


def _next_solar_term(dob: date) -> date:
    """Find the next Jie solar term date after DOB."""
    y = dob.year
    for year_offset in range(0, 2):
        for m, d in SOLAR_TERMS:
            try:
                term_date = date(y + year_offset, m, d)
            except ValueError:
                continue
            if term_date > dob:
                return term_date
    return date(y + 1, 2, 4)


def _prev_solar_term(dob: date) -> date:
    """Find the previous Jie solar term date before or on DOB."""
    y = dob.year
    best = None
    for year_offset in range(1, -1, -1):
        for m, d in SOLAR_TERMS:
            try:
                term_date = date(y - year_offset, m, d)
            except ValueError:
                continue
            if term_date <= dob:
                if best is None or term_date > best:
                    best = term_date
    return best or date(y, 1, 6)


def _format_pillar(stem_idx: int, branch_idx: int, stems: list, branches: list) -> dict:
    s = stems[stem_idx]
    b = branches[branch_idx]
    return {
        "stem": s["chinese"],
        "stem_en": s["pinyin"],
        "stem_element": s["element"],
        "branch": b["chinese"],
        "branch_en": b["pinyin"],
        "animal": b["animal"],
        "branch_element": b["element"],
        "pillar": f"{s['chinese']}{b['chinese']}",
    }


def _generate_pillars(month_stem_idx, month_branch_idx, onset_age, forward, stems, branches):
    """Generate 8 luck pillars stepping through Jiazi cycle."""
    pillars = []
    step = 1 if forward else -1
    for i in range(8):
        s_idx = (month_stem_idx + step * (i + 1)) % 10
        b_idx = (month_branch_idx + step * (i + 1)) % 12
        age_start = onset_age + i * 10
        age_end = age_start + 9
        pillar = _format_pillar(s_idx, b_idx, stems, branches)
        pillar["age_start"] = age_start
        pillar["age_end"] = age_end
        pillars.append(pillar)
    return pillars


def _compute_onset_and_pillars(dob, forward, month_stem_idx, month_branch_idx, stems, branches):
    """Compute onset age and generate pillars for a given direction."""
    if forward:
        target_term = _next_solar_term(dob)
    else:
        target_term = _prev_solar_term(dob)
    days_to_term = _days_between(dob, target_term)
    onset_age = round(days_to_term / 3)
    pillars = _generate_pillars(month_stem_idx, month_branch_idx, onset_age, forward, stems, branches)
    return onset_age, pillars


def compute(profile: InputProfile, constants: dict, bazi_data: dict = None) -> SystemResult:
    if bazi_data is None:
        return SystemResult(
            id="bazi_luck_pillars",
            name="BaZi Luck Pillars / Da Yun (大运)",
            certainty="NEEDS_INPUT",
            data={"error": "bazi_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING"
        )

    zodiac_cfg = constants["chinese_zodiac"]
    stems = zodiac_cfg["heavenly_stems"]
    branches = zodiac_cfg["earthly_branches"]

    month_stem_ch = bazi_data["month_pillar"]["stem"]
    month_branch_ch = bazi_data["month_pillar"]["branch"]
    month_stem_idx = next(i for i, s in enumerate(stems) if s["chinese"] == month_stem_ch)
    month_branch_idx = next(i for i, b in enumerate(branches) if b["chinese"] == month_branch_ch)

    year_stem_polarity = bazi_data["year_pillar"]["stem_polarity"]
    is_yang_year = (year_stem_polarity == "Yang")

    gender = getattr(profile, "gender", None)
    dob = profile.dob

    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1

    if gender:
        # Single-gender mode
        is_male = gender.lower() == "male"
        forward = (is_male and is_yang_year) or (not is_male and not is_yang_year)
        onset_age, pillars = _compute_onset_and_pillars(
            dob, forward, month_stem_idx, month_branch_idx, stems, branches)

        current_pillar = None
        for p in pillars:
            if p["age_start"] <= age <= p["age_end"]:
                current_pillar = p["pillar"]
                break

        return SystemResult(
            id="bazi_luck_pillars",
            name="BaZi Luck Pillars / Da Yun (大运)",
            certainty="COMPUTED_STRICT",
            data={
                "gender": gender,
                "direction": "forward" if forward else "backward",
                "year_stem_polarity": year_stem_polarity,
                "onset_age": onset_age,
                "pillars": pillars,
                "current_luck_pillar": current_pillar,
                "age": age,
            },
            interpretation=None,
            constants_version=constants["version"],
            references=["BaZi Da Yun (大运) — 10-year luck pillar cycle", "Zi Ping method"],
            question="Q4_TIMING"
        )
    else:
        # No gender provided — output both sets
        fwd_m = is_yang_year      # male forward if yang year
        fwd_f = not is_yang_year  # female forward if yin year

        onset_m, pillars_m = _compute_onset_and_pillars(
            dob, fwd_m, month_stem_idx, month_branch_idx, stems, branches)
        onset_f, pillars_f = _compute_onset_and_pillars(
            dob, fwd_f, month_stem_idx, month_branch_idx, stems, branches)

        cur_m = next((p["pillar"] for p in pillars_m if p["age_start"] <= age <= p["age_end"]), None)
        cur_f = next((p["pillar"] for p in pillars_f if p["age_start"] <= age <= p["age_end"]), None)

        return SystemResult(
            id="bazi_luck_pillars",
            name="BaZi Luck Pillars / Da Yun (大运)",
            certainty="COMPUTED_STRICT",
            data={
                "gender": "unknown",
                "year_stem_polarity": year_stem_polarity,
                "age": age,
                "male": {
                    "direction": "forward" if fwd_m else "backward",
                    "onset_age": onset_m,
                    "pillars": pillars_m,
                    "current_luck_pillar": cur_m,
                },
                "female": {
                    "direction": "forward" if fwd_f else "backward",
                    "onset_age": onset_f,
                    "pillars": pillars_f,
                    "current_luck_pillar": cur_f,
                },
                "note": "Gender not provided — showing both male and female luck pillar sets",
            },
            interpretation=None,
            constants_version=constants["version"],
            references=["BaZi Da Yun (大运) — 10-year luck pillar cycle", "Zi Ping method"],
            question="Q4_TIMING"
        )
