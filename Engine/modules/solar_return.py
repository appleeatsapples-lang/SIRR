"""Solar Return — Annual Chart — COMPUTED_STRICT
Computes the chart for the exact moment the transiting Sun returns to its
natal ecliptic longitude each year. This "birthday chart" describes the
themes of the coming year.

Uses Newton-Raphson iteration on pyswisseph to find the precise Julian Day
of the Sun's return, then computes a full chart for that moment.

Sources: Abu Ma'shar (On Solar Revolutions), Morin de Villefranche
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Planets to compute in the return chart
PLANET_IDS = [
    ("Sun", 0), ("Moon", 1), ("Mercury", 2), ("Venus", 3),
    ("Mars", 4), ("Jupiter", 5), ("Saturn", 6),
]


def _sign_data(longitude: float) -> dict:
    sign_idx = int(longitude // 30) % 12
    deg_in_sign = longitude % 30
    degree = int(deg_in_sign)
    minute = int((deg_in_sign - degree) * 60)
    return {
        "longitude": round(longitude, 4),
        "sign": SIGNS[sign_idx],
        "degree": degree,
        "minute": minute,
        "formatted": f"{degree}\u00b0{minute:02d}' {SIGNS[sign_idx]}",
    }


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="solar_return",
            name="Solar Return",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    import swisseph as swe
    swe.set_ephe_path(None)

    natal_sun_lon = natal_chart_data["planets"]["Sun"]["longitude"]

    # Prefer profile coordinates (from geocoder) over internal lookup
    if getattr(profile, 'latitude', None) is not None and getattr(profile, 'longitude', None) is not None:
        lat, lon = profile.latitude, profile.longitude
        tz_offset = getattr(profile, 'utc_offset', None)
        if tz_offset is None:
            from modules.natal_chart import TZ_OFFSETS
            tz_offset = TZ_OFFSETS.get(profile.timezone, 3)
    else:
        from modules.natal_chart import LOCATIONS, TZ_OFFSETS
        coords = LOCATIONS.get(profile.location)
        tz_offset = TZ_OFFSETS.get(profile.timezone, 3)
        if coords is None:
            # Fall back to sirr_core geocoder
            try:
                from sirr_core.natal_chart import geocode
                geo = geocode(profile.location)
                if geo:
                    lat, lon = geo.lat, geo.lng
                    if tz_offset is None:
                        tz_offset = geo.utc_offset
                else:
                    return SystemResult(
                        id="solar_return",
                        name="Solar Return",
                        certainty="NEEDS_INPUT",
                        data={"error": f"Unknown location: {profile.location}"},
                        interpretation=None,
                        constants_version=constants["version"],
                        references=[],
                        question="Q4_TIMING",
                    )
            except Exception:
                return SystemResult(
                    id="solar_return",
                    name="Solar Return",
                    certainty="NEEDS_INPUT",
                    data={"error": f"Unknown location: {profile.location}"},
                    interpretation=None,
                    constants_version=constants["version"],
                    references=[],
                    question="Q4_TIMING",
                )
        else:
            lat, lon = coords

    # Find solar return for the current year (profile.today)
    target_year = profile.today.year
    # Start searching near the birthday in target year
    jd_search = swe.julday(target_year, profile.dob.month, profile.dob.day, 12.0)

    # Newton-Raphson: converge on exact Sun return
    for _ in range(20):
        result = swe.calc_ut(jd_search, swe.SUN)
        sun_lon = result[0][0]
        speed = result[0][3]  # degrees per day
        diff = (natal_sun_lon - sun_lon + 180) % 360 - 180  # signed
        if abs(diff) < 1e-8:
            break
        jd_search += diff / speed

    jd_return = jd_search

    # Compute return chart planets
    return_planets = {}
    for name, pid in PLANET_IDS:
        r = swe.calc_ut(jd_return, pid)
        return_planets[name] = _sign_data(r[0][0])

    # Compute return ASC and MC
    cusps, asmc = swe.houses(jd_return, lat, lon, b'W')
    return_asc = _sign_data(asmc[0])
    return_mc = _sign_data(asmc[1])

    # Convert JD to date/time
    y, mo, d, h = swe.revjul(jd_return)
    local_h = h + tz_offset
    local_day_offset = 0
    if local_h >= 24:
        local_h -= 24
        local_day_offset = 1
    elif local_h < 0:
        local_h += 24
        local_day_offset = -1
    hour = int(local_h)
    minute = int((local_h - hour) * 60)

    # Return ASC sign as the year's rising sign (key interpretive factor)
    return_rising = return_asc["sign"]

    # Which house does the return Sun fall in? (Whole Sign from return ASC)
    return_asc_sign_idx = SIGNS.index(return_asc["sign"])
    return_sun_sign_idx = SIGNS.index(return_planets["Sun"]["sign"])
    sun_house = (return_sun_sign_idx - return_asc_sign_idx) % 12 + 1

    # Moon sign in return chart (most variable factor year to year)
    return_moon_sign = return_planets["Moon"]["sign"]

    data = {
        "return_year": target_year,
        "return_date": f"{y}-{mo:02d}-{d:02d}",
        "return_time_local": f"{hour:02d}:{minute:02d}",
        "return_rising": return_rising,
        "return_moon_sign": return_moon_sign,
        "sun_house": sun_house,
        "planets": return_planets,
        "ascendant": return_asc,
        "midheaven": return_mc,
    }

    return SystemResult(
        id="solar_return",
        name="Solar Return",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Abu Ma'shar, On Solar Revolutions",
            "Swiss Ephemeris — Newton-Raphson Sun return",
        ],
        question="Q4_TIMING",
    )
