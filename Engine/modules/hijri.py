"""Hijri Calendar — COMPUTED_STRICT
Gregorian to Islamic Hijri date conversion.
Uses hijri_converter library (Umm al-Qura calendar) with tabular fallback.
"""
from __future__ import annotations
import math
from sirr_core.types import InputProfile, SystemResult

try:
    from hijri_converter import Gregorian as HijriGregorian
    _HAS_HIJRI_LIB = True
except ImportError:
    _HAS_HIJRI_LIB = False

HIJRI_MONTHS = {
    1: ("Muharram", "محرّم"), 2: ("Safar", "صفر"),
    3: ("Rabi al-Awwal", "ربيع الأول"), 4: ("Rabi al-Thani", "ربيع الثاني"),
    5: ("Jumada al-Ula", "جمادى الأولى"), 6: ("Jumada al-Thani", "جمادى الثانية"),
    7: ("Rajab", "رجب"), 8: ("Sha'ban", "شعبان"),
    9: ("Ramadan", "رمضان"), 10: ("Shawwal", "شوال"),
    11: ("Dhu al-Qi'dah", "ذو القعدة"), 12: ("Dhu al-Hijjah", "ذو الحجة"),
}

WEEKDAY_AR = {
    0: ("Monday", "الاثنين"), 1: ("Tuesday", "الثلاثاء"),
    2: ("Wednesday", "الأربعاء"), 3: ("Thursday", "الخميس"),
    4: ("Friday", "الجمعة"), 5: ("Saturday", "السبت"),
    6: ("Sunday", "الأحد"),
}


def _gregorian_to_jdn(y, m, d):
    """Convert Gregorian date to Julian Day Number."""
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def _jdn_to_hijri(jdn):
    """Convert JDN to Hijri date (Tabular Islamic Calendar, civil/Thursday epoch)."""
    # Epoch: July 16, 622 CE (Julian) = JDN 1948439.5, using 1948440
    l = jdn - 1948440 + 10632
    n = (l - 1) // 10631
    l = l - 10631 * n + 354
    j = (((10985 - l) // 5316)) * ((50 * l) // 17719) + ((l // 5670)) * ((43 * l) // 15238)
    l = l - (((30 - j) // 15)) * ((17719 * j) // 50) - (((j // 16)) * ((15238 * j) // 43)) + 29
    m = (24 * l) // 709
    d = l - (709 * m) // 24
    y = 30 * n + j - 30
    return y, m, d


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    dob = profile.dob
    today = profile.today

    _use_tabular = not _HAS_HIJRI_LIB
    if _HAS_HIJRI_LIB:
        try:
            hijri_birth = HijriGregorian(dob.year, dob.month, dob.day).to_hijri()
            h_year, h_month, h_day = hijri_birth.year, hijri_birth.month, hijri_birth.day
            hijri_today = HijriGregorian(today.year, today.month, today.day).to_hijri()
            t_year, t_month, t_day = hijri_today.year, hijri_today.month, hijri_today.day
            source_note = "Umm al-Qura calendar via hijri-converter library."
        except (OverflowError, ValueError):
            _use_tabular = True
    if _use_tabular:
        jdn = _gregorian_to_jdn(dob.year, dob.month, dob.day)
        h_year, h_month, h_day = _jdn_to_hijri(jdn)
        jdn_today = _gregorian_to_jdn(today.year, today.month, today.day)
        t_year, t_month, t_day = _jdn_to_hijri(jdn_today)
        source_note = "Tabular Islamic Calendar (arithmetic). May differ ±1 day from observed calendar."

    month_en, month_ar = HIJRI_MONTHS.get(h_month, ("Unknown", "غير معروف"))
    t_month_en, t_month_ar = HIJRI_MONTHS.get(t_month, ("Unknown", "غير معروف"))

    # Hijri age
    hijri_age = t_year - h_year
    if (t_month, t_day) < (h_month, h_day):
        hijri_age -= 1

    return SystemResult(
        id="hijri",
        name="Hijri Calendar (التقويم الهجري)",
        certainty="COMPUTED_STRICT",
        data={
            "birth_hijri": f"{h_day} {month_en} {h_year} AH",
            "birth_hijri_ar": f"{h_day} {month_ar} {h_year} هـ",
            "birth_year": h_year,
            "birth_month": h_month,
            "birth_month_name": month_en,
            "birth_day": h_day,
            "today_hijri": f"{t_day} {t_month_en} {t_year} AH",
            "hijri_age": hijri_age,
            "born_in_ramadan": h_month == 9,
            "born_in_dhul_hijjah": h_month == 12,
            "note": source_note
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Tabular Islamic Calendar algorithm. Civil/Thursday epoch variant."],
        question="Q4_TIMING"
    )
