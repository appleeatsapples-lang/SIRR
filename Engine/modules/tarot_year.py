"""Tarot Year Card — COMPUTED_STRICT
The Tarot Year Card reveals the archetypal theme of the current year.
Calculation: birth month + birth day + current year, reduced to 1-22.
Source: Angeles Arrien, Mary K. Greer
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

MAJOR_ARCANA = {
    0: "The Fool", 1: "The Magician", 2: "The High Priestess",
    3: "The Empress", 4: "The Emperor", 5: "The Hierophant",
    6: "The Lovers", 7: "The Chariot", 8: "Strength",
    9: "The Hermit", 10: "Wheel of Fortune", 11: "Justice",
    12: "The Hanged Man", 13: "Death", 14: "Temperance",
    15: "The Devil", 16: "The Tower", 17: "The Star",
    18: "The Moon", 19: "The Sun", 20: "Judgement",
    21: "The World", 22: "The Fool (0/22)",
}

def _reduce_tarot(n: int) -> int:
    """Reduce to 1-22 range per Greer method."""
    while n > 22:
        n = sum(int(d) for d in str(n))
    return n

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    m, d, y = profile.dob.month, profile.dob.day, profile.today.year
    raw = m + d + sum(int(ch) for ch in str(y))
    card_num = _reduce_tarot(raw)
    card_name = MAJOR_ARCANA.get(card_num, f"Arcanum {card_num}")

    return SystemResult(
        id="tarot_year",
        name="Tarot Year Card",
        certainty="COMPUTED_STRICT",
        data={
            "year": y,
            "raw_sum": raw,
            "card_number": card_num,
            "card_name": card_name,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Greer: month + day + current year digits, reduced to 1-22"],
        question="Q3_TIMING"
    )
