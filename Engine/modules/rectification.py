"""Rectification — Birth Time Sensitivity Diagnostic

Tests birth time sensitivity across a ±30 minute window to identify
which chart angles change when time shifts. Produces a confidence
report on the currently recorded birth time.

COMPUTED_STRICT when birth_time_local + timezone + location are present
and pyswisseph is available. NEEDS_INPUT otherwise.

This is diagnostic infrastructure — excluded from convergence (set()
in CONVERGENCE_FIELDS).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Time offsets in minutes from base time
VARIANTS = {
    "minus_30": -30,
    "minus_15": -15,
    "plus_15": 15,
    "plus_30": 30,
}

# Known timezone offsets (mirrors natal_chart.py)
TZ_OFFSETS = {
    "Asia/Riyadh": 3,
    "Asia/Dubai": 4,
    "Asia/Kuwait": 3,
    "Asia/Amman": 2,
    "Africa/Cairo": 2,
    "Asia/Beirut": 2,
    "Asia/Damascus": 2,
    "Asia/Baghdad": 3,
    "Europe/Istanbul": 3,
    "Europe/London": 0,
    "America/New_York": -5,
    "UTC": 0,
}

# Known locations (mirrors natal_chart.py)
LOCATIONS = {
    "Cairo, Egypt": (26.2361, 50.0393),
    "Riyadh, Saudi Arabia": (24.7136, 46.6753),
    "Jeddah, Saudi Arabia": (21.5433, 39.1728),
    "Amman, Jordan": (31.9454, 35.9284),
    "Cairo, Egypt": (30.0444, 31.2357),
    "Dubai, UAE": (25.2048, 55.2708),
    "Kuwait City, Kuwait": (29.3759, 47.9774),
    "Beirut, Lebanon": (33.8938, 35.5018),
    "Damascus, Syria": (33.5138, 36.2765),
    "Baghdad, Iraq": (33.3152, 44.3661),
    "Istanbul, Turkey": (41.0082, 28.9784),
    "London, UK": (51.5074, -0.1278),
    "New York, USA": (40.7128, -74.0060),
}


def _parse_location(location: str):
    """Return (lat, lon) for a known location string."""
    coords = LOCATIONS.get(location)
    if coords:
        return coords
    try:
        from sirr_core.natal_chart import geocode
        geo = geocode(location)
        if geo:
            return geo.lat, geo.lng
    except Exception:
        pass
    return None


def _compute_chart_point(jd_ut, lat, lon):
    """Compute ascendant, MC, Moon sign, Sun house for a given JD."""
    import swisseph as swe
    swe.set_ephe_path(None)

    # Ascendant + MC via Whole Sign houses
    cusps, asmc = swe.houses(jd_ut, lat, lon, b'W')
    asc_lon = asmc[0]
    mc_lon = asmc[1]

    asc_sign_idx = int(asc_lon // 30) % 12
    mc_sign_idx = int(mc_lon // 30) % 12

    # Moon position
    moon_result = swe.calc_ut(jd_ut, 1)  # swe.MOON = 1
    moon_lon = moon_result[0][0]
    moon_sign_idx = int(moon_lon // 30) % 12

    # Sun position → house (whole sign: house 1 = ascendant sign)
    sun_result = swe.calc_ut(jd_ut, 0)  # swe.SUN = 0
    sun_lon = sun_result[0][0]
    sun_sign_idx = int(sun_lon // 30) % 12
    sun_house = ((sun_sign_idx - asc_sign_idx) % 12) + 1

    return {
        "ascendant_sign": SIGNS[asc_sign_idx],
        "ascendant_degree": round(asc_lon, 1),
        "mc_sign": SIGNS[mc_sign_idx],
        "mc_degree": round(mc_lon, 1),
        "moon_sign": SIGNS[moon_sign_idx],
        "sun_house": sun_house,
    }


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    if not profile.birth_time_local or not profile.timezone or not profile.location:
        return SystemResult(
            id="rectification",
            name="Rectification (Birth Time Sensitivity)",
            certainty="NEEDS_INPUT",
            data={"error": "Requires birth_time_local, timezone, and location"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
        )

    coords = _parse_location(profile.location)
    if coords is None:
        return SystemResult(
            id="rectification",
            name="Rectification (Birth Time Sensitivity)",
            certainty="NEEDS_INPUT",
            data={"error": f"Unknown location: {profile.location}"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
        )

    lat, lon = coords
    tz_offset = TZ_OFFSETS.get(profile.timezone)
    if tz_offset is None:
        try:
            from sirr_core.natal_chart import geocode
            geo = geocode(profile.location)
            if geo:
                tz_offset = geo.utc_offset
        except Exception:
            pass
    if tz_offset is None:
        return SystemResult(
            id="rectification",
            name="Rectification (Birth Time Sensitivity)",
            certainty="NEEDS_INPUT",
            data={"error": f"Unknown timezone: {profile.timezone}"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
        )

    import swisseph as swe
    swe.set_ephe_path(None)

    # Parse base time
    h, m = map(int, profile.birth_time_local.split(":"))
    base_minutes = h * 60 + m

    # Compute JD for each time variant
    def _jd_for_minutes(total_min):
        hh = total_min // 60
        mm = total_min % 60
        ut = (hh + mm / 60.0) - tz_offset
        return swe.julday(profile.dob.year, profile.dob.month, profile.dob.day, ut)

    # Base chart
    base_jd = _jd_for_minutes(base_minutes)
    base = _compute_chart_point(base_jd, lat, lon)

    # Variants
    variants = {}
    for label, offset in VARIANTS.items():
        v_jd = _jd_for_minutes(base_minutes + offset)
        variants[label] = _compute_chart_point(v_jd, lat, lon)

    # Stability analysis
    all_asc_signs = {base["ascendant_sign"]}
    all_mc_signs = {base["mc_sign"]}
    all_moon_signs = {base["moon_sign"]}
    inner_asc_signs = {base["ascendant_sign"]}
    inner_mc_signs = {base["mc_sign"]}

    for label, v in variants.items():
        all_asc_signs.add(v["ascendant_sign"])
        all_mc_signs.add(v["mc_sign"])
        all_moon_signs.add(v["moon_sign"])
        if label in ("minus_15", "plus_15"):
            inner_asc_signs.add(v["ascendant_sign"])
            inner_mc_signs.add(v["mc_sign"])

    asc_stable = len(all_asc_signs) == 1
    mc_stable = len(all_mc_signs) == 1
    moon_stable = len(all_moon_signs) == 1

    # Time sensitivity
    if len(inner_asc_signs) > 1:
        sensitivity = "HIGH"
    elif len(all_asc_signs) > 1:
        sensitivity = "MEDIUM"
    else:
        sensitivity = "LOW"

    base_time = profile.birth_time_local

    # Confidence note
    if sensitivity == "LOW":
        conf_note = (
            f"Birth time {base_time} yields {base['ascendant_sign']} Ascendant. "
            f"This sign is stable across a ±30 minute window, giving HIGH "
            f"confidence in time-dependent outputs."
        )
    elif sensitivity == "MEDIUM":
        conf_note = (
            f"Birth time {base_time} yields {base['ascendant_sign']} Ascendant. "
            f"This sign is stable within ±15 minutes but shifts at ±30, giving MEDIUM "
            f"confidence in time-dependent outputs."
        )
    else:
        conf_note = (
            f"Birth time {base_time} yields {base['ascendant_sign']} Ascendant. "
            f"This sign is fragile — it changes within ±15 minutes, giving LOW "
            f"confidence in time-dependent outputs."
        )

    interpretation = conf_note

    data = {
        "base_time": base_time,
        "base_ascendant_sign": base["ascendant_sign"],
        "base_ascendant_degree": base["ascendant_degree"],
        "base_mc_sign": base["mc_sign"],
        "base_mc_degree": base["mc_degree"],
        "base_moon_sign": base["moon_sign"],
        "base_sun_house": base["sun_house"],
        "ascendant_sign_stable": asc_stable,
        "mc_sign_stable": mc_stable,
        "moon_sign_stable": moon_stable,
        "time_sensitivity": sensitivity,
        "variants": variants,
        "confidence_note": conf_note,
    }

    return SystemResult(
        id="rectification",
        name="Rectification (Birth Time Sensitivity)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interpretation,
        constants_version=constants["version"],
        references=["pyswisseph Swiss Ephemeris", "Placidus/Whole Sign house system"],
    )
