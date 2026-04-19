"""Tarot Name Cards — COMPUTED_STRICT
Derives Major Arcana correspondence from name numerology values.
Expression number → primary name card, Soul Urge → soul card.
Source: Mary K. Greer, Rachel Pollack
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

PYTHAGOREAN = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
    'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9,
    'S':1,'T':2,'U':3,'V':4,'W':5,'X':6,'Y':7,'Z':8,
}
VOWELS = set("AEIOUaeiou")
MAJOR_ARCANA = {
    1:"The Magician",2:"The High Priestess",3:"The Empress",
    4:"The Emperor",5:"The Hierophant",6:"The Lovers",7:"The Chariot",
    8:"Strength",9:"The Hermit",10:"Wheel of Fortune",11:"Justice",
    12:"The Hanged Man",13:"Death",14:"Temperance",15:"The Devil",
    16:"The Tower",17:"The Star",18:"The Moon",19:"The Sun",
    20:"Judgement",21:"The World",22:"The Fool (0/22)",
}

def _reduce_tarot(n: int) -> int:
    while n > 22:
        n = sum(int(d) for d in str(n))
    return n

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    all_vals = [PYTHAGOREAN.get(ch, 0) for ch in name if ch.isalpha()]
    vowel_vals = [PYTHAGOREAN.get(ch, 0) for ch in name if ch.upper() in VOWELS]

    expr_raw = sum(all_vals)
    soul_raw = sum(vowel_vals)

    expr_card = _reduce_tarot(reduce_number(expr_raw, keep_masters=(11,22)))
    soul_card = _reduce_tarot(reduce_number(soul_raw, keep_masters=(11,22)))

    return SystemResult(
        id="tarot_name",
        name="Tarot Name Cards",
        certainty="COMPUTED_STRICT",
        data={
            "expression_raw": expr_raw,
            "expression_card_number": expr_card,
            "expression_card_name": MAJOR_ARCANA.get(expr_card, f"Arcanum {expr_card}"),
            "soul_urge_raw": soul_raw,
            "soul_card_number": soul_card,
            "soul_card_name": MAJOR_ARCANA.get(soul_card, f"Arcanum {soul_card}"),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Greer: Expression → primary name arcanum, Soul Urge → soul arcanum"],
        question="Q1_IDENTITY"
    )
