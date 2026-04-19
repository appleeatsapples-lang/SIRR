"""Georgian Alphabetic Numerals — COMPUTED_STRICT
Georgian Asomtavruli: 37 letters with values 1-9, 10-90, 100-900, 1000-9000.
Source: Georgian numeral tradition (Mkhedruli/Asomtavruli scripts)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

GEORGIAN_MAP = {
    'A':1,'B':2,'G':3,'D':4,'E':5,'F':500,'H':8,'I':10,
    'K':20,'L':30,'M':40,'N':50,'O':70,'P':80,'R':200,
    'S':300,'T':400,'U':600,'V':4000,'W':800,'X':60,'Y':700,'Z':7,
    'C':20,'J':10,'Q':9000,
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [(ch, GEORGIAN_MAP.get(ch, 0)) for ch in name if ch.isalpha()]
    total = sum(v for _, v in letters)
    root = reduce_number(total, keep_masters=(11, 22, 33))
    return SystemResult(
        id="georgian_gematria", name="Georgian Alphabetic Numerals",
        certainty="COMPUTED_STRICT",
        data={"name": profile.subject, "total": total, "root": root, "letter_count": len(letters)},
        interpretation=None, constants_version=constants["version"],
        references=["Georgian Asomtavruli numeral values via Latin phonetic transliteration"],
        question="Q1_IDENTITY"
    )
