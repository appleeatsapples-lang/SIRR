"""Jaimini Chara Dasha — Sign-Based Timing System — COMPUTED_STRICT

Jaimini's rashi dasha: each Mahadasha is ruled by a zodiacal sign rather than
a planet. The sequence direction (direct/reverse) depends on odd/even sign
parity, and period length is the distance from the dasha sign to its lord.

Algorithm (K.N. Rao method):
  1. Start from Lagna sign (sidereal)
  2. Odd signs progress direct, even signs reverse
  3. Period = count from dasha sign to its lord (sign-inclusive, minus 1)
  4. Lord in own sign = 12 years
  5. Scorpio/Aquarius dual lords: use stronger lord
  6. Antardashas: divide Mahadasha into 12 equal sub-periods

Sources: Jaimini Upadesa Sutras (Sanjay Rath), K.N. Rao — Chara Dasha
"""
from __future__ import annotations
import swisseph as swe
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Odd signs (1-indexed): Aries=1, Gemini=3, Leo=5, Libra=7, Sagittarius=9, Aquarius=11
ODD_SIGNS = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}

# Single lordship map (standard Jaimini = Parashari lords)
LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Pisces": "Jupiter",
}

# Dual-lord signs
DUAL_LORDS = {
    "Scorpio": ("Mars", "Ketu"),
    "Aquarius": ("Saturn", "Rahu"),
}

# Rahu/Ketu are not planets in natal_chart_data; use North Node position
# Ketu is always 180° from Rahu (North Node)


def _sign_index(sign: str) -> int:
    return SIGNS.index(sign)


def _sign_of_longitude(lon: float) -> str:
    return SIGNS[int(lon / 30) % 12]


def _count_signs(from_sign: str, to_sign: str, forward: bool) -> int:
    """Count signs from `from_sign` to `to_sign` (inclusive of to_sign).
    Returns 1-12. If same sign, returns 12 (lord in own sign)."""
    fi = _sign_index(from_sign)
    ti = _sign_index(to_sign)
    if fi == ti:
        return 12
    if forward:
        return ((ti - fi) % 12)
    else:
        return ((fi - ti) % 12)


def _get_planet_sign(planets: dict, planet_name: str) -> str:
    """Get the sidereal sign of a planet."""
    if planet_name == "Rahu":
        lon = planets.get("North Node", {}).get("longitude", 0)
    elif planet_name == "Ketu":
        rahu_lon = planets.get("North Node", {}).get("longitude", 0)
        lon = (rahu_lon + 180) % 360
    else:
        lon = planets.get(planet_name, {}).get("longitude", 0)
    return _sign_of_longitude(lon)


def _planet_strength(planets: dict, planet_name: str) -> float:
    """Simple strength: degree within sign (higher = stronger for tie-breaking)."""
    if planet_name == "Rahu":
        lon = planets.get("North Node", {}).get("longitude", 0)
    elif planet_name == "Ketu":
        rahu_lon = planets.get("North Node", {}).get("longitude", 0)
        lon = (rahu_lon + 180) % 360
    else:
        lon = planets.get(planet_name, {}).get("longitude", 0)
    return lon % 30  # degree within sign


def _resolve_lord(dasha_sign: str, sid_planets: dict) -> tuple:
    """Resolve the lord of a dasha sign. For dual-lord signs, pick stronger."""
    if dasha_sign in DUAL_LORDS:
        lord1, lord2 = DUAL_LORDS[dasha_sign]
        # Count how many planets are in each lord's signs
        lord1_sign = _get_planet_sign(sid_planets, lord1)
        lord2_sign = _get_planet_sign(sid_planets, lord2)
        # Strength: degree within sign (higher = stronger)
        s1 = _planet_strength(sid_planets, lord1)
        s2 = _planet_strength(sid_planets, lord2)
        chosen = lord1 if s1 >= s2 else lord2
        return chosen, f"{lord1}/{lord2} → {chosen} (stronger)"
    else:
        lord = LORDS[dasha_sign]
        return lord, lord


def _compute_sidereal_planets(natal_data: dict) -> dict:
    """Convert tropical longitudes to sidereal (Lahiri) for all planets."""
    jd = natal_data.get("julian_day", 2450349.8)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    sid_planets = {}
    for name, pdata in natal_data.get("planets", {}).items():
        trop_lon = pdata.get("longitude", 0)
        sid_lon = (trop_lon - ayanamsa) % 360
        sid_planets[name] = {
            "longitude": sid_lon,
            "sign": _sign_of_longitude(sid_lon),
            "degree": int(sid_lon % 30),
        }
    # Also convert ASC
    if "ascendant" in natal_data:
        asc_trop = natal_data["ascendant"].get("longitude", 0)
        asc_sid = (asc_trop - ayanamsa) % 360
        sid_planets["_ascendant"] = {
            "longitude": asc_sid,
            "sign": _sign_of_longitude(asc_sid),
        }
    return sid_planets


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="chara_dasha",
            name="Jaimini Chara Dasha (Sign-Based Timing)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    sid_planets = _compute_sidereal_planets(natal_chart_data)

    # Starting sign = sidereal Lagna
    lagna_sign = sid_planets.get("_ascendant", {}).get("sign", "Aries")
    is_odd_lagna = lagna_sign in ODD_SIGNS

    # Build 12 Mahadasha periods
    dasha_sequence = []
    current_sign_idx = _sign_index(lagna_sign)
    direction = 1 if is_odd_lagna else -1

    for i in range(12):
        dasha_sign = SIGNS[current_sign_idx % 12]
        is_odd = dasha_sign in ODD_SIGNS
        lord, lord_note = _resolve_lord(dasha_sign, sid_planets)
        lord_sign = _get_planet_sign(sid_planets, lord)

        # Count from dasha sign to lord's sign
        count = _count_signs(dasha_sign, lord_sign, forward=is_odd)
        duration = count - 1 if count > 1 else 12  # lord in own = 12, otherwise count-1
        # Special: if count is 1 (adjacent), duration = 0 doesn't make sense → use count
        if duration == 0:
            duration = 12

        dasha_sequence.append({
            "sign": dasha_sign,
            "lord": lord,
            "lord_note": lord_note,
            "lord_sign": lord_sign,
            "duration_years": duration,
        })

        current_sign_idx = (current_sign_idx + direction) % 12

    # Compute cumulative ages and find current period
    dob = profile.dob
    today = profile.today if hasattr(profile, "today") else __import__("datetime").date.today()
    age_years = (today - dob).days / 365.25

    cumulative = 0
    current_dasha = None
    for entry in dasha_sequence:
        entry["start_age"] = round(cumulative, 2)
        cumulative += entry["duration_years"]
        entry["end_age"] = round(cumulative, 2)
        if current_dasha is None and age_years < cumulative:
            current_dasha = entry
            entry["is_current"] = True
        else:
            entry["is_current"] = False

    # Compute Antardashas for current period
    if current_dasha:
        antardasha_list = []
        md_sign = current_dasha["sign"]
        md_years = current_dasha["duration_years"]
        ad_years = md_years / 12
        ad_idx = _sign_index(md_sign)
        ad_dir = 1 if md_sign in ODD_SIGNS else -1
        for j in range(12):
            ad_sign = SIGNS[ad_idx % 12]
            antardasha_list.append({
                "sign": ad_sign,
                "duration_years": round(ad_years, 3),
            })
            ad_idx = (ad_idx + ad_dir) % 12
        current_dasha["antardashas"] = antardasha_list

    total_years = sum(e["duration_years"] for e in dasha_sequence)

    data = {
        "method": "kn_rao_chara_dasha_v1",
        "lagna_sign": lagna_sign,
        "lagna_parity": "odd" if is_odd_lagna else "even",
        "progression_direction": "direct" if is_odd_lagna else "reverse",
        "current_age": round(age_years, 2),
        "current_dasha_sign": current_dasha["sign"] if current_dasha else None,
        "current_dasha_lord": current_dasha["lord"] if current_dasha else None,
        "total_cycle_years": total_years,
        "dasha_sequence": dasha_sequence,
    }

    return SystemResult(
        id="chara_dasha",
        name="Jaimini Chara Dasha (Sign-Based Timing)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Jaimini Upadesa Sutras — Sanjay Rath translation",
            "K.N. Rao, Predicting through Jaimini's Chara Dasha",
        ],
        question="Q4_TIMING",
    )
