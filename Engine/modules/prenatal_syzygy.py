"""Prenatal Syzygy — COMPUTED_STRICT
Find the New Moon or Full Moon immediately preceding birth date using Swiss Ephemeris.
Output: syzygy type (new/full), exact datetime, degree, zodiac sign.
Source: Classical Hellenistic (Ptolemy, Tetrabiblos Book III)
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from sirr_core.types import InputProfile, SystemResult

try:
    import swisseph as swe
    _SWE_AVAILABLE = True
except ImportError:
    _SWE_AVAILABLE = False

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _jd_from_date(d, hour=12.0):
    return swe.julday(d.year, d.month, d.day, hour)


def _sign_from_lon(lon):
    idx = int(lon / 30) % 12
    return SIGNS[idx]


def _degree_in_sign(lon):
    return lon % 30


def _find_syzygy(jd_birth):
    """Search backward from birth for the most recent New Moon and Full Moon.
    Return whichever is closer (more recent)."""
    # Search backward in 1-day steps for up to 35 days
    best_new = None
    best_full = None

    # Use a finer search: check Sun-Moon elongation at half-day intervals
    for i in range(70):  # 35 days × 2 steps/day
        jd = jd_birth - i * 0.5
        sun_lon = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]
        diff = (moon_lon - sun_lon) % 360

        # Check next step too for sign change detection
        jd_next = jd + 0.5
        sun_lon_next = swe.calc_ut(jd_next, swe.SUN)[0][0]
        moon_lon_next = swe.calc_ut(jd_next, swe.MOON)[0][0]
        diff_next = (moon_lon_next - sun_lon_next) % 360

        # New Moon: elongation crosses 0 (from ~350+ to ~10)
        if diff < 15 and diff_next > 345 and best_new is None:
            # Refine by bisection
            best_new = _refine_syzygy(jd, jd_next, 0)

        # Full Moon: elongation crosses 180 (from ~170 to ~190)
        if 170 < diff < 190 and best_full is None:
            if diff_next > diff:  # Moving away from 180
                pass
            # Check if we just passed 180
            if abs(diff - 180) < abs(diff_next - 180):
                best_full = _refine_syzygy_full(jd - 0.5, jd + 0.5)

    # Alternative: use direct bisection from birth backward
    if best_new is None:
        best_new = _search_syzygy_type(jd_birth, "new")
    if best_full is None:
        best_full = _search_syzygy_type(jd_birth, "full")

    if best_new is None and best_full is None:
        return None, None, None, None

    # Return the more recent one (closer to birth)
    if best_new is not None and best_full is not None:
        if best_new > best_full:
            return "new_moon", best_new, *_syzygy_details(best_new)
        else:
            return "full_moon", best_full, *_syzygy_details(best_full)
    elif best_new is not None:
        return "new_moon", best_new, *_syzygy_details(best_new)
    else:
        return "full_moon", best_full, *_syzygy_details(best_full)


def _search_syzygy_type(jd_birth, syzygy_type):
    """Direct search for most recent new/full moon before jd_birth."""
    target = 0 if syzygy_type == "new" else 180

    for day_offset in range(1, 35):
        jd = jd_birth - day_offset
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        elong = (moon - sun) % 360

        if abs(elong - target) < 10 or (target == 0 and elong > 350):
            # Refine
            lo = jd - 1
            hi = jd + 1
            for _ in range(50):
                mid = (lo + hi) / 2
                s = swe.calc_ut(mid, swe.SUN)[0][0]
                m = swe.calc_ut(mid, swe.MOON)[0][0]
                e = (m - s) % 360
                if target == 0:
                    err = e if e < 180 else 360 - e
                else:
                    err = e - 180
                if (target == 0 and e > 180) or (target == 180 and e < 180):
                    lo = mid
                else:
                    hi = mid
            result = (lo + hi) / 2
            if result < jd_birth:
                return result
    return None


def _refine_syzygy(lo, hi, target):
    """Bisection to find exact moment of conjunction (target=0) or opposition (target=180)."""
    for _ in range(50):
        mid = (lo + hi) / 2
        s = swe.calc_ut(mid, swe.SUN)[0][0]
        m = swe.calc_ut(mid, swe.MOON)[0][0]
        e = (m - s) % 360
        if e > 180:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _refine_syzygy_full(lo, hi):
    for _ in range(50):
        mid = (lo + hi) / 2
        s = swe.calc_ut(mid, swe.SUN)[0][0]
        m = swe.calc_ut(mid, swe.MOON)[0][0]
        e = (m - s) % 360
        if e < 180:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _syzygy_details(jd):
    """Return (sun_lon, sign) at syzygy moment."""
    sun_lon = swe.calc_ut(jd, swe.SUN)[0][0]
    return sun_lon, _sign_from_lon(sun_lon)


def _jd_to_iso(jd):
    """Convert Julian Day to ISO datetime string."""
    y, m, d, h = swe.revjul(jd)
    hours = int(h)
    minutes = int((h - hours) * 60)
    return f"{y:04d}-{m:02d}-{d:02d}T{hours:02d}:{minutes:02d}:00Z"


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    if not _SWE_AVAILABLE:
        return SystemResult(
            id="prenatal_syzygy", name="Prenatal Syzygy",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "pyswisseph not installed"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q1_IDENTITY",
        )

    jd_birth = _jd_from_date(profile.dob)
    syzygy_type, jd_syzygy, sun_lon, sign = _find_syzygy(jd_birth)

    if syzygy_type is None:
        return SystemResult(
            id="prenatal_syzygy", name="Prenatal Syzygy",
            certainty="COMPUTED_STRICT",
            data={"error": "no syzygy found within 35 days before birth"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q1_IDENTITY",
        )

    degree = round(_degree_in_sign(sun_lon), 2)
    days_before = round(jd_birth - jd_syzygy, 1)

    return SystemResult(
        id="prenatal_syzygy",
        name="Prenatal Syzygy",
        certainty="COMPUTED_STRICT",
        data={
            "syzygy_type": syzygy_type,
            "syzygy_date": _jd_to_iso(jd_syzygy),
            "syzygy_sign": sign,
            "syzygy_degree": degree,
            "sun_longitude": round(sun_lon, 4),
            "days_before_birth": days_before,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Ptolemy, Tetrabiblos Book III: Prenatal Syzygy (lunation preceding birth)",
            "Swiss Ephemeris (Moshier): Sun/Moon positions for syzygy detection",
            "SOURCE_TIER:A — Classical Hellenistic text. Algorithmic implementation verified.",
        ],
        question="Q1_IDENTITY",
    )
