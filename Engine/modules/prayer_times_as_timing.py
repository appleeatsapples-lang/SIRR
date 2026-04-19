"""Prayer Times as Timing — COMPUTED_STRICT
Computes the 5 Islamic prayer times for the birth date and location
as a timing framework. Maps birth time to prayer period.
Uses simplified solar calculation (no external API).
"""
from __future__ import annotations
import math
from datetime import date
from sirr_core.types import InputProfile, SystemResult

DEFAULT_LAT = 26.2361  # Cairo
DEFAULT_LON = 50.0393
DEFAULT_UTC_OFFSET = 3.0  # AST


def _solar_declination(day_of_year: int) -> float:
    return 23.45 * math.sin(math.radians(360 / 365 * (day_of_year - 81)))


def _equation_of_time(day_of_year: int) -> float:
    b = math.radians(360 / 365 * (day_of_year - 81))
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def _hour_angle(lat: float, decl: float, angle: float) -> float:
    """Hour angle for sun at given altitude angle."""
    lat_r = math.radians(lat)
    decl_r = math.radians(decl)
    cos_ha = (math.sin(math.radians(angle)) - math.sin(lat_r) * math.sin(decl_r)) / \
             (math.cos(lat_r) * math.cos(decl_r))
    cos_ha = max(-1, min(1, cos_ha))
    return math.degrees(math.acos(cos_ha))


def _solar_noon(lon: float, utc_offset: float, eot: float) -> float:
    """Solar noon in hours (local time)."""
    return 12 - (lon - 15 * utc_offset) / 15 - eot / 60


def _format_time(hours: float) -> str:
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h:02d}:{m:02d}"


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    lat = profile.latitude or DEFAULT_LAT
    lon = profile.longitude or DEFAULT_LON
    utc_offset = profile.utc_offset or DEFAULT_UTC_OFFSET
    d = profile.dob

    doy = d.timetuple().tm_yday
    decl = _solar_declination(doy)
    eot = _equation_of_time(doy)
    noon = _solar_noon(lon, utc_offset, eot)

    # Fajr: sun at -18° (standard)
    ha_fajr = _hour_angle(lat, decl, -18)
    fajr = noon - ha_fajr / 15

    # Sunrise: sun at -0.833° (atmospheric refraction)
    ha_sunrise = _hour_angle(lat, decl, -0.833)
    sunrise = noon - ha_sunrise / 15

    # Dhuhr: solar noon + 1 min (after zenith)
    dhuhr = noon + 1 / 60

    # Asr: shadow = object + shadow at noon (Shafi'i: factor=1)
    shadow_factor = 1  # Shafi'i
    asr_angle = math.degrees(math.atan(1 / (shadow_factor + math.tan(math.radians(abs(lat - decl))))))
    ha_asr = _hour_angle(lat, decl, asr_angle)
    asr = noon + ha_asr / 15

    # Maghrib: sun at -0.833°
    maghrib = noon + ha_sunrise / 15

    # Isha: sun at -17°
    ha_isha = _hour_angle(lat, decl, -17)
    isha = noon + ha_isha / 15

    # Sunset
    sunset = maghrib

    times = {
        "fajr": round(fajr, 2),
        "sunrise": round(sunrise, 2),
        "dhuhr": round(dhuhr, 2),
        "asr": round(asr, 2),
        "maghrib": round(maghrib, 2),
        "isha": round(isha, 2),
    }

    times_formatted = {k: _format_time(v) for k, v in times.items()}

    # Map birth time to prayer period
    birth_period = "unknown"
    if profile.birth_time_local:
        parts = profile.birth_time_local.split(":")
        birth_hour = int(parts[0]) + int(parts[1]) / 60
        if birth_hour < fajr:
            birth_period = "pre_fajr"
        elif birth_hour < sunrise:
            birth_period = "fajr"
        elif birth_hour < dhuhr:
            birth_period = "duha"
        elif birth_hour < asr:
            birth_period = "dhuhr"
        elif birth_hour < maghrib:
            birth_period = "asr"
        elif birth_hour < isha:
            birth_period = "maghrib"
        else:
            birth_period = "isha"

    # Day length
    day_length = round(sunset - sunrise, 2)
    night_length = round(24 - day_length, 2)

    return SystemResult(
        id="prayer_times_as_timing",
        name="Prayer Times as Timing (أوقات الصلاة كتوقيت)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "birth_date": d.isoformat(),
            "latitude": lat,
            "longitude": lon,
            "prayer_times": times_formatted,
            "prayer_times_decimal": times,
            "birth_period": birth_period,
            "day_length_hours": day_length,
            "night_length_hours": night_length,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Islamic prayer time calculation — simplified solar algorithm",
            "Fajr angle: -18°, Isha angle: -17° (standard)",
            "Shafi'i Asr method (shadow = 1× object length)",
        ],
        question="Q4_TIMING"
    )
