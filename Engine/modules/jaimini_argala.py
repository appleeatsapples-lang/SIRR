"""Jaimini Argala — Planetary Intervention & Obstruction — COMPUTED_STRICT

Argala ("bolt") describes how planets in specific house relationships
create intervention (support) or obstruction (virodha-argala) on a
reference house. This is a core Jaimini technique for assessing which
houses/planets actively support or block a given area of life.

Primary argala positions from any reference house:
  2nd house = dhana argala (wealth intervention)
  4th house = sukha argala (happiness intervention)
  11th house = labha argala (gains intervention)
  5th house = suta argala (progeny/intelligence intervention)

Virodha (obstruction) positions:
  12th obstructs 2nd
  10th obstructs 4th
  3rd obstructs 11th
  9th obstructs 5th

Rule: Argala is blocked only if virodha has equal or more planets.

Sources:
  - Jaimini Upadesa Sutras 1.3.1–1.3.12
  - Sanjay Rath — Jaimini Maharishi's Upadesa Sutras
"""
from __future__ import annotations
import swisseph as swe
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# All planets to check for argala (traditional 9 grahas)
ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Argala positions: (name, house_offset, virodha_offset)
ARGALA_POSITIONS = [
    ("dhana_2nd", 2, 12),
    ("sukha_4th", 4, 10),
    ("labha_11th", 11, 3),
    ("suta_5th", 5, 9),
]


def _sign_of_longitude(lon: float) -> str:
    return SIGNS[int(lon / 30) % 12]


def _sign_at_offset(base_sign: str, offset: int) -> str:
    """Get the sign at a house offset from base (1-indexed: offset=2 means 2nd house)."""
    base_idx = SIGNS.index(base_sign)
    return SIGNS[(base_idx + offset - 1) % 12]


def _compute_sidereal_positions(natal_data: dict) -> dict:
    """Convert tropical longitudes to sidereal (Lahiri)."""
    jd = natal_data.get("julian_day", 2450349.8)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    sid = {}
    for name, pdata in natal_data.get("planets", {}).items():
        trop_lon = pdata.get("longitude", 0)
        sid_lon = (trop_lon - ayanamsa) % 360
        sid[name] = {
            "longitude": sid_lon,
            "sign": _sign_of_longitude(sid_lon),
        }
    # Ascendant
    if "ascendant" in natal_data:
        asc_trop = natal_data["ascendant"].get("longitude", 0)
        asc_sid = (asc_trop - ayanamsa) % 360
        sid["_ascendant"] = {
            "longitude": asc_sid,
            "sign": _sign_of_longitude(asc_sid),
        }
    return sid


def _planets_in_sign(sid_planets: dict, sign: str) -> list:
    """Return list of planet names in a given sign."""
    result = []
    for name, pdata in sid_planets.items():
        if name.startswith("_"):
            continue
        # Skip outer planets for traditional Jaimini
        if name in ("Uranus", "Neptune", "Pluto"):
            continue
        if pdata["sign"] == sign:
            # Map North Node to Rahu
            display_name = "Rahu" if name == "North Node" else name
            result.append(display_name)
    # Check Ketu (180° from North Node)
    nn = sid_planets.get("North Node")
    if nn:
        ketu_lon = (nn["longitude"] + 180) % 360
        ketu_sign = _sign_of_longitude(ketu_lon)
        if ketu_sign == sign:
            result.append("Ketu")
    return result


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="jaimini_argala",
            name="Jaimini Argala (Planetary Intervention)",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "Requires natal_chart_data"},
            interpretation=None,
            constants_version=constants.get("version", "unknown"),
            references=[],
        )

    sid_planets = _compute_sidereal_positions(natal_chart_data)
    asc_data = sid_planets.get("_ascendant")
    if not asc_data:
        return SystemResult(
            id="jaimini_argala",
            name="Jaimini Argala (Planetary Intervention)",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "No ascendant in natal_chart_data"},
            interpretation=None,
            constants_version=constants.get("version", "unknown"),
            references=[],
        )

    lagna_sign = asc_data["sign"]

    argala = {}
    virodha = {}
    net_score = 0

    for name, arg_offset, vir_offset in ARGALA_POSITIONS:
        arg_sign = _sign_at_offset(lagna_sign, arg_offset)
        vir_sign = _sign_at_offset(lagna_sign, vir_offset)

        arg_planets = _planets_in_sign(sid_planets, arg_sign)
        vir_planets = _planets_in_sign(sid_planets, vir_sign)

        # Argala is blocked if virodha planets >= argala planets
        if len(vir_planets) >= len(arg_planets) and len(arg_planets) > 0:
            strength = "blocked"
        elif len(arg_planets) > 0:
            strength = "strong"
            net_score += len(arg_planets) - len(vir_planets)
        else:
            strength = "clear"

        argala[name] = {
            "sign": arg_sign,
            "planets": arg_planets,
            "strength": strength,
        }

        # Store virodha with house number label
        vir_key = f"{vir_offset}th" if vir_offset not in (3, 12) else (
            "3rd" if vir_offset == 3 else "12th"
        )
        virodha[vir_key] = {
            "sign": vir_sign,
            "planets": vir_planets,
        }

    if net_score > 0:
        net_argala = "positive"
    elif net_score < 0:
        net_argala = "negative"
    else:
        net_argala = "neutral"

    # Count strong argalas
    strong_count = sum(1 for a in argala.values() if a["strength"] == "strong")
    blocked_count = sum(1 for a in argala.values() if a["strength"] == "blocked")

    interp = (
        f"Lagna in {lagna_sign}. "
        f"{strong_count} strong argala(s), {blocked_count} blocked. "
        f"Net argala: {net_argala}. "
    )
    # Detail the strong ones
    for name, adata in argala.items():
        if adata["strength"] == "strong" and adata["planets"]:
            interp += f"{name}: {', '.join(adata['planets'])} in {adata['sign']}. "

    data = {
        "reference": "Lagna",
        "lagna_sign": lagna_sign,
        "argala": argala,
        "virodha": virodha,
        "net_argala": net_argala,
        "strong_count": strong_count,
        "blocked_count": blocked_count,
    }

    return SystemResult(
        id="jaimini_argala",
        name="Jaimini Argala (Planetary Intervention)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interp,
        constants_version=constants.get("version", "unknown"),
        references=[
            "Jaimini Upadesa Sutras 1.3.1–1.3.12",
            "Sanjay Rath — Jaimini Maharishi's Upadesa Sutras",
        ],
    )
