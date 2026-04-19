"""Manazil al-Qamar — COMPUTED_STRICT (Moon longitude via ephemeris)
Computes the Arabic Lunar Mansion (منزل القمر) from Moon position.
28 mansions, each spanning 12°51'26" (≈12.857°).
Traditional Islamic astronomical system from Al-Buni / Ibn Arabi.
"""
from __future__ import annotations
from datetime import date
from sirr_core.types import InputProfile, SystemResult


def _get_moon(dob, birth_time_local, timezone):
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        tz_offsets = {"Asia/Riyadh": 3, "Asia/Dubai": 4, "UTC": 0}
        tz_off = tz_offsets.get(timezone, 3)
        h, m = map(int, birth_time_local.split(":"))
        ut = (h + m / 60) - tz_off
        jd_ut = swe.julday(dob.year, dob.month, dob.day, ut)
        moon = swe.calc_ut(jd_ut, swe.MOON)[0][0]
        return moon, True
    except ImportError:
        return None, False


def _approx_solar_degree(month: int, day: int) -> float:
    """Fallback: solar longitude approximation."""
    doy = date(2000, month, day).timetuple().tm_yday
    degree = ((doy - 80) % 365) * (360.0 / 365.25)
    if degree < 0:
        degree += 360
    return degree


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    cfg = constants["manazil"]
    entries = cfg["entries"]

    moon_deg, has_ephem = _get_moon(
        profile.dob, profile.birth_time_local or "10:14", profile.timezone or "Asia/Riyadh"
    )

    if has_ephem and moon_deg is not None:
        degree = moon_deg
        certainty = "COMPUTED_STRICT"
        note = f"Moon={moon_deg:.4f}°. Ephemeris-computed."
    else:
        degree = _approx_solar_degree(profile.dob.month, profile.dob.day)
        certainty = "APPROX"
        note = "Fallback: solar longitude approximation."

    manzil_index = int(degree / (360.0 / 28))  # 0-27
    manzil_num = manzil_index + 1  # 1-28
    entry = entries[str(manzil_num)]

    degree_in_manzil = degree - (manzil_index * (360.0 / 28))
    position_fraction = round(degree_in_manzil / (360.0 / 28), 2)

    return SystemResult(
        id="manazil",
        name="Manazil al-Qamar (منازل القمر)",
        certainty=certainty,
        data={
            "moon_longitude": round(degree, 4) if has_ephem else None,
            "solar_degree_fallback": round(degree, 2) if not has_ephem else None,
            "manzil_number": manzil_num,
            "name_arabic": entry["name_arabic"],
            "name_transliterated": entry["name_transliterated"],
            "name_english": entry["name_english"],
            "element": entry["element"],
            "nature": entry["nature"],
            "letter": entry["letter"],
            "meaning": entry["meaning"],
            "degrees": entry["degrees"],
            "position_in_manzil": position_fraction,
            "note": note,
        },
        interpretation=f"Manzil {manzil_num}: {entry['name_transliterated']} ({entry['name_arabic']}) — {entry['name_english']}. {entry['nature']}. Letter: {entry['letter']}. {entry['meaning']}.",
        constants_version=constants["version"],
        references=["Al-Buni, Shams al-Ma'arif", "28 Manazil al-Qamar tradition", "Swiss Ephemeris" if has_ephem else "Solar approximation"],
        question="Q1_IDENTITY"
    )