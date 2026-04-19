"""Notarikon — COMPUTED_STRICT"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Abjad values for Arabic letters
ABJAD = {
    'م': 40, 'ه': 5, 'ا': 1, 'ب': 2, 'ع': 70, 'ر': 200,
    'ك': 20, 'ف': 80, 'و': 6, 'ل': 30, 'ن': 50, 'ت': 400,
    'ث': 500, 'ج': 3, 'ح': 8, 'خ': 600, 'د': 4, 'ذ': 700,
    'س': 60, 'ش': 300, 'ص': 90, 'ض': 800, 'ط': 9, 'ظ': 900,
    'غ': 1000, 'ق': 100, 'ي': 10,
}

PYTH = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
    'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9,
    'S':1,'T':2,'U':3,'V':4,'W':5,'X':6,'Y':7,'Z':8
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    # Arabic initials
    arabic_words = profile.arabic.split()
    arabic_initials = [w[0] for w in arabic_words if w]
    arabic_vals = [ABJAD.get(c, 0) for c in arabic_initials]
    arabic_sum = sum(arabic_vals)
    arabic_root = reduce_number(arabic_sum, keep_masters=())

    # Latin initials
    latin_words = profile.subject.split()
    latin_initials = [w[0].upper() for w in latin_words if w]
    latin_vals = [PYTH.get(c, 0) for c in latin_initials]
    latin_sum = sum(latin_vals)
    latin_root = reduce_number(latin_sum)

    # Check for double letters
    from collections import Counter
    ar_counter = Counter(arabic_initials)
    repeated_ar = {k: v for k, v in ar_counter.items() if v > 1}

    return SystemResult(
        id="notarikon",
        name="Notarikon (Initial-Letter Analysis)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_initials": " ".join(arabic_initials),
            "arabic_values": dict(zip(arabic_initials, arabic_vals)),
            "arabic_sum": arabic_sum,
            "arabic_root": arabic_root,
            "latin_initials": ".".join(latin_initials),
            "latin_values": dict(zip(latin_initials, latin_vals)),
            "latin_sum": latin_sum,
            "latin_root": latin_root,
            "repeated_arabic": repeated_ar,
            "has_master_number": latin_root in (11, 22, 33)
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Abjad Kabir values for Arabic; Pythagorean for Latin"],
        question="Q1_IDENTITY"
    )
