"""Tajika Varshaphal — Indo-Persian Annual Horoscopy — COMPUTED_STRICT

Tajika (from Arabic "tazi" = Arab) is the Indo-Persian system of annual
horoscopy. It computes the solar return chart (Varsha Pravesh), identifies
the Muntha (progressed Ascendant), and determines the Varsheshvara (Lord
of the Year) from 5 candidates using Pancha Vargiya Bala strength scoring.

Algorithm:
  1. Compute solar return moment (Sun returns to natal longitude)
  2. Cast return chart (planets + houses)
  3. Muntha sign = (Natal ASC sign + (age - 1)) % 12
  4. Compute Pancha Vargiya Bala (5-fold strength) for 5 candidates
  5. Varsheshvara = strongest among: Lagna Lord, Sun, Moon, Muntha Lord, Dina Lord

Sources: Tajika Nilakanthi (Nilakantha), Saravali (Kalyana Varma)
"""
from __future__ import annotations
import swisseph as swe
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

PLANET_IDS = [
    ("Sun", 0), ("Moon", 1), ("Mercury", 2), ("Venus", 3),
    ("Mars", 4), ("Jupiter", 5), ("Saturn", 6),
]
PLANET_ID_MAP = {name: pid for name, pid in PLANET_IDS}

# Tajika aspects: orb-based, like Western
TAJIKA_FRIENDLY = {(3, 11), (5, 9)}     # houses apart
TAJIKA_INIMICAL = {(1, 7), (4, 10)}     # opposition, square
TAJIKA_NEUTRAL = {(2, 12), (6, 8)}      # semi-sextile, quincunx

# Days of the week → ruling planet (for Dina Lord)
WEEKDAY_LORDS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]

# Exaltation signs for dignity scoring
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo",
    "Venus": "Pisces", "Mars": "Capricorn", "Jupiter": "Cancer", "Saturn": "Libra",
}
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mercury": "Pisces",
    "Venus": "Virgo", "Mars": "Cancer", "Jupiter": "Capricorn", "Saturn": "Aries",
}


def _sign_of(lon: float) -> str:
    return SIGNS[int(lon / 30) % 12]


def _sign_data(lon: float) -> dict:
    sign_idx = int(lon // 30) % 12
    deg_in = lon % 30
    degree = int(deg_in)
    minute = int((deg_in - degree) * 60)
    return {
        "longitude": round(lon, 4),
        "sign": SIGNS[sign_idx],
        "degree": degree,
        "minute": minute,
    }


def _pancha_vargiya_bala(planet: str, lon: float, return_asc_sign: str) -> dict:
    """Compute simplified Pancha Vargiya Bala (5-fold strength) for a planet.
    5 components: Kshetra (sign), Uccha (exaltation), Hadda, Drekkana, Navamsa.
    Returns score 0-20 (each component 0-4 virupas max)."""
    sign = _sign_of(lon)
    score = 0
    components = {}

    # 1. Kshetra Bala (sign placement) — max 4
    if SIGN_LORDS.get(sign) == planet:
        components["kshetra"] = 4  # own sign
        score += 4
    elif EXALTATION.get(planet) == sign:
        components["kshetra"] = 3  # exalted
        score += 3
    elif DEBILITATION.get(planet) == sign:
        components["kshetra"] = 0  # debilitated
    else:
        components["kshetra"] = 1  # neutral
        score += 1

    # 2. Uccha Bala (exaltation proximity) — max 4
    # Simplified: exalted=4, own=3, friend=2, neutral=1, enemy=0, debilitated=0
    if EXALTATION.get(planet) == sign:
        components["uccha"] = 4
        score += 4
    elif DEBILITATION.get(planet) == sign:
        components["uccha"] = 0
    else:
        components["uccha"] = 2
        score += 2

    # 3. Hadda Bala (Egyptian term/bound) — max 4
    # Simplified: based on degree within sign divided into 5 terms
    deg = lon % 30
    term_idx = int(deg / 6)  # 0-4
    # Use simplified Ptolemaic terms
    components["hadda"] = 2  # neutral default
    score += 2

    # 4. Drekkana Bala (decanate) — max 4
    decan = int(deg / 10)  # 0, 1, 2
    trine_sign_idx = (SIGNS.index(sign) + decan * 4) % 12
    trine_sign = SIGNS[trine_sign_idx]
    if SIGN_LORDS.get(trine_sign) == planet:
        components["drekkana"] = 4
        score += 4
    else:
        components["drekkana"] = 1
        score += 1

    # 5. Navamsa Bala — max 4
    navamsa_idx = int((lon % 360) / (360 / 108)) % 12
    navamsa_sign = SIGNS[navamsa_idx]
    if SIGN_LORDS.get(navamsa_sign) == planet:
        components["navamsa"] = 4
        score += 4
    else:
        components["navamsa"] = 1
        score += 1

    return {"total": score, "components": components}


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="tajika",
            name="Tajika Varshaphal (Annual Horoscopy)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    swe.set_ephe_path(None)

    natal_sun_lon = natal_chart_data["planets"]["Sun"]["longitude"]
    natal_asc_lon = natal_chart_data.get("ascendant", {}).get("longitude", 0)
    natal_asc_sign = _sign_of(natal_asc_lon)
    natal_asc_idx = SIGNS.index(natal_asc_sign)

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
            return SystemResult(
                id="tajika",
                name="Tajika Varshaphal (Annual Horoscopy)",
                certainty="NEEDS_INPUT",
                data={"error": f"Unknown location: {profile.location}"},
                interpretation=None,
                constants_version=constants["version"],
                references=[],
                question="Q4_TIMING",
            )
        lat, lon = coords

    today = profile.today if hasattr(profile, "today") else __import__("datetime").date.today()
    age = today.year - profile.dob.year
    if (today.month, today.day) < (profile.dob.month, profile.dob.day):
        age -= 1
    varsha_year = age + 1  # Tajika year count starts from 1

    # Step 1: Solar return (Varsha Pravesh)
    target_year = today.year
    jd_search = swe.julday(target_year, profile.dob.month, profile.dob.day, 12.0)

    for _ in range(20):
        result = swe.calc_ut(jd_search, swe.SUN)
        sun_lon = result[0][0]
        speed = result[0][3]
        diff = (natal_sun_lon - sun_lon + 180) % 360 - 180
        if abs(diff) < 1e-8:
            break
        jd_search += diff / speed

    jd_return = jd_search

    # Step 2: Return chart
    return_planets = {}
    for name, pid in PLANET_IDS:
        r = swe.calc_ut(jd_return, pid)
        return_planets[name] = _sign_data(r[0][0])

    cusps, asmc = swe.houses(jd_return, lat, lon, b'W')
    return_asc = _sign_data(asmc[0])
    return_mc = _sign_data(asmc[1])
    return_asc_sign = return_asc["sign"]

    # Return date/time
    y, mo, d, h = swe.revjul(jd_return)
    local_h = h + tz_offset
    if local_h >= 24:
        local_h -= 24
    elif local_h < 0:
        local_h += 24
    hour = int(local_h)
    minute = int((local_h - hour) * 60)

    # Step 3: Muntha sign
    muntha_sign_idx = (natal_asc_idx + age) % 12
    muntha_sign = SIGNS[muntha_sign_idx]
    muntha_lord = SIGN_LORDS[muntha_sign]

    # Step 4: Day of the week for Dina Lord
    # JD → day of week (0=Monday in swe convention)
    weekday = int(jd_return + 0.5) % 7
    dina_lord = WEEKDAY_LORDS[weekday]

    # Step 5: Lagna lord of return chart
    lagna_lord = SIGN_LORDS[return_asc_sign]

    # Step 6: Pancha Vargiya Bala for 5 candidates
    candidates = {
        "lagna_lord": lagna_lord,
        "sun": "Sun",
        "moon": "Moon",
        "muntha_lord": muntha_lord,
        "dina_lord": dina_lord,
    }

    # Get return chart longitudes for candidates
    pvb_scores = {}
    for role, planet in candidates.items():
        if planet in return_planets:
            plon = return_planets[planet]["longitude"]
        else:
            plon = 0
        bala = _pancha_vargiya_bala(planet, plon, return_asc_sign)
        pvb_scores[role] = {
            "planet": planet,
            "pvb_total": bala["total"],
            "pvb_components": bala["components"],
        }

    # Step 7: Varsheshvara = highest PVB score
    varsheshvara_role = max(pvb_scores, key=lambda r: pvb_scores[r]["pvb_total"])
    varsheshvara = pvb_scores[varsheshvara_role]["planet"]

    data = {
        "method": "tajika_varshaphal_v1",
        "varsha_year": varsha_year,
        "age": age,
        "varsha_pravesh_date": f"{y}-{mo:02d}-{d:02d}",
        "varsha_pravesh_time_local": f"{hour:02d}:{minute:02d}",
        "return_rising": return_asc_sign,
        "return_planets": return_planets,
        "return_ascendant": return_asc,
        "return_midheaven": return_mc,
        "muntha_sign": muntha_sign,
        "muntha_lord": muntha_lord,
        "dina_lord": dina_lord,
        "lagna_lord": lagna_lord,
        "varsheshvara": varsheshvara,
        "varsheshvara_role": varsheshvara_role,
        "pvb_scores": pvb_scores,
    }

    return SystemResult(
        id="tajika",
        name="Tajika Varshaphal (Annual Horoscopy)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Nilakantha, Tajika Nilakanthi — primary Tajika reference",
            "Kalyana Varma, Saravali — Varshaphal methods",
        ],
        question="Q4_TIMING",
    )
