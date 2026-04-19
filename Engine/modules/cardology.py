"""Cardology Birth Card — COMPUTED_STRICT (Magi formula)"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SUITS = ["Hearts", "Clubs", "Diamonds", "Spades"]
RANKS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
RANK_MEANINGS = {
    "Ace": "New beginnings, individuality, desire for knowledge",
    "2": "Cooperation, partnership, duality",
    "3": "Creative expression, communication, imagination",
    "4": "Stability, foundation, structure",
    "5": "Adventure, change, restlessness",
    "6": "Responsibility, karma, balance",
    "7": "Spiritual knowledge, faith, reflection",
    "8": "Power, mastery, vision",
    "9": "Completion, universal giving, endings",
    "10": "Career, independence, accomplishment",
    "Jack": "Creative youth, mental brilliance, immaturity risk",
    "Queen": "Nurturing authority, intuition, service",
    "King": "Mastery, leadership, executive power",
}
SUIT_MEANINGS = {
    "Hearts": "Love, relationships, emotions",
    "Clubs": "Knowledge, communication, mental pursuits",
    "Diamonds": "Values, money, material world",
    "Spades": "Wisdom, health, work, spirituality",
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    # Magi Formula: Solar Value = 55 - ((Month * 2) + Day)
    # Card order: A♥=1..K♥=13, A♣=14..K♣=26, A♦=27..K♦=39, A♠=40..K♠=52
    # Dec 31 (sv=0) = Joker
    m, d = profile.dob.month, profile.dob.day
    sv = 55 - ((m * 2) + d)

    if sv <= 0:
        card_name = "Joker"
        suit = "Special"
        rank = "Joker"
    else:
        suit_idx = (sv - 1) // 13
        rank_idx = (sv - 1) % 13
        rank = RANKS[rank_idx]
        suit = SUITS[suit_idx]
        card_name = f"{rank} of {suit}"

    return SystemResult(
        id="cardology",
        name="Cardology Birth Card",
        certainty="COMPUTED_STRICT",
        data={
            "birth_card": card_name,
            "solar_value": sv,
            "rank": rank,
            "suit": suit,
            "rank_meaning": RANK_MEANINGS.get(rank, ""),
            "suit_meaning": SUIT_MEANINGS.get(suit, ""),
            "key": f"{m}-{d}",
            "formula": f"55 - (({m}*2) + {d}) = {sv}",
        },
        interpretation="Computed via Magi Solar Value formula.",
        constants_version=constants["version"],
        references=["Magi Solar Value formula (Olney Richmond / Robert Lee Camp tradition)",
                    "SOURCE_TIER:C — Popularized by Olney Richmond (1893). No classical DOB-to-card algorithm documented."],
        question="Q1_IDENTITY"
    )
