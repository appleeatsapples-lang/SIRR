"""Bast wa Kasr (Expansion & Contraction) — COMPUTED_STRICT
Bast: spells out each Arabic letter by its full phonetic name.
Kasr: takes the expanded form and extracts hidden letters
(letters that appear in the expansion but not the original name).
Source: Shams al-Ma'arif (Al-Buni, 13th century)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Full Arabic letter names (Bast Harfi)
LETTER_NAMES = {
    "ا": "الف", "أ": "الف", "إ": "الف", "آ": "الف",
    "ب": "باء", "ت": "تاء", "ث": "ثاء", "ج": "جيم",
    "ح": "حاء", "خ": "خاء", "د": "دال", "ذ": "ذال",
    "ر": "راء", "ز": "زاي", "س": "سين", "ش": "شين",
    "ص": "صاد", "ض": "ضاد", "ط": "طاء", "ظ": "ظاء",
    "ع": "عين", "غ": "غين", "ف": "فاء", "ق": "قاف",
    "ك": "كاف", "ل": "لام", "م": "ميم", "ن": "نون",
    "ه": "هاء", "و": "واو", "ي": "ياء",
}


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    name_letters = [ch for ch in profile.arabic.replace(" ", "") if ch in abjad]
    original_set = set(name_letters)

    # BAST: expand each letter to its full name
    expanded_parts = []
    for ch in name_letters:
        expanded_parts.append(LETTER_NAMES.get(ch, ch))
    expanded_text = "".join(expanded_parts)

    # Collect all letters from expansion
    expanded_letters = [ch for ch in expanded_text if ch in abjad]

    # KASR: find hidden letters (in expansion but not original)
    hidden_letters = [ch for ch in expanded_letters if ch not in original_set]
    hidden_unique = list(dict.fromkeys(hidden_letters))  # preserve order, dedup

    # Abjad values
    expanded_value = sum(abjad.get(ch, 0) for ch in expanded_letters)
    hidden_value = sum(abjad.get(ch, 0) for ch in hidden_unique)
    original_value = sum(abjad.get(ch, 0) for ch in name_letters)

    return SystemResult(
        id="bast_kasr",
        name="Bast wa Kasr (بسط وكسر — Expansion & Contraction)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic,
            "original_letters": len(name_letters),
            "expanded_text": expanded_text,
            "expanded_letter_count": len(expanded_letters),
            "expanded_value": expanded_value,
            "original_value": original_value,
            "hidden_letters": "".join(hidden_unique),
            "hidden_letter_count": len(hidden_unique),
            "hidden_value": hidden_value,
            "hidden_root": reduce_number(hidden_value, keep_masters=()),
            "expansion_ratio": round(len(expanded_letters) / max(len(name_letters), 1), 2),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Bast Harfi: letter → full phonetic name expansion.",
            "Kasr: extraction of hidden identity from expanded form.",
            "Source: Shams al-Ma'arif, Al-Buni.",
        ],
        question="Q1_IDENTITY"
    )
