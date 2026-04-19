"""
Panchamahabhuta (पञ्चमहाभूत) — Five Great Elements
──────────────────────────────────────────────────────
Maps natal planetary positions to Vedic five-element system:
  Akasha (Ether/Space), Vayu (Air), Agni (Fire), Jala (Water), Prithvi (Earth)

Algorithm:
  1. Get all natal planet positions
  2. Map each planet → Panchamahabhuta element (from vedic_lookups.json / BPHS Ch. 3)
  3. Weight Ascendant lord and Moon lord equally (per Gemini delivery note)
  4. Count element distribution across chart

Source: Brihat Parashara Hora Shastra Ch. 3; Vedic Jyotish tradition
SOURCE_TIER: A (primary Vedic text)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Planet → Panchamahabhuta element (from vedic_lookups.json)
PLANET_ELEMENT = {
    "Jupiter": "Akasha",
    "Saturn": "Vayu",
    "Mars": "Agni",
    "Venus": "Jala",
    "Mercury": "Prithvi",
    "Sun": "Agni",
    "Moon": "Jala",
    "Rahu": "Vayu",
    "Ketu": "Agni",
}

ELEMENT_ENGLISH = {
    "Akasha": "Ether/Space",
    "Vayu": "Air/Wind",
    "Agni": "Fire",
    "Jala": "Water",
    "Prithvi": "Earth",
}

# Sign rulers for ascendant lord determination
SIGN_RULER = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal = kwargs.get("natal_chart_data")
    if not natal or "planets" not in natal:
        return SystemResult(
            id="panchamahabhuta",
            name="Panchamahabhuta (Five Great Elements)",
            certainty="NEEDS_EPHEMERIS",
            data={"dominant_element": None, "reason": "No natal chart data"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["BPHS Ch. 3"],
            question="Q1_IDENTITY",
        )

    planets = natal["planets"]

    # Tally element scores from all planets
    scores = {"Akasha": 0, "Vayu": 0, "Agni": 0, "Jala": 0, "Prithvi": 0}
    planet_elements = {}

    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if name in planets or name.lower() in planets:
            el = PLANET_ELEMENT.get(name)
            if el:
                scores[el] += 1
                planet_elements[name] = el

    # Ascendant lord gets extra weight
    asc_raw = natal.get("ascendant")
    asc = asc_raw.get("longitude") if isinstance(asc_raw, dict) else asc_raw
    if asc is not None:
        asc_sign_idx = int(float(asc) / 30.0) % 12
        asc_lord = SIGN_RULER.get(asc_sign_idx)
        if asc_lord:
            asc_el = PLANET_ELEMENT.get(asc_lord)
            if asc_el:
                scores[asc_el] += 1
                planet_elements["Ascendant_Lord"] = f"{asc_lord} ({asc_el})"

    # Moon lord also gets extra weight
    moon_info = planets.get("Moon")
    if moon_info is not None:
        moon_lon = moon_info if isinstance(moon_info, (int, float)) else moon_info.get("longitude", moon_info.get("lon", 0))
        moon_sign_idx = int(float(moon_lon) / 30.0) % 12
        moon_lord = SIGN_RULER.get(moon_sign_idx)
        if moon_lord:
            moon_el = PLANET_ELEMENT.get(moon_lord)
            if moon_el:
                scores[moon_el] += 1
                planet_elements["Moon_Lord"] = f"{moon_lord} ({moon_el})"

    dominant = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)
    total = sum(scores.values())

    return SystemResult(
        id="panchamahabhuta",
        name="Panchamahabhuta (Five Great Elements)",
        certainty="COMPUTED_STRICT",
        data={
            "scores": scores,
            "dominant_element": dominant,
            "dominant_english": ELEMENT_ENGLISH[dominant],
            "weakest_element": weakest,
            "weakest_english": ELEMENT_ENGLISH[weakest],
            "planet_elements": planet_elements,
            "total_votes": total,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Brihat Parashara Hora Shastra Ch. 3", "vedic_lookups.json"],
        question="Q1_IDENTITY",
    )
