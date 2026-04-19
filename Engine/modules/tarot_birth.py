"""Tarot Birth Cards — COMPUTED_STRICT
Mary K. Greer method:
1. S = sum of all digits of YYYY + MM + DD
2. Reduce to 1-22 (sum digits while > 22)
3. Personality card = result
4. Soul card = sum digits of personality, reduce to 1-9
5. If personality = 19, chain: 19 → 10 → 1 (three cards)
6. Fool = 22 (not 0) for reduction purposes
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

MAJOR_ARCANA = {
    1: "The Magician", 2: "The High Priestess", 3: "The Empress",
    4: "The Emperor", 5: "The Hierophant", 6: "The Lovers",
    7: "The Chariot", 8: "Strength", 9: "The Hermit",
    10: "Wheel of Fortune", 11: "Justice", 12: "The Hanged Man",
    13: "Death", 14: "Temperance", 15: "The Devil",
    16: "The Tower", 17: "The Star", 18: "The Moon",
    19: "The Sun", 20: "Judgement", 21: "The World",
    22: "The Fool",
}


def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(n))


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    dob = profile.dob
    raw = _digit_sum(dob.month) + _digit_sum(dob.day) + _digit_sum(dob.year)

    # Reduce to 1-22 range (Fool = 22, not 0)
    total = raw
    while total > 22:
        total = _digit_sum(total)

    primary = total  # Personality card

    # Soul card: sum digits of personality, reduce to 1-9
    if primary > 9:
        secondary = _digit_sum(primary)
    else:
        secondary = None

    # Special case: 22 (The Fool) → soul card = 2+2 = 4 (The Emperor)
    if primary == 22:
        secondary = 4

    # Special case: 19 (The Sun) → 10 → 1 (three-card chain)
    tertiary = None
    if primary == 19:
        # secondary is already 10, add tertiary = 1
        tertiary = 1

    data = {
        "raw_sum": raw,
        "primary_card_number": primary,
        "primary_card_name": MAJOR_ARCANA.get(primary, "Unknown"),
    }
    if secondary:
        data["secondary_card_number"] = secondary
        data["secondary_card_name"] = MAJOR_ARCANA.get(secondary, "Unknown")

    if tertiary:
        data["tertiary_card_number"] = tertiary
        data["tertiary_card_name"] = MAJOR_ARCANA.get(tertiary, "Unknown")
        data["pair"] = f"{MAJOR_ARCANA[primary]} / {MAJOR_ARCANA[secondary]} / {MAJOR_ARCANA[tertiary]}"
    elif secondary:
        data["pair"] = f"{MAJOR_ARCANA[primary]} / {MAJOR_ARCANA[secondary]}"
    else:
        data["pair"] = MAJOR_ARCANA.get(primary, "Unknown")

    return SystemResult(
        id="tarot_birth",
        name="Tarot Birth Cards",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=["Mary K. Greer's method. DOB digit sum → Major Arcana pair."],
        question="Q1_IDENTITY"
    )
