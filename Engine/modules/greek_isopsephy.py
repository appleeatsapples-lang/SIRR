"""Greek Isopsephy — COMPUTED_STRICT
Maps Latin name letters to Greek letter numeric values.
Alpha=1, Beta=2, Gamma=3... Omega=800.
Uses phonetic transliteration: A→Alpha(1), B→Beta(2), etc.
Source: Classical Greek numerals / Isopsephy tradition
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Phonetic transliteration: Latin letter → Greek isopsephic value
GREEK_MAP = {
    'A': 1,   # Alpha
    'B': 2,   # Beta
    'G': 3,   # Gamma
    'D': 4,   # Delta
    'E': 5,   # Epsilon
    'F': 500, # Phi (closest phonetic)
    'H': 8,   # Eta
    'I': 10,  # Iota
    'K': 20,  # Kappa
    'L': 30,  # Lambda
    'M': 40,  # Mu
    'N': 50,  # Nu
    'O': 70,  # Omicron
    'P': 80,  # Pi
    'Q': 100, # Qoppa (archaic)
    'R': 100, # Rho
    'S': 200, # Sigma
    'T': 300, # Tau
    'U': 400, # Upsilon
    'V': 400, # Upsilon (variant)
    'W': 800, # Omega (double-U → Omega)
    'X': 60,  # Xi
    'Y': 400, # Upsilon
    'Z': 7,   # Zeta
    'C': 20,  # Kappa (C→K phonetic)
    'J': 10,  # Iota (J→I)
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [(ch, GREEK_MAP.get(ch, 0)) for ch in name if ch.isalpha()]
    total = sum(v for _, v in letters)
    root = reduce_number(total, keep_masters=(11, 22, 33))

    return SystemResult(
        id="greek_isopsephy",
        name="Greek Isopsephy (Ισοψηφία)",
        certainty="COMPUTED_STRICT",
        data={
            "name": profile.subject,
            "total": total,
            "root": root,
            "letter_count": len(letters),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Greek Isopsephy via Latin→Greek phonetic transliteration"],
        question="Q1_IDENTITY"
    )
