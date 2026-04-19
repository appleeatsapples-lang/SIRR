"""Arabic Parts / Lots — COMPUTED_STRICT
Computes the 7 Hermetic Lots from Hellenistic tradition, each associated
with one of the 7 traditional planets.

All lots follow the formula:
  Day chart:   Lot = ASC + Planet_A − Planet_B
  Night chart: Lot = ASC + Planet_B − Planet_A
Result is normalized to 0°–360°.

The 7 Hermetic Lots (Vettius Valens, Anthology):
  Fortune (Moon)   — material well-being, body, health
  Spirit (Sun)     — mind, will, career, purpose
  Eros (Venus)     — love, desire, attraction
  Necessity (Mercury) — constraint, restriction, fate
  Courage (Mars)   — boldness, action, danger
  Victory (Jupiter) — success, honor, achievement
  Nemesis (Saturn)  — downfall, enemies, accountability

Sources: Vettius Valens (Anthology), Paulus Alexandrinus, Al-Biruni
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# The 7 Hermetic Lots: (name, planet_a_day, planet_b_day)
# Day:   LOT = ASC + A - B
# Night: LOT = ASC + B - A
LOTS = [
    ("Fortune",   "Moon",    "Sun"),
    ("Spirit",    "Sun",     "Moon"),
    ("Eros",      "Venus",   "Spirit"),    # Spirit here = Lot of Spirit longitude
    ("Necessity", "Fortune", "Mercury"),   # Fortune here = Lot of Fortune longitude
    ("Courage",   "Fortune", "Mars"),
    ("Victory",   "Jupiter", "Spirit"),
    ("Nemesis",   "Fortune", "Saturn"),
]


def _lot_position(asc: float, a: float, b: float, is_diurnal: bool) -> float:
    """Compute lot longitude. Day: ASC+A-B, Night: ASC+B-A."""
    if is_diurnal:
        lon = asc + a - b
    else:
        lon = asc + b - a
    return lon % 360


def _sign_data(longitude: float) -> dict:
    """Return sign, degree, minute for a longitude."""
    sign_idx = int(longitude // 30) % 12
    deg_in_sign = longitude % 30
    degree = int(deg_in_sign)
    minute = int((deg_in_sign - degree) * 60)
    return {
        "longitude": round(longitude, 4),
        "sign": SIGNS[sign_idx],
        "degree": degree,
        "minute": minute,
        "formatted": f"{degree}\u00b0{minute:02d}' {SIGNS[sign_idx]}",
    }


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="arabic_parts",
            name="Arabic Parts (Hermetic Lots)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    planets = natal_chart_data.get("planets", {})
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    sun_lon = planets["Sun"]["longitude"]

    # Determine sect
    desc_lon = (asc_lon + 180) % 360
    is_diurnal = ((sun_lon - desc_lon) % 360) < 180

    # First pass: compute Fortune and Spirit (needed by other lots)
    fortune_lon = _lot_position(asc_lon, planets["Moon"]["longitude"], sun_lon, is_diurnal)
    spirit_lon = _lot_position(asc_lon, sun_lon, planets["Moon"]["longitude"], is_diurnal)

    # Lookup table for lot computation (maps names to longitudes)
    source_lons = {
        "Sun": sun_lon,
        "Moon": planets["Moon"]["longitude"],
        "Mercury": planets["Mercury"]["longitude"],
        "Venus": planets["Venus"]["longitude"],
        "Mars": planets["Mars"]["longitude"],
        "Jupiter": planets["Jupiter"]["longitude"],
        "Saturn": planets["Saturn"]["longitude"],
        "Fortune": fortune_lon,
        "Spirit": spirit_lon,
    }

    lots = {}
    lot_signs = []

    for name, a_key, b_key in LOTS:
        a_lon = source_lons[a_key]
        b_lon = source_lons[b_key]
        lot_lon = _lot_position(asc_lon, a_lon, b_lon, is_diurnal)
        lot_data = _sign_data(lot_lon)
        lots[name] = lot_data
        lot_signs.append(lot_data["sign"])

    # Fortune and Spirit houses (in Whole Sign from ASC)
    asc_sign_idx = int(asc_lon // 30) % 12
    fortune_sign_idx = int(fortune_lon // 30) % 12
    spirit_sign_idx = int(spirit_lon // 30) % 12
    fortune_house = (fortune_sign_idx - asc_sign_idx) % 12 + 1
    spirit_house = (spirit_sign_idx - asc_sign_idx) % 12 + 1

    data = {
        "is_diurnal": is_diurnal,
        "lots": lots,
        "fortune_house": fortune_house,
        "spirit_house": spirit_house,
        "lot_count": len(lots),
    }

    return SystemResult(
        id="arabic_parts",
        name="Arabic Parts (Hermetic Lots)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Vettius Valens, Anthology — 7 Hermetic Lots",
            "Paulus Alexandrinus — lot formulas with sect reversal",
            "Al-Biruni — Arabic Parts tradition",
        ],
        question="Q1_IDENTITY",
    )
