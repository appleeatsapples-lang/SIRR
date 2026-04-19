"""Jaimini Chara Karakas — 7/8 Planet Significator Assignment — COMPUTED_STRICT

The Chara Karakas are Jaimini's unique significator system. Unlike fixed
Parashari karakas, these are assigned dynamically based on planetary degree
within sign — the planet at the highest degree becomes Atmakaraka (soul),
the next Amatyakaraka (career), etc.

Traditional 7-karaka system uses Sun through Saturn (excluding Rahu/Ketu
and outer planets). The 8-karaka variant adds Rahu as Darakaraka.

Sources:
  - Jaimini Upadesa Sutras (Sanjay Rath translation)
  - K.N. Rao — Predicting Through Jaimini's Chara Dasha
  - Iranganti Rangacharya — Jaimini Sutramritam
"""
from __future__ import annotations
import swisseph as swe
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# 7 traditional Jaimini planets
JAIMINI_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

KARAKA_NAMES = [
    ("atmakaraka", "AK", "Soul, self, the king"),
    ("amatyakaraka", "AmK", "Career, minister"),
    ("bhratrikaraka", "BK", "Siblings, courage"),
    ("matrikaraka", "MK", "Mother, home"),
    ("pitrikaraka", "PiK", "Father, dharma"),
    ("putrakaraka", "PuK", "Children, intelligence"),
    ("gnatikaraka", "GK", "Competition, disease"),
]

# Navamsha start signs by element
NAVAMSHA_STARTS = {
    "Fire": 0,    # Aries
    "Earth": 9,   # Capricorn
    "Air": 6,     # Libra
    "Water": 3,   # Cancer
}

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}


def _sign_of_longitude(lon: float) -> str:
    return SIGNS[int(lon / 30) % 12]


def _compute_navamsha_sign(longitude: float) -> str:
    """Compute D9 navamsha sign from tropical longitude."""
    sign_idx = int(longitude / 30) % 12
    sign_name = SIGNS[sign_idx]
    element = SIGN_ELEMENTS[sign_name]
    start = NAVAMSHA_STARTS[element]
    deg_in_sign = longitude % 30
    navamsha_idx = int(deg_in_sign / (30 / 9))
    if navamsha_idx > 8:
        navamsha_idx = 8
    d9_sign_idx = (start + navamsha_idx) % 12
    return SIGNS[d9_sign_idx]


def _compute_sidereal(natal_data: dict) -> tuple:
    """Convert tropical longitudes to sidereal (Lahiri). Returns (sid_planets, ayanamsa)."""
    jd = natal_data.get("julian_day", 2450349.8)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    sid_planets = {}
    for name, pdata in natal_data.get("planets", {}).items():
        trop_lon = pdata.get("longitude", 0)
        sid_lon = (trop_lon - ayanamsa) % 360
        sid_planets[name] = {
            "longitude": sid_lon,
            "sign": _sign_of_longitude(sid_lon),
            "degree_in_sign": round(sid_lon % 30, 4),
        }
    return sid_planets, ayanamsa


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="jaimini_karakas",
            name="Jaimini Chara Karakas (Significators)",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "Requires natal_chart_data"},
            interpretation=None,
            constants_version=constants.get("version", "unknown"),
            references=[],
        )

    sid_planets, ayanamsa = _compute_sidereal(natal_chart_data)

    # Extract degree within sign for each Jaimini planet
    planet_degrees = []
    for pname in JAIMINI_PLANETS:
        if pname in sid_planets:
            deg = sid_planets[pname]["degree_in_sign"]
            sign = sid_planets[pname]["sign"]
            lon = sid_planets[pname]["longitude"]
            planet_degrees.append((pname, deg, sign, lon))

    # Sort by degree within sign, descending — highest degree = AK
    planet_degrees.sort(key=lambda x: x[1], reverse=True)

    # Assign karakas
    karakas = {}
    for i, (karaka_key, abbrev, meaning) in enumerate(KARAKA_NAMES):
        if i < len(planet_degrees):
            pname, deg, sign, lon = planet_degrees[i]
            karakas[karaka_key] = {
                "planet": pname,
                "sign": sign,
                "degree_in_sign": round(deg, 2),
                "abbreviation": abbrev,
                "meaning": meaning,
            }

    # 8th karaka — Darakaraka (spouse) — Rahu if using 8-karaka system
    # Use the planet with lowest degree as Darakaraka in 7-karaka
    # In 8-karaka: Rahu's degree (counted reverse: 30 - degree)
    if "North Node" in sid_planets:
        rahu_deg = 30 - sid_planets["North Node"]["degree_in_sign"]
        karakas["darakaraka"] = {
            "planet": "Rahu",
            "sign": sid_planets["North Node"]["sign"],
            "degree_in_sign": round(rahu_deg, 2),
            "abbreviation": "DK",
            "meaning": "Spouse, partnerships",
            "note": "8-karaka variant (Rahu as DK)",
        }

    # AK's sign = Swamsha
    ak = karakas.get("atmakaraka", {})
    ak_sign = ak.get("sign", "unknown")

    # AK's Navamsha sign (use sidereal longitude for D9 — Vedic convention)
    ak_planet = ak.get("planet")
    ak_navamsha_sign = "unknown"
    if ak_planet and ak_planet in sid_planets:
        ak_sid_lon = sid_planets[ak_planet]["longitude"]
        ak_navamsha_sign = _compute_navamsha_sign(ak_sid_lon)

    # Interpretation
    ak_deg = ak.get("degree_in_sign", 0)
    interp = (
        f"Atmakaraka {ak.get('planet', '?')} at {ak_deg:.1f}° in {ak_sign} — "
        f"the soul's primary lesson and driving force. "
        f"Navamsha (D9) sign: {ak_navamsha_sign} (Karakamsha). "
        f"Amatyakaraka: {karakas.get('amatyakaraka', {}).get('planet', '?')} — "
        f"the minister supporting the soul's purpose."
    )

    data = {
        "system": "7-karaka (traditional)",
        **{k: v for k, v in karakas.items()},
        "ak_sign": ak_sign,
        "ak_navamsha_sign": ak_navamsha_sign,
        "karakamsha": ak_navamsha_sign,
    }

    return SystemResult(
        id="jaimini_karakas",
        name="Jaimini Chara Karakas (Significators)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interp,
        constants_version=constants.get("version", "unknown"),
        references=[
            "Jaimini Upadesa Sutras (Sanjay Rath translation)",
            "K.N. Rao — Predicting Through Jaimini's Chara Dasha",
            "Iranganti Rangacharya — Jaimini Sutramritam",
        ],
    )
