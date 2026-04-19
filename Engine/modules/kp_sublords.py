"""KP Sub-Lord System — Three-Tier Sub-Lord Hierarchy — COMPUTED_STRICT

Extended KP analysis computing Star Lord, Sub Lord, and Sub-Sub Lord (SSL)
for key chart points using Vimshottari dasha proportions. The sub-lord is
the key predictive element; the SSL adds further granularity.

KP divides each nakshatra (13°20') into 9 sub-lords proportional to
Vimshottari dasha years (total 120). Each sub-lord span is further
divided into 9 sub-sub-lords using the same proportional system.

Also computes house cuspal sub-lords for significator analysis —
the cuspal sub-lord determines which house matters a planet can deliver.

Sources:
  - K.S. Krishnamurti — KP Reader I-VI
  - Vimshottari dasha proportions for 249 sub-lord table
  - KP Ayanamsha (Lahiri) for sidereal conversion
"""
from __future__ import annotations
import swisseph as swe
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]

# Vimshottari dasha sequence and years
KP_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
KP_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
TOTAL_YEARS = 120

# 27 Nakshatras
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Nakshatra lords cycle through KP_SEQUENCE
NAKSHATRA_LORDS = [KP_SEQUENCE[i % 9] for i in range(27)]

NAKSHATRA_SPAN = 360.0 / 27  # 13°20' = 13.33333°

# Planet meanings for interpretation
PLANET_SIGNIFICATIONS = {
    "Sun": "authority, father, government",
    "Moon": "mind, mother, emotions",
    "Mars": "energy, siblings, property",
    "Mercury": "intellect, communication, commerce",
    "Jupiter": "wisdom, expansion, children",
    "Venus": "relationships, luxury, arts",
    "Saturn": "discipline, delays, longevity",
    "Rahu": "unconventional, foreign, obsession",
    "Ketu": "spirituality, detachment, past karma",
}


def _find_sub_lord(degree_in_nak: float, star_lord_idx: int) -> tuple:
    """Find the sub-lord for a position within a nakshatra.

    Returns (sub_lord_name, sub_lord_idx_in_sequence, remaining_degree, sub_start_offset).
    """
    cumulative = 0.0
    for j in range(9):
        sub_idx = (star_lord_idx + j) % 9
        sub_span = NAKSHATRA_SPAN * (KP_YEARS[sub_idx] / TOTAL_YEARS)
        if cumulative + sub_span > degree_in_nak or j == 8:
            remaining = degree_in_nak - cumulative
            return KP_SEQUENCE[sub_idx], sub_idx, remaining, sub_span
        cumulative += sub_span
    # Should not reach here
    return KP_SEQUENCE[star_lord_idx], star_lord_idx, 0.0, NAKSHATRA_SPAN


def _find_sub_sub_lord(degree_in_sub: float, sub_span: float, sub_lord_idx: int) -> str:
    """Find the sub-sub-lord within a sub-lord division."""
    cumulative = 0.0
    for j in range(9):
        ssl_idx = (sub_lord_idx + j) % 9
        ssl_span = sub_span * (KP_YEARS[ssl_idx] / TOTAL_YEARS)
        if cumulative + ssl_span > degree_in_sub or j == 8:
            return KP_SEQUENCE[ssl_idx]
        cumulative += ssl_span
    return KP_SEQUENCE[sub_lord_idx]


def _analyze_point(sidereal_lon: float, tropical_lon: float) -> dict:
    """Full KP analysis for a sidereal longitude: star lord, sub lord, SSL."""
    sid = sidereal_lon % 360

    # Sign
    sign_idx = int(sid / 30) % 12
    sign = SIGNS[sign_idx]
    sign_lord = SIGN_LORDS[sign_idx]

    # Nakshatra
    nak_idx = int(sid / NAKSHATRA_SPAN) % 27
    nakshatra = NAKSHATRAS[nak_idx]
    star_lord = NAKSHATRA_LORDS[nak_idx]
    star_lord_seq_idx = KP_SEQUENCE.index(star_lord)

    # Degree within nakshatra
    deg_in_nak = sid - (nak_idx * NAKSHATRA_SPAN)

    # Sub-lord
    sub_lord, sub_lord_seq_idx, deg_in_sub, sub_span = _find_sub_lord(deg_in_nak, star_lord_seq_idx)

    # Sub-sub-lord
    sub_sub_lord = _find_sub_sub_lord(deg_in_sub, sub_span, sub_lord_seq_idx)

    kp_pointer = f"{star_lord}-{sub_lord}-{sub_sub_lord}"

    return {
        "tropical": round(tropical_lon, 4),
        "sidereal": round(sid, 4),
        "sign": sign,
        "sign_lord": sign_lord,
        "nakshatra": nakshatra,
        "star_lord": star_lord,
        "sub_lord": sub_lord,
        "sub_sub_lord": sub_sub_lord,
        "kp_pointer": kp_pointer,
    }


def _compute_house_cusps_kp(jd: float, lat: float, lon: float, ayanamsa: float) -> dict:
    """Compute KP house cusps (Placidus) and their sub-lords."""
    try:
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')  # Placidus for KP
    except Exception:
        return {}

    house_data = {}
    for i in range(12):
        cusp_trop = cusps[i]
        cusp_sid = (cusp_trop - ayanamsa) % 360

        analysis = _analyze_point(cusp_sid, cusp_trop)
        sign_lord = SIGN_LORDS[int(cusp_sid / 30) % 12]

        house_data[f"house_{i+1}"] = {
            "cuspal_sub_lord": analysis["sub_lord"],
            "cuspal_ssl": analysis["sub_sub_lord"],
            "cusp_sign": analysis["sign"],
            "lord": sign_lord,
            "kp_pointer": analysis["kp_pointer"],
        }

    return house_data


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="kp_sublords",
            name="KP Sub-Lord System (Three-Tier)",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "Requires natal_chart_data"},
            interpretation=None,
            constants_version=constants.get("version", "unknown"),
            references=[],
        )

    jd = natal_chart_data.get("julian_day", 2450349.8)
    swe.set_ephe_path(None)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    planets_data = natal_chart_data.get("planets", {})

    # Points to analyze
    target_planets = ["Sun", "Moon", "Mercury", "Jupiter", "Saturn"]

    points = {}

    # Ascendant
    asc_trop = natal_chart_data.get("ascendant", {}).get("longitude", 0)
    asc_sid = (asc_trop - ayanamsa) % 360
    points["ascendant"] = _analyze_point(asc_sid, asc_trop)

    # Planets
    for pname in target_planets:
        pdata = planets_data.get(pname)
        if pdata:
            trop_lon = pdata.get("longitude", 0)
            sid_lon = (trop_lon - ayanamsa) % 360
            points[pname] = _analyze_point(sid_lon, trop_lon)

    # Extract key sub-lords
    ascendant_sub_lord = points.get("ascendant", {}).get("sub_lord", "unknown")
    moon_sub_lord = points.get("Moon", {}).get("sub_lord", "unknown")
    mercury_sub_lord = points.get("Mercury", {}).get("sub_lord", "unknown")
    jupiter_sub_lord = points.get("Jupiter", {}).get("sub_lord", "unknown")
    saturn_sub_lord = points.get("Saturn", {}).get("sub_lord", "unknown")

    # House significator analysis (requires birth coordinates)
    significator_analysis = {}
    birth_lat = getattr(profile, "latitude", None)
    birth_lon = getattr(profile, "longitude", None)

    if birth_lat is None or birth_lon is None:
        # Try parsing from location
        location = getattr(profile, "location", None)
        if location:
            from modules.natal_chart import _parse_location
            coords = _parse_location(location)
            if coords:
                if len(coords) == 3:
                    birth_lat, birth_lon, _ = coords
                else:
                    birth_lat, birth_lon = coords

    if birth_lat is not None and birth_lon is not None:
        significator_analysis = _compute_house_cusps_kp(jd, birth_lat, birth_lon, ayanamsa)

        # Add occupants to each house (which planets are in which house)
        asc_sid_for_houses = (asc_trop - ayanamsa) % 360
        asc_sign_idx = int(asc_sid_for_houses / 30) % 12
        for pname in target_planets:
            p = points.get(pname)
            if p:
                p_sign_idx = SIGNS.index(p["sign"])
                house_num = ((p_sign_idx - asc_sign_idx) % 12) + 1
                house_key = f"house_{house_num}"
                if house_key in significator_analysis:
                    if "occupants" not in significator_analysis[house_key]:
                        significator_analysis[house_key]["occupants"] = []
                    significator_analysis[house_key]["occupants"].append(pname)

        # Ensure all houses have occupants key
        for i in range(1, 13):
            hk = f"house_{i}"
            if hk in significator_analysis and "occupants" not in significator_analysis[hk]:
                significator_analysis[hk]["occupants"] = []

    # Interpretation
    asc_meaning = PLANET_SIGNIFICATIONS.get(ascendant_sub_lord, "")
    moon_meaning = PLANET_SIGNIFICATIONS.get(moon_sub_lord, "")
    interp = (
        f"KP Ascendant sub-lord {ascendant_sub_lord} indicates focus on {asc_meaning}. "
        f"Moon sub-lord {moon_sub_lord} governs {moon_meaning}. "
        f"Mercury (Atmakaraka) sub-lord: {mercury_sub_lord}. "
        f"Jupiter sub-lord: {jupiter_sub_lord}. Saturn sub-lord: {saturn_sub_lord}. "
        f"Ascendant KP pointer: {points.get('ascendant', {}).get('kp_pointer', '?')}. "
        f"Moon KP pointer: {points.get('Moon', {}).get('kp_pointer', '?')}."
    )

    data = {
        "system": "KP Krishnamurti Paddhati",
        "ayanamsha": round(ayanamsa, 6),
        "points": points,
        "ascendant_sub_lord": ascendant_sub_lord,
        "moon_sub_lord": moon_sub_lord,
        "mercury_sub_lord": mercury_sub_lord,
        "jupiter_sub_lord": jupiter_sub_lord,
        "saturn_sub_lord": saturn_sub_lord,
        "significator_analysis": significator_analysis,
    }

    return SystemResult(
        id="kp_sublords",
        name="KP Sub-Lord System (Three-Tier)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interp,
        constants_version=constants.get("version", "unknown"),
        references=[
            "K.S. Krishnamurti — KP Reader I-VI",
            "Vimshottari dasha proportions for 249 sub-lord table",
            "KP Ayanamsha (Lahiri)",
        ],
    )
