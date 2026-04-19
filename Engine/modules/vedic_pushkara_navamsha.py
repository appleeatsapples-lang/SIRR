"""Vedic Pushkara Navamsha — COMPUTED_STRICT
Check if natal Moon or Ascendant falls in specific "nourished" degree ranges.
Fixed lookup table of Pushkara Navamshas per sign.
Source: Classical Jyotish Pushkara Navamsha tables
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Pushkara Navamsha degree ranges per sign (each navamsha = 3°20')
# A navamsha is Pushkara if it falls in a sign ruled by a benefic (Venus, Jupiter, Mercury, Moon)
# The specific navamshas that are Pushkara, expressed as (start_degree, end_degree) within each sign
# Source: Jyotish classical texts (Jataka Parijata, Uttara Kalamrita)
PUSHKARA_RANGES = {
    "Aries":       [(20.0, 23.333), (26.667, 30.0)],                    # 7th, 9th navamsha
    "Taurus":      [(3.333, 6.667), (13.333, 16.667)],                  # 2nd, 5th
    "Gemini":      [(6.667, 10.0), (23.333, 26.667)],                   # 3rd, 8th
    "Cancer":      [(0.0, 3.333), (20.0, 23.333)],                      # 1st, 7th
    "Leo":         [(16.667, 20.0), (26.667, 30.0)],                    # 6th, 9th
    "Virgo":       [(3.333, 6.667), (13.333, 16.667)],                  # 2nd, 5th
    "Libra":       [(6.667, 10.0), (23.333, 26.667)],                   # 3rd, 8th
    "Scorpio":     [(0.0, 3.333), (20.0, 23.333)],                      # 1st, 7th
    "Sagittarius": [(16.667, 20.0), (26.667, 30.0)],                    # 6th, 9th
    "Capricorn":   [(3.333, 6.667), (13.333, 16.667)],                  # 2nd, 5th
    "Aquarius":    [(6.667, 10.0), (23.333, 26.667)],                   # 3rd, 8th
    "Pisces":      [(0.0, 3.333), (20.0, 23.333)],                      # 1st, 7th
}


def _check_pushkara(longitude):
    """Check if a tropical longitude falls in a Pushkara Navamsha."""
    sign_idx = int(longitude / 30) % 12
    sign = SIGNS[sign_idx]
    deg_in_sign = longitude % 30

    ranges = PUSHKARA_RANGES.get(sign, [])
    for lo, hi in ranges:
        if lo <= deg_in_sign < hi:
            return True, sign, round(deg_in_sign, 2)
    return False, sign, round(deg_in_sign, 2)


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal_chart_data = kwargs.get("natal_chart_data")

    if not natal_chart_data or "planets" not in natal_chart_data:
        return SystemResult(
            id="vedic_pushkara_navamsha", name="Vedic Pushkara Navamsha",
            certainty="NEEDS_EPHEMERIS",
            data={"note": "Requires natal chart data (Moon/Asc longitude)"},
            interpretation=None, constants_version=constants["version"],
            references=["Classical Jyotish Pushkara Navamsha tables"],
            question="Q1_IDENTITY",
        )

    moon_lon = natal_chart_data.get("planets", {}).get("Moon", {}).get("longitude")
    asc_lon = natal_chart_data.get("ascendant", {}).get("longitude")

    results = {}

    if moon_lon is not None:
        is_p, sign, deg = _check_pushkara(moon_lon)
        results["moon_pushkara"] = is_p
        results["moon_sign"] = sign
        results["moon_degree_in_sign"] = deg

    if asc_lon is not None:
        is_p, sign, deg = _check_pushkara(asc_lon)
        results["asc_pushkara"] = is_p
        results["asc_sign"] = sign
        results["asc_degree_in_sign"] = deg

    results["pushkara_status"] = results.get("moon_pushkara", False) or results.get("asc_pushkara", False)

    return SystemResult(
        id="vedic_pushkara_navamsha",
        name="Vedic Pushkara Navamsha",
        certainty="COMPUTED_STRICT",
        data=results,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Classical Jyotish: Pushkara Navamsha = 'nourished' divisions in benefic-ruled signs",
            "Jataka Parijata, Uttara Kalamrita: Pushkara degree tables",
            "SOURCE_TIER:A — Classical Vedic texts.",
        ],
        question="Q1_IDENTITY",
    )
