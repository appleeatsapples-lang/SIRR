"""Coptic Isopsephy — COMPUTED_STRICT
Coptic alphabet numeric values via Latin transliteration.
Coptic inherited Greek values + added 6 Demotic letters.
Source: Coptic numeral tradition
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

COPTIC_MAP = {
    'A':1,'B':2,'G':3,'D':4,'E':5,'F':500,'H':8,'I':10,
    'K':20,'L':30,'M':40,'N':50,'O':70,'P':80,'R':100,
    'S':200,'T':300,'U':400,'V':400,'W':800,'X':60,'Y':400,'Z':7,
    'C':20,'J':10,'Q':90,
    # Coptic-specific: Shai(6), Fai(500), Khei(600), Hori(700), Gangia(3), Shima(900)
    # These map through closest Latin phonetic equivalents above
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [(ch, COPTIC_MAP.get(ch, 0)) for ch in name if ch.isalpha()]
    total = sum(v for _, v in letters)
    root = reduce_number(total, keep_masters=(11, 22, 33))
    return SystemResult(
        id="coptic_isopsephy", name="Coptic Isopsephy",
        certainty="COMPUTED_STRICT",
        data={"name": profile.subject, "total": total, "root": root, "letter_count": len(letters)},
        interpretation=None, constants_version=constants["version"],
        references=["Coptic numeral values via Latin transliteration"],
        question="Q1_IDENTITY"
    )
