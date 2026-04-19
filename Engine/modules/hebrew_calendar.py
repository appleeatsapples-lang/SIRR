"""Hebrew Calendar — COMPUTED_STRICT
Converts Gregorian DOB to Hebrew date with month meaning and holiday detection.
Uses hdate library for reliable conversion.
"""
from __future__ import annotations
from datetime import date
from hdate import HebrewDate
from sirr_core.types import InputProfile, SystemResult


# Major holidays by month-day (Hebrew calendar)
HOLIDAYS = {
    ("תשרי", 1): "Rosh Hashanah (New Year)",
    ("תשרי", 2): "Rosh Hashanah (Day 2)",
    ("תשרי", 10): "Yom Kippur (Day of Atonement)",
    ("תשרי", 15): "Sukkot (Tabernacles)",
    ("ניסן", 15): "Pesach (Passover)",
    ("סיון", 6): "Shavuot (Pentecost)",
    ("כסלו", 25): "Hanukkah (Festival of Lights)",
    ("אדר", 14): "Purim",
    ("שבט", 15): "Tu BiShvat (New Year of Trees)",
    ("אב", 9): "Tisha B'Av (Mourning/Destruction)",
    ("אב", 15): "Tu B'Av (Festival of Love)",
}

# Month number to standard name mapping for constants lookup
MONTH_NUMBERS = {
    "תשרי": 7, "חשוון": 8, "כסלו": 9, "טבת": 10,
    "שבט": 11, "אדר": 12, "אדר א׳": 12, "אדר ב׳": 13,
    "ניסן": 1, "אייר": 2, "סיון": 3, "תמוז": 4,
    "אב": 5, "אלול": 6,
}


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    cfg = constants.get("hebrew_calendar", {})
    months_data = cfg.get("months", {})

    dob = profile.dob
    hd = HebrewDate.from_gdate(dob)

    month_str = str(hd.month)
    month_num = MONTH_NUMBERS.get(month_str, 0)
    month_info = months_data.get(str(month_num), {"name": month_str, "meaning": "Unknown"})

    # Holiday detection
    holiday = HOLIDAYS.get((month_str, hd.day))

    # Hebrew year meaning (gematria of year)
    year_in_cycle = (hd.year - 1) % 19 + 1
    is_leap = year_in_cycle in (3, 6, 8, 11, 14, 17, 19)

    # Also convert today
    today = profile.today
    hd_today = HebrewDate.from_gdate(today)
    hebrew_age = hd_today.year - hd.year

    return SystemResult(
        id="hebrew_calendar",
        name="Hebrew Calendar Date",
        certainty="COMPUTED_STRICT",
        data={
            "hebrew_day": hd.day,
            "hebrew_month": month_str,
            "hebrew_month_number": month_num,
            "hebrew_year": hd.year,
            "month_name_english": month_info.get("name", month_str),
            "month_meaning": month_info.get("meaning", ""),
            "holiday": holiday,
            "is_leap_year": is_leap,
            "year_in_metonic_cycle": year_in_cycle,
            "hebrew_age": hebrew_age,
            "today_hebrew": f"{hd_today.day} {hd_today.month} {hd_today.year}",
            "note": "Gregorian→Hebrew via hdate library. Holiday detection included."
        },
        interpretation=f"Born {hd.day} {month_str} {hd.year}" + (f" — {holiday}" if holiday else "") + f". Hebrew age: {hebrew_age}.",
        constants_version=constants["version"],
        references=["Hebrew calendar (Metonic cycle)", "hdate library"],
        question="Q4_TIMING"
    )
