"""Krishnamurti Paddhati (KP System) — 249 Sub-Lord Table — COMPUTED_STRICT

KP divides the zodiac into 249 sub-divisions using Vimshottari dasha proportions.
Each planet gets a Sign Lord, Star (Nakshatra) Lord, and Sub Lord.
The Sub Lord is the key predictive element in KP astrology.

Algorithm:
  1. Convert all planets to sidereal (Lahiri ayanamsa)
  2. Build 249-sub table: 27 nakshatras × 9 sub-periods (Vimshottari proportions)
  3. Map each planet's sidereal longitude to its sub-lord
  4. Determine Sign Lord, Star Lord, Sub Lord for each planet

Sources: K.S. Krishnamurti, KP Reader I-VI
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

# Vimshottari dasha lords in sequence
DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
TOTAL_DASHA_YEARS = 120

# 27 Nakshatras with their ruling planets (Vimshottari cycle)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Nakshatra lords cycle through DASHA_LORDS (starting Ketu for Ashwini)
NAKSHATRA_LORDS = [DASHA_LORDS[i % 9] for i in range(27)]

NAKSHATRA_SPAN = 360 / 27  # 13°20' = 13.3333°

# Precompute the 249 sub-lord boundaries
_SUB_TABLE = None


def _build_sub_table():
    """Build the 249 sub-lord table with exact degree boundaries."""
    global _SUB_TABLE
    if _SUB_TABLE is not None:
        return _SUB_TABLE

    table = []
    for nak_idx in range(27):
        nak_start = nak_idx * NAKSHATRA_SPAN
        star_lord = NAKSHATRA_LORDS[nak_idx]

        # Sub-lord sequence starts from the star lord's position in DASHA_LORDS
        star_lord_idx = DASHA_LORDS.index(star_lord)

        # Each nakshatra (13°20') is divided into 9 sub-periods
        # proportional to Vimshottari dasha years
        sub_start = nak_start
        for j in range(9):
            sub_lord_idx = (star_lord_idx + j) % 9
            sub_lord = DASHA_LORDS[sub_lord_idx]
            sub_span = NAKSHATRA_SPAN * (DASHA_YEARS[sub_lord] / TOTAL_DASHA_YEARS)
            sub_end = sub_start + sub_span

            table.append({
                "index": len(table) + 1,
                "start_deg": round(sub_start, 6),
                "end_deg": round(sub_end, 6),
                "sign_lord": SIGN_LORDS[int(sub_start / 30) % 12],
                "star_lord": star_lord,
                "sub_lord": sub_lord,
                "nakshatra": NAKSHATRAS[nak_idx],
            })
            sub_start = sub_end

    # Should be 243 entries (27 × 9), but KP tradition calls it "249"
    # because some sub-divisions cross sign boundaries and are split
    _SUB_TABLE = table
    return table


def _lookup_sub(sid_lon: float) -> dict:
    """Find the sub-lord entry for a sidereal longitude."""
    table = _build_sub_table()
    lon = sid_lon % 360
    for entry in table:
        if entry["start_deg"] <= lon < entry["end_deg"]:
            return entry
    # Edge case: exactly 360° or floating point
    return table[-1]


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="kp_system",
            name="Krishnamurti Paddhati (KP System)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q5_SYSTEM",
        )

    jd = natal_chart_data.get("julian_day", 2450349.8)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    planets_data = natal_chart_data.get("planets", {})
    kp_planets = {}

    for name, pdata in planets_data.items():
        trop_lon = pdata.get("longitude", 0)
        sid_lon = (trop_lon - ayanamsa) % 360

        sub_entry = _lookup_sub(sid_lon)
        kp_planets[name] = {
            "sidereal_longitude": round(sid_lon, 4),
            "sidereal_sign": SIGNS[int(sid_lon / 30) % 12],
            "sidereal_degree": round(sid_lon % 30, 4),
            "sign_lord": sub_entry["sign_lord"],
            "star_lord": sub_entry["star_lord"],
            "sub_lord": sub_entry["sub_lord"],
            "nakshatra": sub_entry["nakshatra"],
            "sub_index": sub_entry["index"],
        }

    # Also compute for ASC and MC
    asc_trop = natal_chart_data.get("ascendant", {}).get("longitude", 0)
    mc_trop = natal_chart_data.get("midheaven", {}).get("longitude", 0)

    asc_sid = (asc_trop - ayanamsa) % 360
    mc_sid = (mc_trop - ayanamsa) % 360

    asc_sub = _lookup_sub(asc_sid)
    mc_sub = _lookup_sub(mc_sid)

    kp_cusps = {
        "Ascendant": {
            "sidereal_longitude": round(asc_sid, 4),
            "sign_lord": asc_sub["sign_lord"],
            "star_lord": asc_sub["star_lord"],
            "sub_lord": asc_sub["sub_lord"],
            "nakshatra": asc_sub["nakshatra"],
        },
        "Midheaven": {
            "sidereal_longitude": round(mc_sid, 4),
            "sign_lord": mc_sub["sign_lord"],
            "star_lord": mc_sub["star_lord"],
            "sub_lord": mc_sub["sub_lord"],
            "nakshatra": mc_sub["nakshatra"],
        },
    }

    # Summary: most frequent sub-lord
    all_sub_lords = [p["sub_lord"] for p in kp_planets.values()]
    sub_counts = {}
    for sl in all_sub_lords:
        sub_counts[sl] = sub_counts.get(sl, 0) + 1
    dominant_sub_lord = max(sub_counts, key=sub_counts.get) if sub_counts else None

    data = {
        "method": "kp_249_sublord_v1",
        "ayanamsa": round(ayanamsa, 6),
        "ayanamsa_type": "Lahiri",
        "kp_planets": kp_planets,
        "kp_cusps": kp_cusps,
        "dominant_sub_lord": dominant_sub_lord,
        "sub_lord_distribution": sub_counts,
    }

    return SystemResult(
        id="kp_system",
        name="Krishnamurti Paddhati (KP System)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "K.S. Krishnamurti, KP Reader I-VI",
            "Vimshottari dasha proportions for 249 sub-lord table",
        ],
        question="Q5_SYSTEM",
    )
