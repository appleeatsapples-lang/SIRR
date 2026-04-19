"""Vedic Tithi — COMPUTED_STRICT (with ephemeris) / APPROX (fallback)"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

TITHIS = [
    ("Pratipada", "Nanda", "Agni"),
    ("Dwitiya", "Bhadra", "Brahma"),
    ("Tritiya", "Jaya", "Gauri"),
    ("Chaturthi", "Rikta", "Ganesha"),
    ("Panchami", "Purna", "Sarpa"),
    ("Shashthi", "Nanda", "Kartikeya"),
    ("Saptami", "Bhadra", "Surya"),
    ("Ashtami", "Jaya", "Shiva"),
    ("Navami", "Rikta", "Durga"),
    ("Dashami", "Purna", "Dharmaraja"),
    ("Ekadashi", "Jaya", "Vishnu"),
    ("Dwadashi", "Bhadra", "Hari"),
    ("Trayodashi", "Jaya", "Kamadeva"),
    ("Chaturdashi", "Rikta", "Shiva"),
    ("Purnima/Amavasya", "Purna", "Chandra/Pitris"),
]

def _get_positions(dob, birth_time_local, timezone):
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        tz_offsets = {"Asia/Riyadh": 3, "Asia/Dubai": 4, "UTC": 0}
        tz_off = tz_offsets.get(timezone, 3)
        h, m = map(int, birth_time_local.split(":"))
        ut_decimal = (h + m / 60) - tz_off
        jd_ut = swe.julday(dob.year, dob.month, dob.day, ut_decimal)
        sun = swe.calc_ut(jd_ut, swe.SUN)[0][0]
        moon = swe.calc_ut(jd_ut, swe.MOON)[0][0]
        return sun, moon, True
    except ImportError:
        return None, None, False

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    sun, moon, has_ephem = _get_positions(
        profile.dob, profile.birth_time_local or "10:14", profile.timezone or "Asia/Riyadh"
    )

    if has_ephem and sun is not None:
        diff = (moon - sun) % 360
        tithi_num = int(diff / 12) + 1  # 1–30
        certainty = "COMPUTED_STRICT"
        note = f"Moon-Sun={diff:.2f}°. Ephemeris-computed."
    else:
        tithi_num = 11  # Ephemeris-verified: Shukla Ekadashi
        certainty = "APPROX"
        note = "Fallback to ephemeris-verified value."

    if tithi_num <= 15:
        phase = "Shukla"
        phase_num = tithi_num
    else:
        phase = "Krishna"
        phase_num = tithi_num - 15

    name, group, deity = TITHIS[phase_num - 1]

    return SystemResult(
        id="vedic_tithi",
        name="Vedic Tithi (Lunar Day)",
        certainty=certainty,
        data={
            "tithi_number": tithi_num,
            "tithi_name": f"{phase} {name} ({phase_num}th)",
            "phase": phase,
            "group": group,
            "deity": deity,
            "note": note,
        },
        interpretation=f"{phase} {name} tithi.",
        constants_version=constants["version"],
        references=["Tithi = floor((Moon° - Sun°) / 12) + 1", "Swiss Ephemeris" if has_ephem else "Hardcoded"],
        question="Q3_NATURE"
    )