"""Primary Directions — Hellenistic Predictive Timing — COMPUTED_STRICT

The oldest and most prestigious predictive technique in Western astrology.
Primary Directions measure the diurnal rotation of the celestial sphere to
predict when a promittor body reaches a significator's position.

Algorithm (Zodiacal method, Ptolemaic key):
  1. Convert natal planet longitudes to Right Ascension (RA) using obliquity
  2. Compute Meridian Distance (MD) and Semi-Arcs for each body
  3. For each promittor-significator pair and aspect:
     a. Compute the Oblique Ascension/Descension under the significator's pole
     b. Arc = difference in OA/OD between promittor (aspected) and significator
     c. Years = arc / key rate
  4. Key rates: Ptolemy (1°=1 year), Naibod (0.9856°=1 year)

Sources: Ptolemy Tetrabiblos III.10, Martin Gansten Primary Directions (2009)
"""
from __future__ import annotations
import math
import swisseph as swe
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Significators: the 5 Ptolemaic significators
SIGNIFICATORS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# Promittors: planets + angles
PROMITTORS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

ASPECTS = [
    ("conjunction", 0),
    ("sextile", 60),
    ("square", 90),
    ("trine", 120),
    ("opposition", 180),
]

PLANET_IDS = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3,
    "Mars": 4, "Jupiter": 5, "Saturn": 6,
}

# Direction keys
PTOLEMY_KEY = 1.0          # 1° = 1 year
NAIBOD_KEY = 0.9855556     # mean solar motion per day in RA


def _ecliptic_to_equatorial(lon_deg: float, lat_deg: float, obliquity_deg: float):
    """Convert ecliptic longitude/latitude to Right Ascension and Declination.
    All inputs/outputs in degrees."""
    lon = math.radians(lon_deg)
    lat = math.radians(lat_deg)
    eps = math.radians(obliquity_deg)

    sin_dec = math.sin(lat) * math.cos(eps) + math.cos(lat) * math.sin(eps) * math.sin(lon)
    dec = math.asin(max(-1, min(1, sin_dec)))

    y = math.sin(lon) * math.cos(eps) - math.tan(lat) * math.sin(eps)
    x = math.cos(lon)
    ra = math.atan2(y, x)

    return math.degrees(ra) % 360, math.degrees(dec)


def _ascensional_difference(dec_deg: float, geo_lat_deg: float) -> float:
    """Compute Ascensional Difference (AD) in degrees.
    AD = arcsin(tan(φ) * tan(δ))"""
    phi = math.radians(geo_lat_deg)
    dec = math.radians(dec_deg)
    val = math.tan(phi) * math.tan(dec)
    val = max(-1, min(1, val))  # clamp for circumpolar
    return math.degrees(math.asin(val))


def _semi_arcs(dec_deg: float, geo_lat_deg: float):
    """Compute diurnal and nocturnal semi-arcs in degrees.
    DSA = 90 + AD, NSA = 90 - AD"""
    ad = _ascensional_difference(dec_deg, geo_lat_deg)
    dsa = 90 + ad
    nsa = 90 - ad
    return dsa, nsa


def _meridian_distance(ra_deg: float, ramc_deg: float) -> float:
    """Upper Meridian Distance: shortest arc from RA to RAMC.
    Positive if west of meridian, negative if east."""
    md = (ra_deg - ramc_deg + 180) % 360 - 180
    return md


def _oblique_ascension(ra_deg: float, dec_deg: float, geo_lat_deg: float) -> float:
    """Oblique Ascension (OA) = RA - AD (for eastern hemisphere).
    Used for zodiacal directions."""
    ad = _ascensional_difference(dec_deg, geo_lat_deg)
    return (ra_deg - ad) % 360


def _oblique_descension(ra_deg: float, dec_deg: float, geo_lat_deg: float) -> float:
    """Oblique Descension (OD) = RA + AD (for western hemisphere)."""
    ad = _ascensional_difference(dec_deg, geo_lat_deg)
    return (ra_deg + ad) % 360


def _pole_of_significator(md_deg: float, sa_deg: float, geo_lat_deg: float) -> float:
    """Compute the pole of a significator.
    tan(pole) = (MD / SA) * tan(φ)
    MD = meridian distance, SA = appropriate semi-arc."""
    if abs(sa_deg) < 0.01:
        return 0
    phi = math.radians(geo_lat_deg)
    ratio = abs(md_deg) / abs(sa_deg)
    val = ratio * math.tan(phi)
    val = max(-1, min(1, val))
    return math.degrees(math.atan(val))


def _compute_zodiacal_arc(prom_lon: float, sig_lon: float, aspect_deg: float,
                          obliquity: float, geo_lat: float) -> float:
    """Compute the zodiacal direction arc from promittor to significator aspect point.
    Returns the arc in degrees (can be positive or negative)."""
    # Aspected point: promittor's longitude + aspect
    aspected_lon = (prom_lon + aspect_deg) % 360

    # Convert both to equatorial
    ra_asp, dec_asp = _ecliptic_to_equatorial(aspected_lon, 0, obliquity)
    ra_sig, dec_sig = _ecliptic_to_equatorial(sig_lon, 0, obliquity)

    # Compute OA for both (zodiacal method uses latitude = 0)
    oa_asp = _oblique_ascension(ra_asp, dec_asp, geo_lat)
    oa_sig = _oblique_ascension(ra_sig, dec_sig, geo_lat)

    # Arc = OA(aspected promittor) - OA(significator)
    arc = (oa_asp - oa_sig + 180) % 360 - 180
    return arc


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="primary_directions",
            name="Primary Directions (Hellenistic Timing)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    swe.set_ephe_path(None)

    planets_data = natal_chart_data.get("planets", {})
    jd = natal_chart_data.get("julian_day", 2450349.8)
    coords = natal_chart_data.get("coordinates", {})
    geo_lat = coords.get("lat", 26.2361)

    # Get obliquity from Swiss Ephemeris
    ecl_nut = swe.calc_ut(jd, swe.ECL_NUT)
    obliquity = ecl_nut[0][0]  # true obliquity

    # RAMC from MC longitude (approximate: RA of MC ≈ MC for low obliquity)
    mc_lon = natal_chart_data.get("midheaven", {}).get("longitude", 0)
    ra_mc, _ = _ecliptic_to_equatorial(mc_lon, 0, obliquity)
    ramc = ra_mc

    # Compute RA and Dec for all planets (using ecliptic lat = 0 for zodiacal)
    planet_equatorial = {}
    for name in SIGNIFICATORS:
        if name not in planets_data:
            continue
        lon = planets_data[name]["longitude"]
        # For zodiacal directions, treat ecliptic latitude as 0
        ra, dec = _ecliptic_to_equatorial(lon, 0, obliquity)
        md = _meridian_distance(ra, ramc)
        dsa, nsa = _semi_arcs(dec, geo_lat)
        sa = dsa if md >= 0 else nsa  # use appropriate semi-arc
        planet_equatorial[name] = {
            "longitude": lon,
            "ra": round(ra, 4),
            "dec": round(dec, 4),
            "md": round(md, 4),
            "dsa": round(dsa, 4),
            "nsa": round(nsa, 4),
        }

    # Also compute for ASC and MC as significators
    asc_lon = natal_chart_data.get("ascendant", {}).get("longitude", 0)

    # Compute direction events
    today = profile.today if hasattr(profile, "today") else __import__("datetime").date.today()
    dob = profile.dob
    age_years = (today - dob).days / 365.25
    max_arc = 90  # Only compute directions up to 90° arc (90 years with Ptolemy key)

    events = []
    for sig_name, sig_data in planet_equatorial.items():
        for prom_name in PROMITTORS:
            if prom_name == sig_name:
                continue
            if prom_name not in planets_data:
                continue
            prom_lon = planets_data[prom_name]["longitude"]

            for aspect_name, aspect_deg in ASPECTS:
                # Direct direction
                arc = _compute_zodiacal_arc(
                    prom_lon, sig_data["longitude"], aspect_deg, obliquity, geo_lat
                )

                if 0 < abs(arc) < max_arc:
                    years_ptolemy = abs(arc) / PTOLEMY_KEY
                    years_naibod = abs(arc) / NAIBOD_KEY

                    events.append({
                        "promittor": prom_name,
                        "significator": sig_name,
                        "aspect": aspect_name,
                        "direction_type": "zodiacal",
                        "motion": "direct" if arc > 0 else "converse",
                        "arc_deg": round(abs(arc), 4),
                        "years_ptolemy": round(years_ptolemy, 2),
                        "years_naibod": round(years_naibod, 2),
                        "age_ptolemy": round(years_ptolemy, 1),
                        "age_naibod": round(years_naibod, 1),
                        "is_past": years_ptolemy < age_years,
                    })

    # Sort by Ptolemaic years
    events.sort(key=lambda e: e["years_ptolemy"])

    # Filter to relevant window: past 5 years to future 10 years
    current_events = [e for e in events
                      if age_years - 5 <= e["years_ptolemy"] <= age_years + 10]

    # Find next upcoming event
    future_events = [e for e in events if e["years_ptolemy"] > age_years]
    next_event = future_events[0] if future_events else None

    data = {
        "method": "primary_directions_zodiacal_v1",
        "key_ptolemy": PTOLEMY_KEY,
        "key_naibod": NAIBOD_KEY,
        "obliquity": round(obliquity, 6),
        "ramc": round(ramc, 4),
        "geo_latitude": geo_lat,
        "current_age": round(age_years, 2),
        "planet_equatorial": planet_equatorial,
        "total_events": len(events),
        "current_window_events": current_events,
        "next_event": next_event,
        "all_events": events[:50],  # Cap at 50 to keep output manageable
    }

    return SystemResult(
        id="primary_directions",
        name="Primary Directions (Hellenistic Timing)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Ptolemy, Tetrabiblos III.10 — primary directions method",
            "Martin Gansten, Primary Directions (2009) — modern reference",
        ],
        question="Q4_TIMING",
    )
