"""Special Letters (First Vowel Key + First Consonant Key) — COMPUTED_STRICT
First Vowel: first vowel in first name → Pythagorean value (inner motivation key).
First Consonant: first consonant in first name → Pythagorean value (outer approach key).
Source: Decoz Special Letters (p.130), Family Tree report
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

VOWELS = set("AEIOU")

PYTH = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    first_name = profile.subject.upper().split()[0] if profile.subject.split() else ""

    first_vowel_letter = None
    first_vowel_value = None
    first_consonant_letter = None
    first_consonant_value = None

    for ch in first_name:
        if ch in PYTH:
            if ch in VOWELS and first_vowel_letter is None:
                first_vowel_letter = ch
                first_vowel_value = PYTH[ch]
            elif ch not in VOWELS and first_consonant_letter is None:
                first_consonant_letter = ch
                first_consonant_value = PYTH[ch]
        if first_vowel_letter and first_consonant_letter:
            break

    return SystemResult(
        id="special_letters",
        name="Special Letters (First Vowel / First Consonant)",
        certainty="COMPUTED_STRICT",
        data={
            "first_name": first_name,
            "first_vowel_letter": first_vowel_letter or "?",
            "first_vowel_value": first_vowel_value or 0,
            "first_consonant_letter": first_consonant_letter or "?",
            "first_consonant_value": first_consonant_value or 0,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Decoz: First Vowel = inner motivation key; First Consonant = outer approach key (Special Letters p.130)",
            "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented.",
        ],
        question="Q1_IDENTITY",
    )
