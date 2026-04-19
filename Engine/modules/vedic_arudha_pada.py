"""Vedic Arudha Pada (Arudha Lagna) — COMPUTED_STRICT
(1) Find Lagna (Ascendant) sign. (2) Find Lagna lord's sign.
(3) Count houses from Lagna to Lagna lord. (4) Count same from Lagna lord forward.
(5) Exception: if result is 1st or 7th from Lagna, add 10 houses.
Result = Arudha Lagna sign.
Source: Parashara, "Brihat Parashara Hora Shastra", Ch.29
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Traditional sign rulers (Vedic — uses traditional rulers only)
SIGN_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}


def _sign_index(sign_name):
    try:
        return SIGNS.index(sign_name)
    except ValueError:
        return -1


def _planet_sign(natal_chart_data, planet_name):
    """Get the sign a planet is in from natal_chart_data."""
    planets = natal_chart_data.get("planets", {})
    p = planets.get(planet_name, {})
    return p.get("sign", "")


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal_chart_data = kwargs.get("natal_chart_data")

    if not natal_chart_data or "ascendant" not in natal_chart_data:
        return SystemResult(
            id="vedic_arudha_pada", name="Vedic Arudha Pada",
            certainty="NEEDS_EPHEMERIS",
            data={"note": "Requires natal chart data (ascendant + planet positions)"},
            interpretation=None, constants_version=constants["version"],
            references=["Parashara, BPHS Ch.29"],
            question="Q1_IDENTITY",
        )

    asc_sign = natal_chart_data.get("rising_sign", "")
    asc_idx = _sign_index(asc_sign)

    if asc_idx < 0:
        return SystemResult(
            id="vedic_arudha_pada", name="Vedic Arudha Pada",
            certainty="NEEDS_EPHEMERIS",
            data={"note": f"Could not resolve ascendant sign: {asc_sign}"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q1_IDENTITY",
        )

    lagna_lord = SIGN_LORD.get(asc_sign, "")
    lord_sign = _planet_sign(natal_chart_data, lagna_lord)
    lord_idx = _sign_index(lord_sign)

    if lord_idx < 0:
        return SystemResult(
            id="vedic_arudha_pada", name="Vedic Arudha Pada",
            certainty="NEEDS_EPHEMERIS",
            data={"note": f"Could not find {lagna_lord} sign in natal chart"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q1_IDENTITY",
        )

    # Count from Lagna to lord (inclusive of starting sign = 1)
    houses_to_lord = (lord_idx - asc_idx) % 12 + 1

    # Count same from lord forward
    arudha_idx = (lord_idx + houses_to_lord - 1) % 12

    # Exception: if Arudha falls in 1st or 7th from Lagna, move 10 houses
    dist = (arudha_idx - asc_idx) % 12
    if dist == 0 or dist == 6:
        arudha_idx = (arudha_idx + 10) % 12

    arudha_sign = SIGNS[arudha_idx]

    return SystemResult(
        id="vedic_arudha_pada",
        name="Vedic Arudha Pada (Arudha Lagna)",
        certainty="COMPUTED_STRICT",
        data={
            "lagna_sign": asc_sign,
            "lagna_lord": lagna_lord,
            "lord_sign": lord_sign,
            "houses_to_lord": houses_to_lord,
            "arudha_lagna_sign": arudha_sign,
            "arudha_lagna_index": arudha_idx,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Parashara, 'Brihat Parashara Hora Shastra', Ch.29: Arudha Pada",
            "SOURCE_TIER:A — Classical Vedic text.",
        ],
        question="Q1_IDENTITY",
    )
