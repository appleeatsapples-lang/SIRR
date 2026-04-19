"""Shodashavarga — Vedic Divisional Charts — COMPUTED_STRICT
Computes the 6 most important divisional charts from the Shodashavarga scheme
(16 divisional charts). Each chart divides each sign into N equal parts,
producing a new "sign" placement that reveals different life domains.

Key divisional charts computed:
  D1  — Rasi (natal chart itself, reference baseline)
  D2  — Hora (wealth, financial capacity) — 2 divisions per sign
  D3  — Drekkana (siblings, courage) — 3 divisions per sign
  D9  — Navamsha (dharma, marriage, spiritual essence) — 9 divisions per sign
  D10 — Dashamsha (career, public role) — 10 divisions per sign
  D12 — Dwadashamsha (parents, ancestral karma) — 12 divisions per sign

Uses sidereal (Lahiri ayanamsha) positions.

Sources: Brihat Parashara Hora Shastra (BPHS),
         B.V. Raman (Hindu Predictive Astrology)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

DIVISIONS = {
    "D2":  {"n": 2,  "name": "Hora",        "domain": "wealth"},
    "D3":  {"n": 3,  "name": "Drekkana",    "domain": "siblings/courage"},
    "D9":  {"n": 9,  "name": "Navamsha",    "domain": "dharma/marriage"},
    "D10": {"n": 10, "name": "Dashamsha",   "domain": "career"},
    "D12": {"n": 12, "name": "Dwadashamsha", "domain": "parents/ancestry"},
}


def _divisional_sign(sid_longitude: float, n: int) -> int:
    """Compute the divisional chart sign index for a given sidereal longitude.

    Standard formula: For a planet at degree D in sign S (0-indexed),
    the Dn sign = (S * n + floor(D * n / 30)) % 12
    """
    sign_idx = int(sid_longitude // 30) % 12
    deg_in_sign = sid_longitude % 30
    div_part = int(deg_in_sign * n / 30)
    return (sign_idx * n + div_part) % 12


def _d2_hora(sid_longitude: float) -> int:
    """D2 Hora: first 15° → Sun's hora (Leo), second 15° → Moon's hora (Cancer).
    For odd signs: 0-15° = Leo (4), 15-30° = Cancer (3)
    For even signs: 0-15° = Cancer (3), 15-30° = Leo (4)
    """
    sign_idx = int(sid_longitude // 30) % 12
    deg_in_sign = sid_longitude % 30
    is_odd_sign = (sign_idx % 2) == 0  # Aries(0)=odd, Taurus(1)=even
    if deg_in_sign < 15:
        return 4 if is_odd_sign else 3  # Leo or Cancer
    else:
        return 3 if is_odd_sign else 4  # Cancer or Leo


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="shodashavarga", name="Shodashavarga (Vedic Divisional Charts)",
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
            id="shodashavarga", name="Shodashavarga (Vedic Divisional Charts)",
            certainty="NEEDS_INPUT",
            data={"error": "julian_day not in natal_chart_data"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    ayanamsha = swe.get_ayanamsa_ut(jd_ut)

    # Compute sidereal longitudes
    sid_lons = {}
    for name in PLANETS:
        trop_lon = natal_chart_data["planets"][name]["longitude"]
        sid_lons[name] = (trop_lon - ayanamsha) % 360

    # Also include ASC
    asc_sid = (natal_chart_data["ascendant"]["longitude"] - ayanamsha) % 360
    sid_lons["ASC"] = asc_sid

    # D1 — Rasi (baseline)
    d1 = {}
    for name, lon in sid_lons.items():
        d1[name] = SIGNS[int(lon // 30) % 12]

    # Compute each divisional chart
    varga_charts = {"D1": d1}

    for chart_key, info in DIVISIONS.items():
        n = info["n"]
        chart = {}
        for name, lon in sid_lons.items():
            if chart_key == "D2":
                sign_idx = _d2_hora(lon)
            else:
                sign_idx = _divisional_sign(lon, n)
            chart[name] = SIGNS[sign_idx]
        varga_charts[chart_key] = chart

    # Vimshopaka strength (simplified): count how many charts a planet is
    # in its own sign or exaltation sign
    DOMICILE = {
        "Sun": {"Leo"}, "Moon": {"Cancer"},
        "Mercury": {"Gemini", "Virgo"}, "Venus": {"Taurus", "Libra"},
        "Mars": {"Aries", "Scorpio"}, "Jupiter": {"Sagittarius", "Pisces"},
        "Saturn": {"Capricorn", "Aquarius"},
    }
    EXALT = {
        "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo",
        "Venus": "Pisces", "Mars": "Capricorn", "Jupiter": "Cancer",
        "Saturn": "Libra",
    }

    vimshopaka = {}
    for planet in PLANETS:
        dignified_count = 0
        for ck in varga_charts:
            sign = varga_charts[ck].get(planet, "")
            if sign in DOMICILE.get(planet, set()) or sign == EXALT.get(planet, ""):
                dignified_count += 1
        vimshopaka[planet] = dignified_count

    strongest = max(vimshopaka, key=vimshopaka.get)
    weakest = min(vimshopaka, key=vimshopaka.get)

    # Navamsha ASC sign (important for marriage/dharma analysis)
    navamsha_asc = varga_charts["D9"].get("ASC", "?")

    data = {
        "ayanamsha": round(ayanamsha, 4),
        "varga_charts": varga_charts,
        "navamsha_asc": navamsha_asc,
        "vimshopaka_scores": vimshopaka,
        "strongest_planet": strongest,
        "weakest_planet": weakest,
    }

    return SystemResult(
        id="shodashavarga",
        name="Shodashavarga (Vedic Divisional Charts)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Brihat Parashara Hora Shastra — Shodashavarga scheme",
            "B.V. Raman, Hindu Predictive Astrology — divisional charts",
        ],
        question="Q3_NATURE",
    )
