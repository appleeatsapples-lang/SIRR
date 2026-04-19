"""Ashtakavarga — Vedic Benefic Point System — COMPUTED_STRICT
Computes the Sarvashtakavarga (combined benefic point table) for all 12 signs.
Each of the 7 traditional planets contributes benefic points (bindus) to signs
based on their positions relative to each other and the Ascendant.

For each planet, there are 8 contributors (7 planets + Ascendant) each providing
bindus to specific houses counted from the contributor's sign. The BAV (Bhinna
Ashtakavarga) is per-planet; the SAV (Sarva Ashtakavarga) is the sum.

A sign with SAV >= 28 is strong for transits; <= 25 is weak.
Maximum possible SAV per sign = 56 (8 contributors × 7 bindus max).

Uses sidereal (Lahiri ayanamsha) positions for Jyotish accuracy.

Sources: Brihat Parashara Hora Shastra (BPHS),
         B.V. Raman (Ashtakavarga System of Prediction)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Ashtakavarga contribution tables (BPHS standard)
# Key: beneficiary planet → contributor → list of houses (1-indexed) from contributor
# where beneficiary gets a bindu
BAV_TABLES = {
    "Sun": {
        "Sun":     [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon":    [3, 6, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus":   [6, 7, 12],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "ASC":     [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun":     [3, 6, 7, 8, 10, 11],
        "Moon":    [1, 3, 6, 7, 10, 11],
        "Mars":    [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus":   [3, 4, 5, 7, 9, 10, 11],
        "Saturn":  [3, 5, 6, 11],
        "ASC":     [3, 6, 10, 11],
    },
    "Mars": {
        "Sun":     [3, 5, 6, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus":   [6, 8, 11, 12],
        "Saturn":  [1, 4, 7, 8, 9, 10, 11],
        "ASC":     [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun":     [5, 6, 9, 11, 12],
        "Moon":    [2, 4, 6, 8, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "ASC":     [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun":     [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon":    [2, 5, 7, 9, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus":   [2, 5, 6, 9, 10, 11],
        "Saturn":  [3, 5, 6, 12],
        "ASC":     [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun":     [8, 11, 12],
        "Moon":    [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars":    [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn":  [3, 4, 5, 8, 9, 10, 11],
        "ASC":     [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun":     [1, 2, 4, 7, 8, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus":   [6, 11, 12],
        "Saturn":  [3, 5, 6, 11],
        "ASC":     [1, 3, 4, 6, 10, 11],
    },
}


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="ashtakavarga", name="Ashtakavarga (Vedic Benefic Points)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    import swisseph as swe
    swe.set_ephe_path(None)

    jd_ut = natal_chart_data.get("julian_day")
    if jd_ut is None:
        return SystemResult(
            id="ashtakavarga", name="Ashtakavarga (Vedic Benefic Points)",
            certainty="NEEDS_INPUT",
            data={"error": "julian_day not in natal_chart_data"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    # Get Lahiri ayanamsha for sidereal conversion
    ayanamsha = swe.get_ayanamsa_ut(jd_ut)

    # Compute sidereal sign positions for planets and ASC
    planet_signs = {}
    for name in PLANETS_7:
        trop_lon = natal_chart_data["planets"][name]["longitude"]
        sid_lon = (trop_lon - ayanamsha) % 360
        planet_signs[name] = int(sid_lon // 30) % 12

    asc_sid = (natal_chart_data["ascendant"]["longitude"] - ayanamsha) % 360
    asc_sign = int(asc_sid // 30) % 12

    # Compute BAV (per-planet) and SAV (combined)
    sav = [0] * 12  # Sarvashtakavarga: total bindus per sign
    bav_summary = {}

    for beneficiary in PLANETS_7:
        bav_row = [0] * 12
        table = BAV_TABLES[beneficiary]

        for contributor in PLANETS_7:
            c_sign = planet_signs[contributor]
            houses = table.get(contributor, [])
            for h in houses:
                target_sign = (c_sign + h - 1) % 12
                bav_row[target_sign] += 1

        # ASC contribution
        houses = table.get("ASC", [])
        for h in houses:
            target_sign = (asc_sign + h - 1) % 12
            bav_row[target_sign] += 1

        bav_total = sum(bav_row)
        bav_summary[beneficiary] = {
            "total_bindus": bav_total,
            "sign_bindus": {SIGNS[i]: bav_row[i] for i in range(12)},
        }

        for i in range(12):
            sav[i] += bav_row[i]

    # SAV analysis
    sav_data = {SIGNS[i]: sav[i] for i in range(12)}
    strongest_sign = max(sav_data, key=sav_data.get)
    weakest_sign = min(sav_data, key=sav_data.get)
    strongest_bindus = sav_data[strongest_sign]
    weakest_bindus = sav_data[weakest_sign]

    data = {
        "ayanamsha": round(ayanamsha, 4),
        "sarvashtakavarga": sav_data,
        "strongest_sign": strongest_sign,
        "strongest_bindus": strongest_bindus,
        "weakest_sign": weakest_sign,
        "weakest_bindus": weakest_bindus,
        "bav_totals": {p: bav_summary[p]["total_bindus"] for p in PLANETS_7},
    }

    return SystemResult(
        id="ashtakavarga",
        name="Ashtakavarga (Vedic Benefic Points)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Brihat Parashara Hora Shastra (BPHS) — Ashtakavarga tables",
            "B.V. Raman, Ashtakavarga System of Prediction",
        ],
        question="Q3_NATURE",
    )
