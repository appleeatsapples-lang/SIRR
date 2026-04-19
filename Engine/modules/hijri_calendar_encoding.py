"""Hijri Calendar Encoding — COMPUTED_STRICT
Digit-level analysis of the Hijri birth date: year digit sum,
prime factorization, month significance, day patterns.
Extends the hijri module with structural number analysis.
"""
from __future__ import annotations
import math
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

try:
    from hijri_converter import Hijri, Gregorian
    _HAS_HIJRI = True
except ImportError:
    _HAS_HIJRI = False


def _prime_factors(n: int) -> list[int]:
    if n < 2:
        return []
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


# Months with special significance in Islamic tradition
SIGNIFICANT_MONTHS = {
    1: {"name": "Muharram", "significance": "Sacred month, month of Hijra"},
    3: {"name": "Rabi al-Awwal", "significance": "Birth month of the Prophet ﷺ"},
    7: {"name": "Rajab", "significance": "Sacred month, month of Isra and Mi'raj"},
    9: {"name": "Ramadan", "significance": "Month of fasting, revelation of Quran"},
    12: {"name": "Dhul Hijjah", "significance": "Sacred month, month of Hajj"},
}

# Spiritual classification for each Hijri month
SPIRITUAL_MONTHS = {
    1: "sacred",       # Muharram — one of four sacred months
    2: "ordinary",     # Safar
    3: "prophetic",    # Rabi al-Awwal — birth of the Prophet ﷺ
    4: "ordinary",     # Rabi al-Thani
    5: "ordinary",     # Jumada al-Ula
    6: "ordinary",     # Jumada al-Thani
    7: "sacred",       # Rajab — sacred month, Isra and Mi'raj
    8: "preparatory",  # Sha'ban — preparation for Ramadan
    9: "devotional",   # Ramadan — fasting, Quran revelation
    10: "festive",     # Shawwal — Eid al-Fitr, six fasts of Shawwal
    11: "sacred",      # Dhul Qa'dah — sacred month
    12: "sacred",      # Dhul Hijjah — sacred month, Hajj, Eid al-Adha
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    if not _HAS_HIJRI:
        return SystemResult(
            id="hijri_calendar_encoding", name="Hijri Calendar Encoding",
            certainty="NEEDS_INPUT", data={"error": "hijri-converter not installed"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q4_TIMING"
        )

    try:
        h = Gregorian(profile.dob.year, profile.dob.month, profile.dob.day).to_hijri()
        h_year, h_month, h_day = h.year, h.month, h.day
    except (OverflowError, ValueError):
        # Dates outside hijri-converter range — use tabular algorithm
        from modules.hijri import _gregorian_to_jdn, _jdn_to_hijri
        jdn = _gregorian_to_jdn(profile.dob.year, profile.dob.month, profile.dob.day)
        h_year, h_month, h_day = _jdn_to_hijri(jdn)

    # Year analysis
    year_digits = [int(d) for d in str(h_year)]
    year_digit_sum = sum(year_digits)
    year_digit_root = reduce_number(year_digit_sum, keep_masters=())
    year_primes = _prime_factors(h_year)

    # Month analysis
    month_significance = SIGNIFICANT_MONTHS.get(h_month)
    is_sacred_month = h_month in {1, 7, 11, 12}  # Four sacred months
    is_ramadan = h_month == 9
    is_hajj_season = h_month == 12
    spiritual_month = SPIRITUAL_MONTHS.get(h_month, "ordinary")

    # Day analysis
    day_digit_root = reduce_number(h_day, keep_masters=())

    # Combined date sum
    combined_sum = h_year + h_month + h_day
    combined_root = reduce_number(combined_sum, keep_masters=())

    # Full date digit sum (all digits of YYYYMMDD)
    full_digits = [int(d) for d in f"{h_year}{h_month:02d}{h_day:02d}"]
    full_digit_sum = sum(full_digits)
    full_digit_root = reduce_number(full_digit_sum, keep_masters=())

    return SystemResult(
        id="hijri_calendar_encoding",
        name="Hijri Calendar Encoding (ترميز التقويم الهجري)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "hijri_year": h_year,
            "hijri_month": h_month,
            "hijri_day": h_day,
            "year_digits": year_digits,
            "year_digit_sum": year_digit_sum,
            "year_digit_root": year_digit_root,
            "year_prime_factors": year_primes,
            "is_sacred_month": is_sacred_month,
            "is_ramadan": is_ramadan,
            "is_hajj_season": is_hajj_season,
            "spiritual_month": spiritual_month,
            "month_significance": month_significance,
            "day_digit_root": day_digit_root,
            "combined_sum": combined_sum,
            "combined_root": combined_root,
            "full_digit_sum": full_digit_sum,
            "full_digit_root": full_digit_root,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Tabular Islamic Calendar (arithmetic conversion)", "Sacred months: Muharram, Rajab, Dhul Qa'dah, Dhul Hijjah"],
        question="Q4_TIMING"
    )
