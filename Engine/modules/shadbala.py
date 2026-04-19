"""Shadbala (ṣaḍbala — Six-Fold Planetary Strength)
Computes relative strength of 7 classical Vedic planets across 4 of 6 components:
  1. Uchcha Bala (exaltation strength)
  2. Dignity Bala (D1 Saptavargaja component)
  3. Dig Bala (directional strength)
  4. Kala Bala: Nathonnatha (day/night) + Paksha (lunar phase, Moon only)

Omits: full Saptavargaja (D2-D30 divisional charts), Cheshta Bala (motional speed).
Uses SIDEREAL (Lahiri) positions computed internally — NOT tropical natal_chart_data.
Gated on birth_time_local, timezone, and location.

Source: Parashara, BPHS Ch.27; B.V. Raman, Graha and Bhava Balas (1992).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PLANETS_7 = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
SWE_IDS = {"Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4, "Jupiter": 5, "Saturn": 6}

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

TZ_OFFSETS = {
    "Asia/Riyadh": 3, "Asia/Dubai": 4, "Asia/Kuwait": 3,
    "Asia/Amman": 2, "Africa/Cairo": 2, "Asia/Beirut": 2,
    "Asia/Damascus": 2, "Asia/Baghdad": 3, "Europe/Istanbul": 3,
    "Europe/London": 0, "America/New_York": -5, "UTC": 0,
}

# ── Uchcha Bala: exaltation degrees (sidereal) ──
EXALT_DEG = {
    "Sun": 10, "Moon": 33, "Mercury": 165, "Venus": 357,
    "Mars": 298, "Jupiter": 95, "Saturn": 200,
}

# ── Dignity Bala (D1): sign rulers ──
RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

MOOLATRIKONA = {
    "Sun": ("Leo", 0, 20), "Moon": ("Taurus", 4, 30), "Mercury": ("Virgo", 16, 20),
    "Venus": ("Libra", 0, 15), "Mars": ("Aries", 0, 12),
    "Jupiter": ("Sagittarius", 0, 10), "Saturn": ("Aquarius", 0, 20),
}

EXALT_SIGN = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo", "Venus": "Pisces",
    "Mars": "Capricorn", "Jupiter": "Cancer", "Saturn": "Libra",
}

DEBIL_SIGN = {p: SIGNS[(SIGNS.index(s) + 6) % 12] for p, s in EXALT_SIGN.items()}

# Natural friendships (Parashara)
FRIENDS = {
    "Sun":     {"F": {"Moon", "Mars", "Jupiter"},           "E": {"Venus", "Saturn"}},
    "Moon":    {"F": {"Sun", "Mercury"},                    "E": set()},
    "Mercury": {"F": {"Sun", "Venus"},                      "E": {"Moon"}},
    "Venus":   {"F": {"Mercury", "Saturn"},                  "E": {"Sun", "Moon"}},
    "Mars":    {"F": {"Sun", "Moon", "Jupiter"},             "E": {"Mercury"}},
    "Jupiter": {"F": {"Sun", "Moon", "Mars"},                "E": {"Mercury", "Venus"}},
    "Saturn":  {"F": {"Mercury", "Venus"},                   "E": {"Sun", "Moon", "Mars"}},
}

# ── Dig Bala: preferred houses ──
DIG_PREFERRED_HOUSE = {
    "Sun": 10, "Moon": 4, "Mercury": 1,
    "Venus": 4, "Mars": 10, "Jupiter": 1, "Saturn": 7,
}

# ── Kala Bala: day/night planets ──
DAY_PLANETS = {"Sun", "Jupiter", "Saturn"}
NIGHT_PLANETS = {"Moon", "Venus", "Mars"}


def _uchcha_bala(planet: str, lon: float) -> float:
    ex = EXALT_DEG[planet]
    dist = abs(lon - ex) % 360
    if dist > 180:
        dist = 360 - dist
    return round((180 - dist) / 3, 2)


def _dignity_bala(planet: str, lon: float) -> tuple[float, str]:
    sign_idx = int(lon // 30) % 12
    sign = SIGNS[sign_idx]
    deg_in_sign = lon % 30

    # Check moolatrikona
    mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]
    if sign == mt_sign and mt_start <= deg_in_sign < mt_end:
        return 45.0, "Moolatrikona"

    # Check own sign (swakshetra)
    own_signs = [s for s, r in RULERS.items() if r == planet]
    if sign in own_signs:
        return 30.0, "Swakshetra"

    # Check exaltation
    if sign == EXALT_SIGN[planet]:
        return 30.0, "Exalted"  # Treated as own-sign level if not in MT range

    # Check debilitation
    if sign == DEBIL_SIGN[planet]:
        return 0.0, "Debilitated"

    # Check friendship
    ruler = RULERS[sign]
    if ruler == planet:
        return 30.0, "Swakshetra"

    if ruler in FRIENDS[planet]["F"]:
        return 22.5, "Friend"
    elif ruler in FRIENDS[planet]["E"]:
        return 7.5, "Enemy"
    else:
        return 15.0, "Neutral"


def _dig_bala(planet: str, planet_lon: float, lagna_sign_idx: int) -> float:
    preferred = DIG_PREFERRED_HOUSE[planet]
    cusp = ((lagna_sign_idx + preferred - 1) % 12) * 30
    dist = abs(planet_lon - cusp) % 360
    if dist > 180:
        dist = 360 - dist
    return round((180 - dist) / 3, 2)


def _nathonnatha_bala(planet: str, is_day: bool) -> float:
    if planet in DAY_PLANETS:
        return 60.0 if is_day else 0.0
    if planet in NIGHT_PLANETS:
        return 60.0 if not is_day else 0.0
    return 30.0  # Mercury


def _paksha_bala(moon_lon: float, sun_lon: float) -> tuple[float, int, bool]:
    tithi = int(((moon_lon - sun_lon) % 360) / 12) + 1
    is_shukla = tithi <= 15
    moon_score = 60.0 if is_shukla else 0.0
    return moon_score, tithi, is_shukla


TITHI_NAMES = {
    1: "Shukla Pratipada", 2: "Shukla Dwitiya", 3: "Shukla Tritiya",
    4: "Shukla Chaturthi", 5: "Shukla Panchami", 6: "Shukla Shashthi",
    7: "Shukla Saptami", 8: "Shukla Ashtami", 9: "Shukla Navami",
    10: "Shukla Dashami", 11: "Shukla Ekadashi", 12: "Shukla Dwadashi",
    13: "Shukla Trayodashi", 14: "Shukla Chaturdashi", 15: "Purnima",
    16: "Krishna Pratipada", 17: "Krishna Dwitiya", 18: "Krishna Tritiya",
    19: "Krishna Chaturthi", 20: "Krishna Panchami", 21: "Krishna Shashthi",
    22: "Krishna Saptami", 23: "Krishna Ashtami", 24: "Krishna Navami",
    25: "Krishna Dashami", 26: "Krishna Ekadashi", 27: "Krishna Dwadashi",
    28: "Krishna Trayodashi", 29: "Krishna Chaturdashi", 30: "Amavasya",
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    if not profile.birth_time_local:
        return SystemResult(
            id="shadbala",
            name="Shadbala (Six-Fold Planetary Strength)",
            certainty="NEEDS_INPUT",
            data={"applicable": False, "reason": "birth_time_local required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    # Resolve coordinates: prefer profile lat/lng (from geocoder), fall back to LOCATIONS dict
    if getattr(profile, 'latitude', None) is not None and getattr(profile, 'longitude', None) is not None:
        lat, lon = profile.latitude, profile.longitude
        tz_offset = getattr(profile, 'utc_offset', None)
        if tz_offset is None:
            tz_offset = TZ_OFFSETS.get(profile.timezone, 3)
    elif profile.location:
        coords = LOCATIONS.get(profile.location)
        if coords is None:
            return SystemResult(
                id="shadbala",
                name="Shadbala (Six-Fold Planetary Strength)",
                certainty="NEEDS_INPUT",
                data={"applicable": False, "reason": f"Unknown location: {profile.location}"},
                interpretation=None,
                constants_version=constants["version"],
                references=[],
                question="Q1_IDENTITY",
            )
        lat, lon = coords
        tz_offset = TZ_OFFSETS.get(profile.timezone)
        if tz_offset is None:
            return SystemResult(
                id="shadbala",
                name="Shadbala (Six-Fold Planetary Strength)",
                certainty="NEEDS_INPUT",
                data={"applicable": False, "reason": f"Unknown timezone: {profile.timezone}"},
                interpretation=None,
                constants_version=constants["version"],
                references=[],
                question="Q1_IDENTITY",
            )
    else:
        return SystemResult(
            id="shadbala",
            name="Shadbala (Six-Fold Planetary Strength)",
            certainty="NEEDS_INPUT",
            data={"applicable": False, "reason": "location or coordinates required"},
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

    # Compute SIDEREAL positions (Lahiri ayanamsa)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    positions = {}
    for name in PLANETS_7:
        result = swe.calc_ut(jd_ut, SWE_IDS[name], swe.FLG_SIDEREAL)
        positions[name] = result[0][0]

    # Sidereal Ascendant
    cusps, asmc = swe.houses_ex(jd_ut, lat, lon, b'W', swe.FLG_SIDEREAL)
    asc_lon = asmc[0]
    lagna_sign_idx = int(asc_lon // 30) % 12
    lagna_sign = SIGNS[lagna_sign_idx]

    # Determine house for each planet (Whole Sign from sidereal lagna)
    planet_houses = {}
    for name in PLANETS_7:
        p_sign_idx = int(positions[name] // 30) % 12
        house = ((p_sign_idx - lagna_sign_idx) % 12) + 1
        planet_houses[name] = house

    # Is it daytime? Sun above horizon = daytime
    sun_lon = positions["Sun"]
    # Simple check: Sun in houses 7-12 (above horizon in whole sign)
    sun_house = planet_houses["Sun"]
    is_daytime = sun_house >= 7  # Houses 7-12 are above horizon

    # For birth at 10:14 AM, it's clearly daytime — verify with hour
    birth_hour = int(profile.birth_time_local.split(":")[0])
    if birth_hour >= 6 and birth_hour < 18:
        is_daytime = True
    elif birth_hour >= 18 or birth_hour < 6:
        is_daytime = False

    # Paksha Bala (Moon phase)
    moon_paksha, tithi, is_shukla = _paksha_bala(positions["Moon"], positions["Sun"])
    tithi_name = TITHI_NAMES.get(tithi, f"Tithi {tithi}")

    # Compute all components for each planet
    planets_data = {}
    totals = {}
    for name in PLANETS_7:
        p_lon = positions[name]
        uchcha = _uchcha_bala(name, p_lon)
        dignity, dignity_label = _dignity_bala(name, p_lon)
        dig = _dig_bala(name, p_lon, lagna_sign_idx)
        natho = _nathonnatha_bala(name, is_daytime)
        paksha = moon_paksha if name == "Moon" else 0.0
        total = round(uchcha + dignity + dig + natho + paksha, 1)

        planets_data[name] = {
            "uchcha": uchcha,
            "dignity": dignity,
            "dig": dig,
            "nathonnatha": natho,
            "paksha": paksha,
            "total": total,
            "dignity_label": dignity_label,
            "house": planet_houses[name],
        }
        totals[name] = total

    # Ranking
    ranking = sorted(PLANETS_7, key=lambda p: totals[p], reverse=True)
    strongest = ranking[0]
    weakest = ranking[-1]

    data = {
        "applicable": True,
        "components_computed": ["uchcha_bala", "dignity_d1", "dig_bala", "nathonnatha", "paksha_bala"],
        "components_omitted": ["saptavargaja_d2_d30", "cheshta_bala"],
        "tithi": tithi,
        "tithi_name": tithi_name,
        "is_waxing": is_shukla,
        "is_daytime": is_daytime,
        "lagna": lagna_sign,
        "planets": planets_data,
        "ranking": ranking,
        "strongest": strongest,
        "weakest": weakest,
        "note": "Partial Shadbala: 4 of 6 components. Omits D2-D30 Saptavargaja and Cheshta Bala (motional speed).",
    }

    strong_total = planets_data[strongest]["total"]
    weak_total = planets_data[weakest]["total"]
    interp = (
        f"{strongest} strongest ({strong_total} virupas): "
        f"{planets_data[strongest]['dignity_label']} dignity, "
        f"house {planets_data[strongest]['house']}. "
        f"{weakest} weakest ({weak_total}): "
        f"{planets_data[weakest]['dignity_label']} dignity. "
        f"{'Daytime' if is_daytime else 'Nighttime'} birth "
        f"({'strengthens Sun, Jupiter, Saturn' if is_daytime else 'strengthens Moon, Venus, Mars'})."
    )

    return SystemResult(
        id="shadbala",
        name="Shadbala (Six-Fold Planetary Strength)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interp,
        constants_version=constants["version"],
        references=[
            "Parashara, BPHS Ch.27 — Shadbala calculation method",
            "B.V. Raman, Graha and Bhava Balas (1992) — practical computation guide",
            "Swiss Ephemeris — Lahiri sidereal positions",
        ],
        question="Q1_IDENTITY",
    )
