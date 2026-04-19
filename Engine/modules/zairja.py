"""Zairja — Combinatorial Letter Device — COMPUTED_STRICT

Scholarship fidelity (§4.5 rule 4 — Ibn Khaldun documented AND rejected):
  Ibn Khaldun describes zairja in the Muqaddimah (Book III, Ch. 6) as a real
  combinatorial device used by Sufi and Maghribi circles — and rejects it as
  "mechanical, non-prophetic, outside reliable epistemology." SIRR uses it as
  a deterministic computation, NOT as oracular speech. Silent reliance on
  Ibn Khaldun's documentation while omitting his critique would be scholarship
  by half-truth. Both halves are named.

Algorithmic lineage: Ibn Khaldun (as documentarian, not endorser) and
Abu al-Abbas al-Sabti.

Combines the Abjad Kabir sum of the Arabic name with the natal ascendant degree
to derive a starting lunar mansion (manzil), then applies a chord sequence to
generate 8 letters mapped to elemental natures.

Algorithm:
  1. Abjad Kabir sum of full Arabic name
  2. (Abjad_Sum + floor(Ascendant_Degree)) % 28 → manzil index
  3. Map manzil index → starting Arabic letter (28 Mansions-to-Letters table)
  4. Apply Ibn Khaldun chord sequence [4, 7, 3, 8, 5, 2, 6] cyclically
     from starting index to generate 8 total letters
  5. Map each letter to elemental nature per Al-Buni classification

Edge cases: Ta Marbuta (ة) → Ha (ه) = 5, Hamza variants → Alif (ا) = 1

Sources: Ibn Khaldun (Muqaddimah, Ch. 6), Abu al-Abbas al-Sabti,
         Al-Buni (Shams al-Ma'arif)
"""
from __future__ import annotations
import math
from sirr_core.types import InputProfile, SystemResult

# 28 Arabic letters in Abjad order, mapped to Manzil index
MANZIL_LETTERS = [
    "ا", "ب", "ج", "د", "ه", "و", "ز", "ح", "ط", "ي",
    "ك", "ل", "م", "ن", "س", "ع", "ف", "ص", "ق", "ر",
    "ش", "ت", "ث", "خ", "ذ", "ض", "ظ", "غ",
]

MANZIL_NAMES = [
    "Al-Sharatain", "Al-Butain", "Al-Thuraya", "Al-Dabaran",
    "Al-Haqah", "Al-Hanah", "Al-Dhira", "Al-Nathrah",
    "Al-Tarf", "Al-Jabhah", "Al-Zubrah", "Al-Sarfah",
    "Al-Awwa", "Al-Simak", "Al-Ghafr", "Al-Zubana",
    "Al-Iklil", "Al-Qalb", "Al-Shawlah", "Al-Naayim",
    "Al-Baldah", "Sad al-Dhabih", "Sad al-Bula", "Sad al-Suud",
    "Sad al-Akhbiyah", "Al-Fargh al-Awwal", "Al-Fargh al-Thani", "Batn al-Hut",
]

# Al-Buni elemental classification of the 28 letters
ELEMENT_MAP = {
    "ا": "Fire", "ه": "Fire", "ط": "Fire", "م": "Fire",
    "ف": "Fire", "ش": "Fire", "ذ": "Fire",
    "ب": "Earth", "و": "Earth", "ي": "Earth", "ن": "Earth",
    "ص": "Earth", "ت": "Earth", "ض": "Earth",
    "ج": "Air", "ز": "Air", "ك": "Air", "س": "Air",
    "ق": "Air", "ث": "Air", "ظ": "Air",
    "د": "Water", "ح": "Water", "ل": "Water", "ع": "Water",
    "ر": "Water", "خ": "Water", "غ": "Water",
}

# Ibn Khaldun chord sequence
CHORD_SEQUENCE = [4, 7, 3, 8, 5, 2, 6]


def _abjad_sum(arabic_name: str, abjad_table: dict) -> int:
    """Compute Abjad Kabir sum with edge case handling."""
    total = 0
    for ch in arabic_name:
        if ch == "\u0629":  # ة Ta Marbuta → Ha (5)
            total += 5
        elif ch in ("\u0621", "\u0623", "\u0625", "\u0622"):  # ء أ إ آ → Alif (1)
            total += 1
        elif ch in abjad_table:
            total += abjad_table[ch]
    return total


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="zairja",
            name="Zairja (mechanical letter device — Ibn Khaldun)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required for ascendant degree"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q2_PATH",
        )

    # Step 1: Abjad Kabir sum of Arabic name
    abjad_table = constants.get("arabic_letters", {}).get("abjad_kabir", {})
    arabic_name = profile.arabic or ""
    abjad_total = _abjad_sum(arabic_name, abjad_table)

    # Step 2: Ascendant degree
    asc_degree = natal_chart_data.get("ascendant", {}).get("longitude", 0)
    asc_floor = int(math.floor(asc_degree))

    # Manzil index
    manzil_index = (abjad_total + asc_floor) % 28

    # Step 3: Starting letter and manzil
    starting_letter = MANZIL_LETTERS[manzil_index]
    starting_manzil = MANZIL_NAMES[manzil_index]

    # Step 4: Generate 8 letters using chord sequence
    chord_letters = [starting_letter]
    current_idx = manzil_index
    for i in range(7):
        step = CHORD_SEQUENCE[i]
        current_idx = (current_idx + step) % 28
        chord_letters.append(MANZIL_LETTERS[current_idx])

    # Step 5: Map to elements
    elemental_sequence = [ELEMENT_MAP.get(ch, "Unknown") for ch in chord_letters]

    # Element counts
    element_counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    for elem in elemental_sequence:
        if elem in element_counts:
            element_counts[elem] += 1

    dominant_element = max(element_counts, key=element_counts.get)

    data = {
        "abjad_sum": abjad_total,
        "ascendant_degree": round(asc_degree, 2),
        "manzil_index": manzil_index,
        "starting_manzil": starting_manzil,
        "starting_letter": starting_letter,
        "chord_sequence": chord_letters,
        "elemental_sequence": elemental_sequence,
        "element_summary": element_counts,
        "dominant_element": dominant_element,
        # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
        "scholarship_fidelity": "CLASSICAL_METHOD_MODERN_APPLICATION",
        "scholarship_note": "Ibn Khaldun documented (Muqaddimah III Ch. 6) AND rejected as mechanical, non-prophetic. SIRR uses deterministically.",
    }

    return SystemResult(
        id="zairja",
        name="Zairja (mechanical letter device — Ibn Khaldun)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Ibn Khaldun, Al-Muqaddimah, Book III Ch. 6 — documents zairja method",
            "Ibn Khaldun, Al-Muqaddimah, Book III Ch. 6 — rejects zairja as mechanical, non-prophetic (scholarship fidelity requires both)",
            "Abu al-Abbas al-Sabti — combinatorial letter device",
            "Al-Buni, Shams al-Ma'arif — elemental letter classification",
        ],
        question="Q2_PATH",
    )
