"""Nadi Amsa (D-150) — Tamil Vedic Micro-Division — COMPUTED_STRICT

The Nadi Amsa divides each sign into 150 equal micro-portions (amsas),
producing the finest-grained divisional chart in the Vedic system.
Each amsa maps to a Tattwa (element) and a Nadi group, providing
a precision layer beyond the standard Shodashavarga (16 divisions).

Algorithm:
  1. Convert all planet longitudes to sidereal (Lahiri ayanamsa)
  2. For each point: amsa_index = floor(degree_in_sign * 150 / 30) → 0-149
  3. Tattwa = cycle of 5 (Akash, Vayu, Agni, Jala, Prithvi) repeating 30x
  4. Nadi group = floor(amsa_index / 5) → 0-29, each with a traditional name
  5. Gender polarity = even/odd amsa_index

Sources: Nadi Jyotish tradition (Tamil), R. Santhanam's translation of
         Brihat Parashara Hora Shastra, Nadi Grantha literature
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

TATTWAS = ["Akash", "Vayu", "Agni", "Jala", "Prithvi"]

# 30 Nadi group names (traditional Tamil Nadi classification)
NADI_NAMES = [
    "Vasi", "Marichi", "Agastya", "Pulaha", "Atri",
    "Pulastya", "Kratu", "Vasishtha", "Angiras", "Bhrigu",
    "Narada", "Kashyapa", "Gautama", "Bharadvaja", "Vishvamitra",
    "Jamadagni", "Shandilya", "Parasara", "Garga", "Durvasa",
    "Vyasa", "Shaunaka", "Daksha", "Kanva", "Chyavana",
    "Maitreya", "Lomasha", "Jabali", "Suka", "Kaushika",
]

PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
           "Uranus", "Neptune", "Pluto"]


def _compute_nadi_amsa(sidereal_lon: float) -> dict:
    """Compute Nadi Amsa for a single sidereal longitude."""
    degree_in_sign = sidereal_lon % 30.0
    sign_idx = int(sidereal_lon // 30) % 12

    # 150 amsas per sign, each = 0.2 degrees
    amsa_index = int(degree_in_sign * 150 / 30)
    amsa_index = min(amsa_index, 149)  # clamp

    tattwa = TATTWAS[amsa_index % 5]
    nadi_group = amsa_index // 5
    nadi_name = NADI_NAMES[nadi_group]
    gender = "Even" if amsa_index % 2 == 0 else "Odd"

    return {
        "sidereal_sign": SIGNS[sign_idx],
        "degree_in_sign": round(degree_in_sign, 4),
        "amsa_index": amsa_index,
        "tattwa": tattwa,
        "nadi_group": nadi_group,
        "nadi_name": nadi_name,
        "gender": gender,
    }


def compute(profile: InputProfile, constants: dict,
            natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None or not profile.birth_time_local:
        return SystemResult(
            id="nadi_amsa", name="Nadi Amsa (D-150 Micro-Division)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data and birth time required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    import swisseph as swe

    jd_ut = natal_chart_data.get("julian_day")
    if jd_ut is None:
        return SystemResult(
            id="nadi_amsa", name="Nadi Amsa (D-150 Micro-Division)",
            certainty="NEEDS_INPUT",
            data={"error": "julian_day not in natal_chart_data"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    # Compute sidereal longitudes
    planets_data = natal_chart_data.get("planets", {})
    planet_amsas = {}

    for name in PLANETS:
        pdata = planets_data.get(name, {})
        trop_lon = pdata.get("longitude")
        if trop_lon is not None:
            sid_lon = (trop_lon - ayanamsa) % 360
            planet_amsas[name] = _compute_nadi_amsa(sid_lon)

    # Lagna (ASC)
    asc_data = natal_chart_data.get("ascendant", {})
    asc_lon = asc_data.get("longitude")
    lagna_amsa = None
    if asc_lon is not None:
        asc_sid = (asc_lon - ayanamsa) % 360
        lagna_amsa = _compute_nadi_amsa(asc_sid)

    # Moon Nadi Amsa (highlight)
    moon_amsa = planet_amsas.get("Moon")

    # Tattwa distribution
    tattwa_dist = {t: 0 for t in TATTWAS}
    all_amsas = list(planet_amsas.values())
    if lagna_amsa:
        all_amsas.append(lagna_amsa)
    for a in all_amsas:
        tattwa_dist[a["tattwa"]] += 1

    dominant_tattwa = max(tattwa_dist, key=tattwa_dist.get)

    data = {
        "method": "nadi_amsa_d150_v1",
        "ayanamsa": round(ayanamsa, 6),
        "ayanamsa_type": "Lahiri",
        "lagna_nadi_amsa": lagna_amsa,
        "moon_nadi_amsa": moon_amsa,
        "planet_nadi_amsas": planet_amsas,
        "dominant_tattwa": dominant_tattwa,
        "tattwa_distribution": tattwa_dist,
    }

    return SystemResult(
        id="nadi_amsa",
        name="Nadi Amsa (D-150 Micro-Division)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Nadi Jyotish tradition — Tamil Nadi Grantha literature",
            "R. Santhanam, Brihat Parashara Hora Shastra (translation)",
        ],
        question="Q3_NATURE",
    )
