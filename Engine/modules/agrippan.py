"""Agrippan Numerology — COMPUTED_STRICT
Cornelius Agrippa's Latin letter-number system from Three Books of Occult Philosophy (1533).
Maps Latin alphabet to planetary/elemental correspondences via numeric values.
Source: Agrippa, De Occulta Philosophia, Book II
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Agrippa's 3x9 grid: 9 units, 9 tens, 9 hundreds (adapted for 26 Latin letters)
AGRIPPA_MAP = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
    'K':10,'L':20,'M':30,'N':40,'O':50,'P':60,'Q':70,'R':80,'S':90,
    'T':100,'U':200,'V':200,'W':200,'X':300,'Y':400,'Z':500,
    'J':9,  # J=I in Agrippa's era
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [(ch, AGRIPPA_MAP.get(ch, 0)) for ch in name if ch.isalpha()]
    total = sum(v for _, v in letters)
    root = reduce_number(total, keep_masters=(11, 22, 33))
    return SystemResult(
        id="agrippan", name="Agrippan Numerology",
        certainty="COMPUTED_STRICT",
        data={"name": profile.subject, "total": total, "root": root,
              "letter_count": len(letters), "letter_breakdown": letters},
        interpretation=None, constants_version=constants["version"],
        references=["Cornelius Agrippa, De Occulta Philosophia (1533), Book II Latin numeral grid"],
        question="Q1_IDENTITY"
    )
