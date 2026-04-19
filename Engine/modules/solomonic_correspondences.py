"""
Solomonic Correspondences (מפתח שלמה)
────────────────────────────────────────
Maps planetary rulers from the natal chart to the Solomonic magical
tradition: angels, intelligences, spirits, metals, colors, kamea constants.

Class C / META — derives from natal chart planetary data.

Algorithm:
  1. Identify dominant planet (chart ruler = Ascendant lord)
  2. Identify secondary planet (Moon sign lord)
  3. Look up Solomonic correspondence table for each planet
  4. Map Day of Birth → ruling planet → Solomonic angel

Source: Clavicula Salomonis (Key of Solomon); Agrippa: Three Books of Occult Philosophy
SOURCE_TIER: B (respected secondary — Western esoteric tradition)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


SOLOMONIC_TABLE = {
    "Saturn": {
        "angel": "Cassiel", "intelligence": "Agiel", "spirit": "Zazel",
        "metal": "Lead", "day": "Saturday", "color": "Black",
        "kamea_order": 3, "magic_square_constant": 15, "stone": "Onyx",
    },
    "Jupiter": {
        "angel": "Sachiel", "intelligence": "Iophiel", "spirit": "Hismael",
        "metal": "Tin", "day": "Thursday", "color": "Blue",
        "kamea_order": 4, "magic_square_constant": 34,
    },
    "Mars": {
        "angel": "Samael", "intelligence": "Graphiel", "spirit": "Bartzabel",
        "metal": "Iron", "day": "Tuesday", "color": "Red",
        "kamea_order": 5, "magic_square_constant": 65,
    },
    "Sun": {
        "angel": "Michael", "intelligence": "Nakhiel", "spirit": "Sorath",
        "metal": "Gold", "day": "Sunday", "color": "Yellow/Gold",
        "kamea_order": 6, "magic_square_constant": 111,
    },
    "Venus": {
        "angel": "Anael", "intelligence": "Hagiel", "spirit": "Kedemel",
        "metal": "Copper", "day": "Friday", "color": "Green",
        "kamea_order": 7, "magic_square_constant": 175,
    },
    "Mercury": {
        "angel": "Raphael", "intelligence": "Tiriel", "spirit": "Taphthartharath",
        "metal": "Mercury (quicksilver)", "day": "Wednesday", "color": "Orange",
        "kamea_order": 8, "magic_square_constant": 260,
    },
    "Moon": {
        "angel": "Gabriel", "intelligence": "Malkah be-Tarshishim", "spirit": "Chasmodai",
        "metal": "Silver", "day": "Monday", "color": "Silver/White",
        "kamea_order": 9, "magic_square_constant": 369,
    },
}

SIGN_RULER = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

WEEKDAY_PLANET = {
    0: "Moon",      # Monday
    1: "Mars",      # Tuesday
    2: "Mercury",   # Wednesday
    3: "Jupiter",   # Thursday
    4: "Venus",     # Friday
    5: "Saturn",    # Saturday
    6: "Sun",       # Sunday
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal = kwargs.get("natal_chart_data")

    # Birth weekday planet
    weekday = profile.dob.weekday()  # 0=Monday
    birth_planet = WEEKDAY_PLANET.get(weekday)
    birth_correspondence = SOLOMONIC_TABLE.get(birth_planet, {})

    # Chart ruler (Ascendant lord)
    chart_ruler = None
    chart_correspondence = {}
    if natal and natal.get("ascendant") is not None:
        asc_raw = natal["ascendant"]
        asc_val = asc_raw.get("longitude") if isinstance(asc_raw, dict) else asc_raw
        asc_sign = int(float(asc_val) / 30.0) % 12
        chart_ruler = SIGN_RULER.get(asc_sign)
        chart_correspondence = SOLOMONIC_TABLE.get(chart_ruler, {})

    # Moon lord
    moon_lord = None
    moon_correspondence = {}
    if natal and "planets" in natal:
        moon_info = natal["planets"].get("Moon")
        if moon_info is not None:
            moon_lon = moon_info if isinstance(moon_info, (int, float)) else moon_info.get("longitude", moon_info.get("lon", 0))
            moon_sign = int(float(moon_lon) / 30.0) % 12
            moon_lord = SIGN_RULER.get(moon_sign)
            moon_correspondence = SOLOMONIC_TABLE.get(moon_lord, {})

    # Collect all unique planets involved
    active_planets = set(filter(None, [birth_planet, chart_ruler, moon_lord]))
    active_correspondences = {}
    for p in active_planets:
        active_correspondences[p] = SOLOMONIC_TABLE.get(p, {})

    # Dominant angel (from chart ruler, fallback to birth planet)
    dominant_planet = chart_ruler or birth_planet
    dominant = SOLOMONIC_TABLE.get(dominant_planet, {})

    certainty = "META" if natal else "META"

    return SystemResult(
        id="solomonic_correspondences",
        name="Solomonic Correspondences",
        certainty=certainty,
        data={
            "birth_day_planet": birth_planet,
            "birth_day_angel": birth_correspondence.get("angel"),
            "birth_day_intelligence": birth_correspondence.get("intelligence"),
            "birth_day_spirit": birth_correspondence.get("spirit"),
            "chart_ruler": chart_ruler,
            "chart_ruler_angel": chart_correspondence.get("angel"),
            "chart_ruler_metal": chart_correspondence.get("metal"),
            "chart_ruler_color": chart_correspondence.get("color"),
            "moon_lord": moon_lord,
            "moon_lord_angel": moon_correspondence.get("angel"),
            "dominant_planet": dominant_planet,
            "dominant_angel": dominant.get("angel"),
            "dominant_kamea_constant": dominant.get("magic_square_constant"),
            "active_correspondences": active_correspondences,
            "module_class": "meta",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Clavicula Salomonis", "Agrippa: Three Books of Occult Philosophy",
                     "kabbalah_solomonic_lookups.json"],
        question="Q2_MEANING",
    )
