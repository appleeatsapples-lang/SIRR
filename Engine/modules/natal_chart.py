"""Natal Chart — Planetary Positions (Tropical Zodiac)
Computes Sun through Pluto + North Node positions using Swiss Ephemeris.
Requires birth_time_local, timezone, and location in the profile.

COMPUTED_STRICT when birth time is present, NEEDS_INPUT when missing.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Known locations → (lat, lon)
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

# Known timezone offsets (hours from UTC)
TZ_OFFSETS = {
    "Asia/Riyadh": 3,
    "Asia/Dubai": 4,
    "Asia/Kuwait": 3,
    "Asia/Amman": 2,    # Standard; +3 in summer
    "Africa/Cairo": 2,
    "Asia/Beirut": 2,
    "Asia/Damascus": 2,
    "Asia/Baghdad": 3,
    "Europe/Istanbul": 3,
    "Europe/London": 0,
    "America/New_York": -5,
    "UTC": 0,
}

PLANETS = [
    ("Sun", 0),       # swe.SUN
    ("Moon", 1),       # swe.MOON
    ("Mercury", 2),    # swe.MERCURY
    ("Venus", 3),      # swe.VENUS
    ("Mars", 4),       # swe.MARS
    ("Jupiter", 5),    # swe.JUPITER
    ("Saturn", 6),     # swe.SATURN
    ("Uranus", 7),     # swe.URANUS
    ("Neptune", 8),    # swe.NEPTUNE
    ("Pluto", 9),      # swe.PLUTO
    ("North Node", 11), # swe.MEAN_NODE (True Node = 11 in some builds)
]


def _parse_location(location: str):
    """Return (lat, lon, tz_offset) for a known location string.
    
    First tries the legacy LOCATIONS dict (exact match).
    Falls back to sirr_core.natal_chart geocoder (120+ cities, fuzzy city-name matching).
    Returns (lat, lon, tz_offset) tuple or None.
    """
    # Legacy exact match
    coords = LOCATIONS.get(location)
    if coords:
        return coords[0], coords[1], None  # caller must look up tz separately

    # Try full geocoder
    try:
        from sirr_core.natal_chart import geocode
        geo = geocode(location)
        if geo:
            return geo.lat, geo.lng, geo.utc_offset
    except Exception:
        pass
    return None


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    if not profile.birth_time_local or not profile.timezone or not profile.location:
        return SystemResult(
            id="natal_chart",
            name="Natal Chart (Tropical)",
            certainty="NEEDS_INPUT",
            data={"error": "Requires birth_time_local, timezone, and location"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    coords = _parse_location(profile.location)
    if coords is None:
        return SystemResult(
            id="natal_chart",
            name="Natal Chart (Tropical)",
            certainty="NEEDS_INPUT",
            data={"error": f"Unknown location: {profile.location}"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    lat, lon, geo_tz_offset = coords

    tz_offset = TZ_OFFSETS.get(profile.timezone)
    if tz_offset is None:
        # Fall back to geocoder's tz offset (already returned when city matched)
        tz_offset = geo_tz_offset
    if tz_offset is None:
        return SystemResult(
            id="natal_chart",
            name="Natal Chart (Tropical)",
            certainty="NEEDS_INPUT",
            data={"error": f"Unknown timezone: {profile.timezone}"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    import swisseph as swe
    swe.set_ephe_path(None)

    h, m = map(int, profile.birth_time_local.split(":"))
    ut = (h + m / 60.0) - tz_offset
    jd_ut = swe.julday(profile.dob.year, profile.dob.month, profile.dob.day, ut)

    # Compute planetary positions
    planets = {}
    planet_longitudes = {}
    for name, pid in PLANETS:
        # swe.MEAN_NODE id is 10 in pyswisseph
        actual_id = pid if pid != 11 else 10
        result = swe.calc_ut(jd_ut, actual_id)
        longitude = result[0][0]
        sign_idx = int(longitude // 30) % 12
        deg_in_sign = longitude % 30
        degree = int(deg_in_sign)
        minute = int((deg_in_sign - degree) * 60)

        planets[name] = {
            "longitude": round(longitude, 4),
            "sign": SIGNS[sign_idx],
            "degree": degree,
            "minute": minute,
            "formatted": f"{degree}\u00b0{minute:02d}' {SIGNS[sign_idx]}",
        }
        planet_longitudes[name] = round(longitude, 4)

    # Compute Ascendant and MC via house calculation
    cusps, asmc = swe.houses(jd_ut, lat, lon, b'W')
    asc_lon = asmc[0]
    mc_lon = asmc[1]
    asc_sign_idx = int(asc_lon // 30) % 12
    mc_sign_idx = int(mc_lon // 30) % 12

    asc_deg = int(asc_lon % 30)
    asc_min = int((asc_lon % 30 - asc_deg) * 60)
    mc_deg = int(mc_lon % 30)
    mc_min = int((mc_lon % 30 - mc_deg) * 60)

    data = {
        "planets": planets,
        "ascendant": {
            "longitude": round(asc_lon, 4),
            "sign": SIGNS[asc_sign_idx],
            "degree": asc_deg,
            "minute": asc_min,
            "formatted": f"{asc_deg}\u00b0{asc_min:02d}' {SIGNS[asc_sign_idx]}",
        },
        "midheaven": {
            "longitude": round(mc_lon, 4),
            "sign": SIGNS[mc_sign_idx],
            "degree": mc_deg,
            "minute": mc_min,
            "formatted": f"{mc_deg}\u00b0{mc_min:02d}' {SIGNS[mc_sign_idx]}",
        },
        "julian_day": round(jd_ut, 6),
        "coordinates": {"lat": lat, "lon": lon},
        "sun_sign": planets["Sun"]["sign"],
        "moon_sign": planets["Moon"]["sign"],
        "rising_sign": SIGNS[asc_sign_idx],
    }

    return SystemResult(
        id="natal_chart",
        name="Natal Chart (Tropical)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Swiss Ephemeris (Moshier)",
            "Tropical zodiac (Fagan-Bradley ayanamsa not applied)",
        ],
        question="Q1_IDENTITY",
    )
