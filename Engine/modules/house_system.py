"""House System — Whole Sign Houses (primary)
Given natal chart data (passed via kwargs), computes 12 house cusps
and assigns each planet to its house.

Whole Sign: the sign containing the Ascendant = House 1, next sign = House 2, etc.
Every house cusp is exactly 0° of its sign.

COMPUTED_STRICT when natal_chart_data is present, NEEDS_INPUT when missing.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="house_system",
            name="House System (Whole Sign)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    asc_sign = natal_chart_data["ascendant"]["sign"]
    asc_sign_idx = SIGNS.index(asc_sign)

    # Build 12 house cusps (Whole Sign: each house starts at 0° of its sign)
    houses = {}
    for i in range(12):
        house_num = i + 1
        sign_idx = (asc_sign_idx + i) % 12
        sign = SIGNS[sign_idx]
        cusp_degree = sign_idx * 30
        houses[f"house_{house_num}"] = {
            "sign": sign,
            "cusp_degree": cusp_degree,
        }

    # Assign planets to houses
    planets = natal_chart_data.get("planets", {})
    planet_houses = {}
    for planet_name, planet_data in planets.items():
        planet_lon = planet_data["longitude"]
        planet_sign_idx = int(planet_lon // 30) % 12
        # In Whole Sign, house number = (planet_sign_index - asc_sign_index) mod 12 + 1
        house_num = (planet_sign_idx - asc_sign_idx) % 12 + 1
        planet_houses[planet_name] = {
            "house": house_num,
            "sign": SIGNS[planet_sign_idx],
        }

    # Also assign Ascendant and MC
    mc_sign = natal_chart_data["midheaven"]["sign"]
    mc_sign_idx = SIGNS.index(mc_sign)
    mc_house = (mc_sign_idx - asc_sign_idx) % 12 + 1

    data = {
        "system": "Whole Sign",
        "ascending_sign": asc_sign,
        "houses": houses,
        "planet_houses": planet_houses,
        "mc_house": mc_house,
    }

    return SystemResult(
        id="house_system",
        name="House System (Whole Sign)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Whole Sign Houses — oldest house system (Hellenistic tradition)",
            "Each house = one complete zodiac sign, starting from Ascendant sign",
        ],
        question="Q1_IDENTITY",
    )
