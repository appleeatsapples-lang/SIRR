"""Arabic Morphology Analysis (علم الصرف) — COMPUTED_STRICT
Classify each Arabic name word by its morphological pattern (وزن),
grammatical class, and voice (active/passive).

Compound name awareness: certain nasab positions may pair adjacent
words into a single generational unit. The position-to-word-pair map is
supplied per profile via ``profile.compound_metadata`` (see
``InputProfile``); the structural note is derived from the morphology
table when both component words are classified.
Sources: Sibawayh Al-Kitab, Wright's Arabic Grammar
"""
from __future__ import annotations
import json
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult
from sirr_core.private_overlay import load_and_merge, overlay_provides_lookups

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "arabic_linguistics_tables.json"
_TABLES = None

# Compound positions are now sourced from ``profile.compound_metadata`` at
# compute time (V-3c calibration boundary). The module-level constant is
# kept as an empty dict purely as a stable export for any external
# importer; it is never populated with profile-specific data.
COMPOUND_STRUCTURES: dict = {}


def _load_tables() -> dict:
    global _TABLES
    if _TABLES is None:
        public = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
        _TABLES = load_and_merge(public)
    return _TABLES


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    tables = _load_tables()
    morph_table = tables.get("name_morphology", {}) or {}
    has_lookups = overlay_provides_lookups(tables)

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

    # Detect compound name structures using the per-profile compound metadata.
    compound_names = []
    profile_compounds = profile.compound_metadata or {}
    for pos, pair in profile_compounds.items():
        if not pair or len(pair) < 2:
            continue
        w1, w2 = pair[0], pair[1]
        if pos + 1 < len(words) and words[pos] == w1 and words[pos + 1] == w2:
            entry1 = morph_table.get(w1) or {}
            entry2 = morph_table.get(w2) or {}
            cls1 = entry1.get("class", "unclassified")
            cls2 = entry2.get("class", "unclassified")
            structure = f"{cls1} + {cls2}" if entry1 and entry2 else "compound"
            compound_names.append({
                "compound": f"{w1} {w2}",
                "position": pos,
                "structure": structure,
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
        certainty="COMPUTED_STRICT" if has_lookups else "APPROX",
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
