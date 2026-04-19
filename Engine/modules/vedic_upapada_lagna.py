"""Vedic Upapada Lagna — COMPUTED_STRICT
Same Arudha method as vedic_arudha_pada, but applied to 12th house lord instead of 1st.
Shows the nature of marriage partner / significant relationships.
Source: Parashara, BPHS Ch.29
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

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
    planets = natal_chart_data.get("planets", {})
    p = planets.get(planet_name, {})
    return p.get("sign", "")


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal_chart_data = kwargs.get("natal_chart_data")

    if not natal_chart_data or "ascendant" not in natal_chart_data:
        return SystemResult(
            id="vedic_upapada_lagna", name="Vedic Upapada Lagna",
            certainty="NEEDS_EPHEMERIS",
            data={"note": "Requires natal chart data"},
            interpretation=None, constants_version=constants["version"],
            references=["Parashara, BPHS Ch.29"],
            question="Q1_IDENTITY",
        )

    asc_sign = natal_chart_data.get("rising_sign", "")
    asc_idx = _sign_index(asc_sign)

    if asc_idx < 0:
        return SystemResult(
            id="vedic_upapada_lagna", name="Vedic Upapada Lagna",
            certainty="NEEDS_EPHEMERIS",
            data={"note": f"Could not resolve ascendant sign: {asc_sign}"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q1_IDENTITY",
        )

    # 12th house sign = sign before ascendant
    twelfth_idx = (asc_idx - 1) % 12
    twelfth_sign = SIGNS[twelfth_idx]

    # Lord of 12th house
    twelfth_lord = SIGN_LORD.get(twelfth_sign, "")
    lord_sign = _planet_sign(natal_chart_data, twelfth_lord)
    lord_idx = _sign_index(lord_sign)

    if lord_idx < 0:
        return SystemResult(
            id="vedic_upapada_lagna", name="Vedic Upapada Lagna",
            certainty="NEEDS_EPHEMERIS",
            data={"note": f"Could not find {twelfth_lord} sign in natal chart"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q1_IDENTITY",
        )

    # Count from 12th house to its lord
    houses_to_lord = (lord_idx - twelfth_idx) % 12 + 1

    # Count same from lord forward
    upapada_idx = (lord_idx + houses_to_lord - 1) % 12

    # Exception: if Upapada falls in 12th or 6th from 12th house, move 10
    dist = (upapada_idx - twelfth_idx) % 12
    if dist == 0 or dist == 6:
        upapada_idx = (upapada_idx + 10) % 12

    upapada_sign = SIGNS[upapada_idx]

    return SystemResult(
        id="vedic_upapada_lagna",
        name="Vedic Upapada Lagna",
        certainty="COMPUTED_STRICT",
        data={
            "lagna_sign": asc_sign,
            "twelfth_house_sign": twelfth_sign,
            "twelfth_lord": twelfth_lord,
            "lord_sign": lord_sign,
            "houses_to_lord": houses_to_lord,
            "upapada_sign": upapada_sign,
            "upapada_index": upapada_idx,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Parashara, 'Brihat Parashara Hora Shastra', Ch.29: Upapada Lagna",
            "SOURCE_TIER:A — Classical Vedic text.",
        ],
        question="Q1_IDENTITY",
    )
