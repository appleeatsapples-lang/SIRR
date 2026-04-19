"""Burmese Mahabote (မဟာဘုတ်) — 7-planet year-cycle + 8-animal weekday system.
Pure arithmetic. No ephemeris. COMPUTED_STRICT.

Source: Cameron & Crowther — MaHaBote: The Little Key (AFA, ~2002)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


REMAINDER_PLANET = {
    0: "Saturn", 1: "Sun", 2: "Moon", 3: "Mars",
    4: "Mercury", 5: "Jupiter", 6: "Venus",
}

FILL_ORDER = ["Sun", "Mercury", "Saturn", "Mars", "Venus", "Moon", "Jupiter"]

# Python weekday(): 0=Mon … 6=Sun
WEEKDAY_PLANET = {
    0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
    4: "Venus", 5: "Saturn", 6: "Sun",
}
WEEKDAY_ANIMAL = {
    0: "Tiger", 1: "Lion", 2: "Tusked Elephant", 3: "Rat",
    4: "Guinea Pig", 5: "Dragon", 6: "Garuda",
}

ANIMAL_ATTRS = {
    "Garuda":            {"direction": "Northeast", "keywords": ["kind", "wise", "public figure"]},
    "Tiger":             {"direction": "East",      "keywords": ["forceful", "intuitive", "spiritual"]},
    "Lion":              {"direction": "Southeast", "keywords": ["brave", "leader", "justice"]},
    "Tusked Elephant":   {"direction": "South",     "keywords": ["adventurer", "quick thinker"]},
    "Tuskless Elephant": {"direction": "Northwest", "keywords": ["calculated", "private"]},
    "Rat":               {"direction": "West",      "keywords": ["survivor", "wealth builder"]},
    "Guinea Pig":        {"direction": "North",     "keywords": ["loving", "creative"]},
    "Dragon":            {"direction": "Southwest", "keywords": ["confident", "charismatic"]},
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    dob = profile.dob
    month_day = (dob.month, dob.day)

    # Step 1 — Adjusted year (Thingyan cutoff Apr 15/16)
    if month_day <= (4, 15):
        adjusted_year = dob.year - 639
    else:
        adjusted_year = dob.year - 638

    # Step 2 — Remainder & house-1 planet
    remainder = adjusted_year % 7
    house1_planet = REMAINDER_PLANET[remainder]

    # Step 3 — 7-house layout
    start_idx = FILL_ORDER.index(house1_planet)
    houses = {}
    for i in range(7):
        houses[str(i + 1)] = FILL_ORDER[(start_idx + i) % 7]

    # Step 4 — Birth weekday animal & planet
    wd = dob.weekday()  # 0=Mon … 6=Sun
    birth_planet = WEEKDAY_PLANET[wd]
    birth_animal = WEEKDAY_ANIMAL[wd]

    # Wednesday PM special case
    wednesday_pm = False
    if wd == 2 and profile.birth_time_local:
        h, _ = map(int, profile.birth_time_local.split(":"))
        if h >= 12:
            wednesday_pm = True
            birth_animal = "Tuskless Elephant"
            birth_planet = "Rahu"

    # Step 5 — Animal attributes
    attrs = ANIMAL_ATTRS[birth_animal]
    direction = attrs["direction"]
    animal_keywords = attrs["keywords"]

    # Find which house the birth planet occupies
    birth_planet_house = None
    for h_num, h_planet in houses.items():
        if h_planet == birth_planet:
            birth_planet_house = int(h_num)
            break

    house_position_note = (
        f"House {birth_planet_house}" if birth_planet_house else "unplaced"
    )
    interpretation = (
        f"Your Mahabote birth animal is the {birth_animal} ({direction} direction), "
        f"carrying the qualities: {', '.join(animal_keywords)}. "
        f"The year lord for Burmese Era {adjusted_year} (remainder {remainder}) is {house1_planet}, "
        f"holding House 1 in your 7-house planetary layout. "
        f"Your birth planet {birth_planet} occupies {house_position_note} in this layout, "
        f"which shapes how the birth animal's energy interfaces with the year's structural tone. "
        f"In Mahabote cosmology, the birth animal governs social orientation and relational style, "
        f"while the year lord colors the background environment of your birth cycle. "
        f"The {birth_animal} pattern favors intuitive responsiveness over linear force "
        f"— the {direction} directional axis orients natural momentum and auspicious timing."
    )

    data = {
        "adjusted_year": adjusted_year,
        "remainder": remainder,
        "house1_planet": house1_planet,
        "birth_planet": birth_planet,
        "birth_animal": birth_animal,
        "houses": houses,
        "direction": direction,
        "animal_keywords": animal_keywords,
        "birth_planet_house": birth_planet_house,
        "wednesday_pm": wednesday_pm,
    }

    return SystemResult(
        id="mahabote",
        name="Burmese Mahabote (မဟာဘုတ်)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interpretation,
        constants_version=constants["version"],
        references=[
            "Cameron, B. & Crowther, S.L. — MaHaBote: The Little Key (AFA, ~2002)",
            "Sage Asita — MaHaBote Teaching Guide (2005, Dirah Foundation)",
            "WOFS — MaHaBote 2023 Edition",
        ],
        question="Q1_IDENTITY",
    )
