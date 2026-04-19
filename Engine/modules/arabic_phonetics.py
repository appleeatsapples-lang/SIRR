"""Arabic Phonetics — Letter Articulation Analysis (علم المخارج والصفات) — COMPUTED_STRICT
Classify all letters in the Arabic name by makhraj (articulation point)
and sifat (phonetic qualities). Compute distribution.
Sources: Al-Khalil ibn Ahmad, Sibawayh, Tajweed science
"""
from __future__ import annotations
import json
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "arabic_phonetics_tables.json"
_TABLES = None


def _load_tables() -> dict:
    global _TABLES
    if _TABLES is None:
        _TABLES = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    return _TABLES


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    tables = _load_tables()
    artic_table = tables["letter_articulation"]

    name = profile.arabic.replace(" ", "")
    letters = [ch for ch in name if ch in artic_table]

    # Makhraj category distribution
    category_counts = {}
    category_en_counts = {}
    voiced_count = 0
    voiceless_count = 0
    emphatic_count = 0
    sifat_all = {}

    for ch in letters:
        entry = artic_table[ch]
        cat = entry["category"]
        cat_en = entry["category_en"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        category_en_counts[cat_en] = category_en_counts.get(cat_en, 0) + 1

        for s in entry["sifat"]:
            sifat_all[s] = sifat_all.get(s, 0) + 1
            if s == "voiced":
                voiced_count += 1
            elif s == "voiceless":
                voiceless_count += 1
            elif s == "elevated":
                emphatic_count += 1

    total = len(letters)

    # Percentages for category_en
    category_percentages = {}
    for k, v in category_en_counts.items():
        category_percentages[k] = round(v / total * 100, 1) if total > 0 else 0

    dominant_category = max(category_en_counts, key=category_en_counts.get) if category_en_counts else "unknown"
    dominant_category_ar = max(category_counts, key=category_counts.get) if category_counts else "unknown"

    # Voiced vs voiceless ratio
    voice_total = voiced_count + voiceless_count
    voiced_ratio = round(voiced_count / voice_total * 100, 1) if voice_total > 0 else 0
    voiceless_ratio = round(voiceless_count / voice_total * 100, 1) if voice_total > 0 else 0

    return SystemResult(
        id="arabic_phonetics",
        name="Arabic Phonetics (علم المخارج والصفات)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "arabic_name": profile.arabic,
            "total_letters": total,
            "makhraj_distribution": category_en_counts,
            "makhraj_distribution_ar": category_counts,
            "makhraj_percentages": category_percentages,
            "dominant_makhraj": dominant_category,
            "dominant_makhraj_ar": dominant_category_ar,
            "voiced_count": voiced_count,
            "voiceless_count": voiceless_count,
            "voiced_ratio": voiced_ratio,
            "voiceless_ratio": voiceless_ratio,
            "emphatic_count": emphatic_count,
            "sifat_distribution": sifat_all,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Al-Khalil ibn Ahmad al-Farahidi — Kitab al-Ayn",
            "Sibawayh — Al-Kitab (letter articulation)",
            "Classical Tajweed — Makhraj/Sifat classification",
        ],
        question="Q3_NATURE"
    )
