"""Tarot Greer Birth Cards — COMPUTED_STRICT
Mary K. Greer, "Archetypal Tarot" (2021):
  Personality Card: DOB digit sum reduced to 1-22
  Soul Card: Further reduce personality to 1-9 (Fool/22 → 4)
  Constellation: The 3-card family sharing the same root column (e.g., 19→10→1)
  Hidden Factor: The "missing" card in the constellation = Shadow/Teacher Card

NOTE: Personality/Soul computation is identical to existing tarot_birth module.
This module adds Constellation and Hidden Factor (genuinely new).
Convergence fields exclude personality/soul to avoid double-counting with tarot_birth.
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

# Constellation families: each root (1-9) has a column of cards
# Root → [units card, tens card, twenties card]
CONSTELLATIONS = {
    1: [1, 10, 19],
    2: [2, 11, 20],
    3: [3, 12, 21],
    4: [4, 13, 22],  # 22 = Fool
    5: [5, 14],
    6: [6, 15],
    7: [7, 16],
    8: [8, 17],
    9: [9, 18],
}


def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(n))


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    dob = profile.dob
    raw = _digit_sum(dob.month) + _digit_sum(dob.day) + _digit_sum(dob.year)

    total = raw
    while total > 22:
        total = _digit_sum(total)

    personality = total

    # Soul card: reduce to single digit
    if personality == 22:
        soul = 4  # Fool special case
    elif personality > 9:
        soul = _digit_sum(personality)
    else:
        soul = personality

    # Constellation root = soul card value (1-9)
    constellation_root = soul
    constellation_cards = CONSTELLATIONS.get(constellation_root, [])

    # Hidden factor: the card(s) in the constellation NOT held as personality or soul
    held = {personality, soul}
    hidden = [c for c in constellation_cards if c not in held]

    return SystemResult(
        id="tarot_greer_birth_cards",
        name="Tarot Greer Birth Cards (Constellation)",
        certainty="COMPUTED_STRICT",
        data={
            "raw_sum": raw,
            "personality_card": personality,
            "personality_name": MAJOR_ARCANA.get(personality, "Unknown"),
            "soul_card": soul,
            "soul_name": MAJOR_ARCANA.get(soul, "Unknown"),
            "constellation_root": constellation_root,
            "constellation": [
                {"number": c, "name": MAJOR_ARCANA.get(c, "Unknown")}
                for c in constellation_cards
            ],
            "hidden_factor": [
                {"number": c, "name": MAJOR_ARCANA.get(c, "Unknown")}
                for c in hidden
            ],
            "hidden_factor_numbers": hidden,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Mary K. Greer, 'Archetypal Tarot' (2021): Personality, Soul, Constellation, Hidden Factor",
            "SOURCE_TIER:B — Respected secondary source. Greer's systematization of Golden Dawn birth card tradition.",
        ],
        question="Q1_IDENTITY",
    )
