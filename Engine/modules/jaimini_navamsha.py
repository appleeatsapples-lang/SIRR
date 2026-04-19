"""Jaimini Navamsha (D9) — Divisional Chart of Dharma & Marriage — COMPUTED_STRICT

The Navamsha (D9) is the most important divisional chart in Vedic astrology.
It reveals marriage, dharma, and the soul's deeper purpose. In Jaimini,
the Karakamsha (Atmakaraka's D9 sign) is the foundation for reading
spiritual purpose and life direction.

Navamsha computation:
  - Each sign is divided into 9 equal parts (3°20' each)
  - Fire signs (Aries, Leo, Sagittarius): navamsha starts from Aries
  - Earth signs (Taurus, Virgo, Capricorn): starts from Capricorn
  - Air signs (Gemini, Libra, Aquarius): starts from Libra
  - Water signs (Cancer, Scorpio, Pisces): starts from Cancer

Vargottama: a planet in the same sign in D1 (rashi) and D9 is considered
especially strong — it has the same expression at both the manifest and
soul levels.

Pushkara Navamsha: certain navamsha divisions are considered especially
auspicious (degrees that fall in benefic-ruled navamshas).

Sources:
  - BPHS Ch. 6 (Divisional Charts)
  - Jaimini Upadesa Sutras (Karakamsha)
  - Sanjay Rath — Crux of Vedic Astrology
"""
from __future__ import annotations
import swisseph as swe
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
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

# Pushkara navamsha degrees (approximate — degrees where navamsha falls
# in a sign ruled by benefic planets Jupiter/Venus)
# These are the navamsha pada numbers (0-8) that land in benefic signs
BENEFIC_RULED_SIGNS = {"Taurus", "Cancer", "Sagittarius", "Pisces"}

# Planets to compute D9 for
D9_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _sign_of_longitude(lon: float) -> str:
    return SIGNS[int(lon / 30) % 12]


def _compute_navamsha(longitude: float) -> dict:
    """Compute D9 navamsha position from sidereal longitude."""
    sign_idx = int(longitude / 30) % 12
    natal_sign = SIGNS[sign_idx]
    element = SIGN_ELEMENTS[natal_sign]
    start = NAVAMSHA_STARTS[element]

    deg_in_sign = longitude % 30
    navamsha_pada = int(deg_in_sign / (30 / 9))
    if navamsha_pada > 8:
        navamsha_pada = 8

    d9_sign_idx = (start + navamsha_pada) % 12
    d9_sign = SIGNS[d9_sign_idx]

    # D9 degree: position within the navamsha division, scaled to 0-30
    d9_deg_raw = (deg_in_sign % (30 / 9)) * 9
    d9_degree = round(d9_deg_raw, 2)

    is_pushkara = d9_sign in BENEFIC_RULED_SIGNS

    return {
        "natal_sign": natal_sign,
        "d9_sign": d9_sign,
        "d9_degree": d9_degree,
        "navamsha_pada": navamsha_pada + 1,  # 1-based
        "is_pushkara": is_pushkara,
    }


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            karakas_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="jaimini_navamsha",
            name="Jaimini Navamsha (D9 — Dharma Chart)",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "Requires natal_chart_data"},
            interpretation=None,
            constants_version=constants.get("version", "unknown"),
            references=[],
        )

    # Convert to sidereal
    jd = natal_chart_data.get("julian_day", 2450349.8)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    d9_positions = {}
    vargottama = []
    pushkara_navamsha = []

    # Process planets
    for pname in D9_PLANETS:
        pdata = natal_chart_data.get("planets", {}).get(pname)
        if not pdata:
            continue
        trop_lon = pdata.get("longitude", 0)
        sid_lon = (trop_lon - ayanamsa) % 360
        natal_sign = _sign_of_longitude(sid_lon)

        d9 = _compute_navamsha(sid_lon)
        d9_positions[pname] = d9

        # Vargottama: same sign in D1 and D9
        if natal_sign == d9["d9_sign"]:
            vargottama.append(pname)

        # Pushkara navamsha
        if d9["is_pushkara"]:
            pushkara_navamsha.append(pname)

    # Process Rahu (North Node) and Ketu
    nn = natal_chart_data.get("planets", {}).get("North Node")
    if nn:
        nn_trop = nn.get("longitude", 0)
        # Rahu
        rahu_sid = (nn_trop - ayanamsa) % 360
        rahu_natal_sign = _sign_of_longitude(rahu_sid)
        rahu_d9 = _compute_navamsha(rahu_sid)
        d9_positions["Rahu"] = rahu_d9
        if rahu_natal_sign == rahu_d9["d9_sign"]:
            vargottama.append("Rahu")
        if rahu_d9["is_pushkara"]:
            pushkara_navamsha.append("Rahu")

        # Ketu
        ketu_sid = (rahu_sid + 180) % 360
        ketu_natal_sign = _sign_of_longitude(ketu_sid)
        ketu_d9 = _compute_navamsha(ketu_sid)
        d9_positions["Ketu"] = ketu_d9
        if ketu_natal_sign == ketu_d9["d9_sign"]:
            vargottama.append("Ketu")
        if ketu_d9["is_pushkara"]:
            pushkara_navamsha.append("Ketu")

    # Ascendant D9
    asc_data = natal_chart_data.get("ascendant")
    d9_ascendant = "unknown"
    if asc_data:
        asc_trop = asc_data.get("longitude", 0)
        asc_sid = (asc_trop - ayanamsa) % 360
        asc_d9 = _compute_navamsha(asc_sid)
        d9_ascendant = asc_d9["d9_sign"]
        d9_positions["Ascendant"] = asc_d9

    # Karakamsha — AK's D9 sign
    karakamsha = "unknown"
    atmakaraka_navamsha = "unknown"
    if karakas_data:
        ak = karakas_data.get("atmakaraka", {})
        ak_planet = ak.get("planet")
        if ak_planet and ak_planet in d9_positions:
            karakamsha = d9_positions[ak_planet]["d9_sign"]
            atmakaraka_navamsha = karakamsha
        elif karakas_data.get("karakamsha"):
            karakamsha = karakas_data["karakamsha"]
            atmakaraka_navamsha = karakamsha
    else:
        # Fallback: compute AK from planet degrees if no karakas_data
        best_planet = None
        best_deg = -1
        for pname in D9_PLANETS:
            if pname in d9_positions:
                pdata = natal_chart_data.get("planets", {}).get(pname)
                if pdata:
                    sid_lon = (pdata["longitude"] - ayanamsa) % 360
                    deg = sid_lon % 30
                    if deg > best_deg:
                        best_deg = deg
                        best_planet = pname
        if best_planet and best_planet in d9_positions:
            karakamsha = d9_positions[best_planet]["d9_sign"]
            atmakaraka_navamsha = karakamsha

    # Interpretation
    varg_str = ", ".join(vargottama) if vargottama else "none"
    interp = (
        f"D9 Ascendant {d9_ascendant}. "
        f"Vargottama planets: {varg_str} — "
    )
    if vargottama:
        interp += "these are especially strong as they occupy the same sign in both D1 and D9. "
    else:
        interp += "no planets share their D1 sign in D9. "
    interp += f"Karakamsha: {karakamsha}."

    data = {
        "d9_positions": d9_positions,
        "d9_ascendant": d9_ascendant,
        "vargottama": vargottama,
        "pushkara_navamsha": pushkara_navamsha,
        "atmakaraka_navamsha": atmakaraka_navamsha,
        "karakamsha": karakamsha,
    }

    return SystemResult(
        id="jaimini_navamsha",
        name="Jaimini Navamsha (D9 — Dharma Chart)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interp,
        constants_version=constants.get("version", "unknown"),
        references=[
            "BPHS Ch. 6 (Divisional Charts)",
            "Jaimini Upadesa Sutras (Karakamsha)",
            "Sanjay Rath — Crux of Vedic Astrology",
        ],
    )
