"""Tibetan Elements (Lo Element + Srog Vitality) — COMPUTED_STRICT
lo_element: Birth year mod 10 → 5 elements × male/female polarity = 10-year cycle
srog_vitality: Birth year mod 12 → life force element from fixed table
Source: Tibetan Byung-rTsis / Nagtsi texts
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Lo (Natal Element): based on last digit of birth year
# Each element rules 2 consecutive years (male/female polarity)
# Digit 0,1 = Iron; 2,3 = Water; 4,5 = Wood; 6,7 = Fire; 8,9 = Earth
LO_ELEMENT = {
    0: ("Iron", "Male"),    1: ("Iron", "Female"),
    2: ("Water", "Male"),   3: ("Water", "Female"),
    4: ("Wood", "Male"),    5: ("Wood", "Female"),
    6: ("Fire", "Male"),    7: ("Fire", "Female"),
    8: ("Earth", "Male"),   9: ("Earth", "Female"),
}

# Srog (Life Force/Vitality Element): based on year in 12-year animal cycle
# Mouse=Water, Ox=Earth, Tiger=Wood, Hare=Wood, Dragon=Earth, Snake=Fire,
# Horse=Fire, Sheep=Earth, Monkey=Iron, Bird=Iron, Dog=Earth, Pig=Water
SROG_ELEMENT = [
    "Water",  # Mouse/Rat (0)
    "Earth",  # Ox (1)
    "Wood",   # Tiger (2)
    "Wood",   # Hare/Rabbit (3)
    "Earth",  # Dragon (4)
    "Fire",   # Snake (5)
    "Fire",   # Horse (6)
    "Earth",  # Sheep/Goat (7)
    "Iron",   # Monkey (8)
    "Iron",   # Bird/Rooster (9)
    "Earth",  # Dog (10)
    "Water",  # Pig (11)
]

ANIMALS = [
    "Mouse", "Ox", "Tiger", "Hare", "Dragon", "Snake",
    "Horse", "Sheep", "Monkey", "Bird", "Dog", "Pig",
]


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    year = profile.dob.year

    # Lo Element: last digit of birth year
    last_digit = year % 10
    lo_el, lo_pol = LO_ELEMENT[last_digit]

    # Srog Element: year in 12-animal cycle
    # Chinese/Tibetan base: 1924 = Mouse year
    animal_idx = (year - 1924) % 12
    srog_el = SROG_ELEMENT[animal_idx]
    animal = ANIMALS[animal_idx]

    return SystemResult(
        id="tibetan_elements",
        name="Tibetan Elements (Lo + Srog)",
        certainty="COMPUTED_STRICT",
        data={
            "birth_year": year,
            "lo_element": lo_el,
            "lo_polarity": lo_pol,
            "lo_last_digit": last_digit,
            "srog_element": srog_el,
            "srog_animal": animal,
            "srog_animal_index": animal_idx,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Tibetan Byung-rTsis: Lo element from last digit of year, Srog from 12-animal cycle",
            "SOURCE_TIER:B — Traditional Tibetan astrological text.",
        ],
        question="Q1_IDENTITY",
    )
