"""Cornerstone / First Vowel / Capstone — COMPUTED_STRICT
Cornerstone: first letter of first name (approach to life).
First Vowel: first vowel in name (inner motivation).
Capstone: last letter of first name (completion style).
Source: Standard Western Numerology (Decoz, Goodwin)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

VOWELS = set("AEIOUaeiou")

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.strip()
    first_name = name.split()[0] if name.split() else name

    cornerstone = first_name[0].upper() if first_name else "?"
    capstone = first_name[-1].upper() if first_name else "?"

    first_vowel = "?"
    for ch in name:
        if ch.upper() in VOWELS:
            first_vowel = ch.upper()
            break

    return SystemResult(
        id="cornerstone",
        name="Cornerstone / First Vowel / Capstone",
        certainty="COMPUTED_STRICT",
        data={
            "full_name": name,
            "first_name": first_name,
            "cornerstone": cornerstone,
            "first_vowel": first_vowel,
            "capstone": capstone,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Decoz: first letter = Cornerstone, first vowel = inner motivation, last letter of first name = Capstone",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q1_IDENTITY"
    )
