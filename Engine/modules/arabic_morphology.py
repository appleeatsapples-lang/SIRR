"""Arabic Morphology Analysis (علم الصرف) — COMPUTED_STRICT
Classify each Arabic name word by its morphological pattern (وزن),
grammatical class, and voice (active/passive).

Compound name awareness: عمر عاكف = proper noun + active participle (qualifier);
محمد وصفي = passive intensive + relative adjective.
Sources: Sibawayh Al-Kitab, Wright's Arabic Grammar
"""
from __future__ import annotations
import json
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "arabic_linguistics_tables.json"
_TABLES = None

# Compound name structures: positional compound detection
# Position in the 8-word chain → (first_word, second_word, structural_note)
COMPOUND_STRUCTURES = {
    3: ("عمر", "عاكف", "proper_noun + active_participle (qualifier)"),
    5: ("محمد", "وصفي", "passive_intensive + relative_adjective"),
}


def _load_tables() -> dict:
    global _TABLES
    if _TABLES is None:
        _TABLES = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    return _TABLES


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    tables = _load_tables()
    morph_table = tables["name_morphology"]

    words = profile.arabic.split()
    word_morphology = []
    voice_counts = {"active": 0, "passive": 0, "n/a": 0}
    class_counts = {}

    for word in words:
        entry = morph_table.get(word)
        if entry:
            voice = entry.get("voice", "n/a")
            cls = entry.get("class", "unknown")
            word_morphology.append({
                "word": word,
                "wazn": entry["wazn"],
                "wazn_latin": entry["wazn_latin"],
                "class": cls,
                "class_ar": entry.get("class_ar", ""),
                "form": entry.get("form", "I"),
                "voice": voice,
                "note": entry.get("note", ""),
            })
            voice_counts[voice] = voice_counts.get(voice, 0) + 1
            class_counts[cls] = class_counts.get(cls, 0) + 1
        else:
            word_morphology.append({
                "word": word,
                "wazn": None,
                "wazn_latin": None,
                "class": "unclassified",
                "class_ar": "",
                "form": None,
                "voice": "n/a",
                "note": "",
            })
            voice_counts["n/a"] += 1

    # Detect compound name structures
    compound_names = []
    for pos, (w1, w2, note) in COMPOUND_STRUCTURES.items():
        if pos + 1 < len(words) and words[pos] == w1 and words[pos + 1] == w2:
            compound_names.append({
                "compound": f"{w1} {w2}",
                "position": pos,
                "structure": note,
                "words": [w1, w2],
            })

    # Determine dominant voice (active vs passive, ignoring n/a)
    classified_voices = {k: v for k, v in voice_counts.items() if k != "n/a"}
    dominant_voice = max(classified_voices, key=classified_voices.get) if classified_voices else "n/a"

    # Active-passive ratio
    active = voice_counts.get("active", 0)
    passive = voice_counts.get("passive", 0)
    total_voiced = active + passive
    active_ratio = round(active / total_voiced * 100, 1) if total_voiced > 0 else 0
    passive_ratio = round(passive / total_voiced * 100, 1) if total_voiced > 0 else 0

    return SystemResult(
        id="arabic_morphology",
        name="Arabic Morphology Analysis (علم الصرف)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "arabic_name": profile.arabic,
            "word_morphology": word_morphology,
            "compound_names": compound_names,
            "voice_counts": voice_counts,
            "dominant_voice": dominant_voice,
            "active_ratio": active_ratio,
            "passive_ratio": passive_ratio,
            "class_distribution": class_counts,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Sibawayh, Al-Kitab",
            "Wright's Arabic Grammar (3rd ed.)",
        ],
        question="Q1_IDENTITY"
    )
