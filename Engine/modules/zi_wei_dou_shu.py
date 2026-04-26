"""Zi Wei Dou Shu (紫微斗數 — Purple Star Astrology)
Chinese fate-charting system based on lunar calendar + birth hour.
Computes Ming Gong (Life Palace), Shen Gong (Body Palace), Zi Wei star placement,
12 palace assignments, and Da Yun direction.

Gated on birth_time_local — returns NEEDS_INPUT when absent.

Source: Chen Xiyi (陳希夷), Zi Wei Dou Shu Quan Shu — Tier A.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

HOUR_BRANCHES = ['Zi', 'Chou', 'Yin', 'Mao', 'Chen', 'Si',
                 'Wu', 'Wei', 'Shen', 'You', 'Xu', 'Hai']
HOUR_CHINESE = ['子', '丑', '寅', '卯', '辰', '巳',
                '午', '未', '申', '酉', '戌', '亥']

YEAR_STEMS = ['Jia', 'Yi', 'Bing', 'Ding', 'Wu', 'Ji', 'Geng', 'Xin', 'Ren', 'Gui']
STEM_CHINESE = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
YANG_STEMS = {'Jia', 'Bing', 'Wu', 'Geng', 'Ren'}

PALACE_NAMES = [
    "Life (命宮)", "Siblings (兄弟)", "Spouse (夫妻)",
    "Children (子女)", "Wealth (財帛)", "Health (疾厄)",
    "Travel (遷移)", "Friends (交友)", "Career (官祿)",
    "Property (田宅)", "Happiness (福德)", "Parents (父母)",
]

# Zi Wei star placement: lunar day -> 0-based branch index
ZI_WEI_TABLE = {
    1: 2,  2: 2,  3: 2,  4: 2,  5: 2,
    6: 3,  7: 3,  8: 4,  9: 3,  10: 4,
    11: 4, 12: 5, 13: 4, 14: 5, 15: 5,
    16: 6, 17: 5, 18: 6, 19: 6, 20: 7,
    21: 6, 22: 7, 23: 7, 24: 8, 25: 7,
    26: 8, 27: 9, 28: 8, 29: 9, 30: 10,
}

# ── Chinese Lunar Calendar: New Moon dates for lunar month 1 (Chinese New Year) ──
# Used to convert Gregorian DOB to lunar month/day via swisseph new moon search.


def _get_lunar_date_swisseph(year: int, month: int, day: int):
    """Compute Chinese lunar month and day using swisseph new moon search."""
    try:
        import swisseph as swe
        swe.set_ephe_path(None)

        # Get JD for the birth date at noon UT
        jd_birth = swe.julday(year, month, day, 12.0)

        # Search backward for the most recent new moon before birth
        # New moon = Sun-Moon conjunction (elongation = 0)
        # Walk back up to 35 days to find it
        jd_search = jd_birth
        prev_new_moon = None
        for _ in range(40):
            sun = swe.calc_ut(jd_search, swe.SUN)[0][0]
            moon = swe.calc_ut(jd_search, swe.MOON)[0][0]
            elong = (moon - sun) % 360
            if elong > 180:
                elong -= 360
            if abs(elong) < 8:  # close to new moon, refine
                # Binary search refinement
                jd_lo, jd_hi = jd_search - 2, jd_search + 2
                for _ in range(50):
                    jd_mid = (jd_lo + jd_hi) / 2
                    s = swe.calc_ut(jd_mid, swe.SUN)[0][0]
                    m = swe.calc_ut(jd_mid, swe.MOON)[0][0]
                    e = (m - s) % 360
                    if e > 180:
                        e -= 360
                    if e < 0:
                        jd_lo = jd_mid
                    else:
                        jd_hi = jd_mid
                prev_new_moon = (jd_lo + jd_hi) / 2
                break
            jd_search -= 1

        if prev_new_moon is None:
            return None, None

        # Lunar day = days since new moon + 1
        lunar_day = int(jd_birth - prev_new_moon) + 1
        if lunar_day < 1:
            lunar_day = 1
        if lunar_day > 30:
            lunar_day = 30

        # Determine lunar month by counting new moons from Chinese New Year
        # Find the new moon of Chinese New Year (month 1)
        # Chinese New Year is the 2nd new moon after winter solstice
        # Approximate: search backward from Feb 20 of birth year
        jd_feb = swe.julday(year, 2, 20, 12.0)
        cny_new_moon = None
        jd_s = jd_feb
        for _ in range(60):
            sun = swe.calc_ut(jd_s, swe.SUN)[0][0]
            moon_l = swe.calc_ut(jd_s, swe.MOON)[0][0]
            elong = (moon_l - sun) % 360
            if elong > 180:
                elong -= 360
            if abs(elong) < 8:
                jd_lo2, jd_hi2 = jd_s - 2, jd_s + 2
                for _ in range(50):
                    jd_mid2 = (jd_lo2 + jd_hi2) / 2
                    s2 = swe.calc_ut(jd_mid2, swe.SUN)[0][0]
                    m2 = swe.calc_ut(jd_mid2, swe.MOON)[0][0]
                    e2 = (m2 - s2) % 360
                    if e2 > 180:
                        e2 -= 360
                    if e2 < 0:
                        jd_lo2 = jd_mid2
                    else:
                        jd_hi2 = jd_mid2
                candidate = (jd_lo2 + jd_hi2) / 2
                # CNY new moon should be between Jan 21 and Feb 21
                cy, cm, cd, _ = swe.revjul(candidate)
                if cm == 1 and cd >= 21 or cm == 2 and cd <= 21:
                    cny_new_moon = candidate
                    break
            jd_s -= 1

        if cny_new_moon is None:
            # Fallback: use known CNY dates
            return None, None

        # Count synodic months from CNY new moon to birth's new moon
        lunar_month = round((prev_new_moon - cny_new_moon) / 29.53) + 1
        if lunar_month < 1:
            # Birth is before CNY — belongs to previous year's month 11 or 12
            # Search from previous year's CNY
            jd_prev_feb = swe.julday(year - 1, 2, 20, 12.0)
            prev_cny = None
            jd_s2 = jd_prev_feb
            for _ in range(60):
                sun = swe.calc_ut(jd_s2, swe.SUN)[0][0]
                moon_l = swe.calc_ut(jd_s2, swe.MOON)[0][0]
                elong = (moon_l - sun) % 360
                if elong > 180:
                    elong -= 360
                if abs(elong) < 8:
                    jd_lo3, jd_hi3 = jd_s2 - 2, jd_s2 + 2
                    for _ in range(50):
                        jd_mid3 = (jd_lo3 + jd_hi3) / 2
                        s3 = swe.calc_ut(jd_mid3, swe.SUN)[0][0]
                        m3 = swe.calc_ut(jd_mid3, swe.MOON)[0][0]
                        e3 = (m3 - s3) % 360
                        if e3 > 180:
                            e3 -= 360
                        if e3 < 0:
                            jd_lo3 = jd_mid3
                        else:
                            jd_hi3 = jd_mid3
                    prev_cny = (jd_lo3 + jd_hi3) / 2
                    break
                jd_s2 -= 1
            if prev_cny:
                lunar_month = round((prev_new_moon - prev_cny) / 29.53) + 1

        if lunar_month < 1:
            lunar_month = 12
        if lunar_month > 12:
            lunar_month = 12  # Intercalary month capped

        return lunar_month, lunar_day
    except ImportError:
        return None, None


# ── Fallback: Known lunar dates for calibration ──
# Pre-computed via astronomical new moon tables
# Populated lazily from local config; do not hardcode personal dates here.
_KNOWN_LUNAR = {
    # (year, month, day) -> (lunar_month, lunar_day)
}


def _get_hour_branch_idx(birth_time_local: str) -> int:
    """Returns 0-based index (Zi=0) for the 2-hour period."""
    h, m = map(int, birth_time_local.split(':'))
    if h == 23 or h < 1:
        return 0  # Zi
    return min((h - 1) // 2 + 1, 11)


def _get_year_stem(year: int) -> str:
    return YEAR_STEMS[(year - 4) % 10]


def _get_year_branch(year: int) -> str:
    return HOUR_BRANCHES[(year - 4) % 12]


def _format_branch(idx: int) -> str:
    return f"{HOUR_BRANCHES[idx]} ({HOUR_CHINESE[idx]})"


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    if not profile.birth_time_local:
        return SystemResult(
            id="zi_wei_dou_shu",
            name="Zi Wei Dou Shu (紫微斗數 — Purple Star Astrology)",
            certainty="NEEDS_INPUT",
            data={"applicable": False, "reason": "birth_time_local required for Ming Gong placement"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    dob = profile.dob
    year = dob.year

    # Step 1: Chinese lunar calendar
    lunar_month, lunar_day = _get_lunar_date_swisseph(year, dob.month, dob.day)

    # Fallback to known table if swisseph failed
    if lunar_month is None or lunar_day is None:
        key = (year, dob.month, dob.day)
        if key in _KNOWN_LUNAR:
            lunar_month, lunar_day = _KNOWN_LUNAR[key]
        else:
            return SystemResult(
                id="zi_wei_dou_shu",
                name="Zi Wei Dou Shu (紫微斗數 — Purple Star Astrology)",
                certainty="NEEDS_INPUT",
                data={"applicable": False, "reason": "Could not determine Chinese lunar date"},
                interpretation=None,
                constants_version=constants["version"],
                references=[],
                question="Q4_TIMING",
            )

    # Step 2: Hour branch
    hour_idx = _get_hour_branch_idx(profile.birth_time_local)

    # Step 3: Ming Gong (Life Palace)
    month_branch = (lunar_month + 1) % 12
    ming_gong = (month_branch - hour_idx) % 12

    # Step 4: Shen Gong (Body Palace)
    shen_gong = (month_branch + hour_idx) % 12

    # Step 5: Zi Wei star placement
    clamped_day = max(1, min(30, lunar_day))
    zi_wei_branch = ZI_WEI_TABLE[clamped_day]

    # Step 6: 12 palace assignments
    palaces = {}
    for i, name in enumerate(PALACE_NAMES):
        branch = (ming_gong + i) % 12
        palaces[name] = _format_branch(branch)

    # Find which palace Zi Wei and Shen Gong land in
    zi_wei_palace_name = PALACE_NAMES[(zi_wei_branch - ming_gong) % 12]
    shen_gong_palace_name = PALACE_NAMES[(shen_gong - ming_gong) % 12]

    # Step 7: Year pillar and Da Yun direction
    stem = _get_year_stem(year)
    stem_idx = (year - 4) % 10
    branch = _get_year_branch(year)
    branch_idx = (year - 4) % 12

    is_male = (profile.gender or "male") == "male"
    is_yang = stem in YANG_STEMS
    da_yun_forward = (is_male and is_yang) or (not is_male and not is_yang)

    year_pillar = f"{stem} {branch} ({STEM_CHINESE[stem_idx]}{HOUR_CHINESE[branch_idx]})"

    data = {
        "applicable": True,
        "year_pillar": year_pillar,
        "year_stem": f"{stem} ({STEM_CHINESE[stem_idx]})",
        "year_branch": f"{branch} ({HOUR_CHINESE[branch_idx]})",
        "lunar_month": lunar_month,
        "lunar_day": lunar_day,
        "hour_branch": _format_branch(hour_idx),
        "ming_gong": _format_branch(ming_gong),
        "ming_gong_domain": "Life/Destiny Palace",
        "shen_gong": _format_branch(shen_gong),
        "shen_gong_domain": f"{shen_gong_palace_name}",
        "zi_wei_palace": _format_branch(zi_wei_branch),
        "zi_wei_domain": f"{zi_wei_palace_name}",
        "da_yun_direction": "forward (顺行)" if da_yun_forward else "reverse (逆行)",
        "palaces": palaces,
        "note": (
            f"Purple Star (Zi Wei) in {zi_wei_palace_name}. "
            f"Life Palace {_format_branch(ming_gong)}. "
            f"Body Palace {_format_branch(shen_gong)} ({shen_gong_palace_name}). "
            f"Da Yun advances {'forward' if da_yun_forward else 'reverse'}."
        ),
    }

    interp = (
        f"Life Palace in {_format_branch(ming_gong)}. "
        f"Zi Wei star in {_format_branch(zi_wei_branch)} palace ({zi_wei_palace_name}). "
        f"Body palace in {_format_branch(shen_gong)} ({shen_gong_palace_name}). "
        f"Da Yun cycles advance {'forward' if da_yun_forward else 'reverse'} — "
        f"starting from month pillar, each major limit = 10 years."
    )

    return SystemResult(
        id="zi_wei_dou_shu",
        name="Zi Wei Dou Shu (紫微斗數 — Purple Star Astrology)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interp,
        constants_version=constants["version"],
        references=[
            "Chen Xiyi (陳希夷), Zi Wei Dou Shu Quan Shu — Ming Gong formula",
            "Zi Wei Table: lunar day → Purple Star palace placement",
            "Da Yun direction: Yang male = forward, Yin male = reverse",
        ],
        question="Q4_TIMING",
    )
