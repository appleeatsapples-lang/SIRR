"""Arabic Root Extraction (علم الاشتقاق) — COMPUTED_STRICT
Extract the trilateral root (جذر) from each Arabic name component
and map to primary meaning and semantic field.

Compound name awareness: when two adjacent nasab positions form a
compound generational unit, both component roots are extracted
independently and credited to the same generation. Compound positions
are configured in COMPOUND_POSITIONS below.
Sources: Lane's Lexicon, Lisan al-Arab, Maqayis al-Lugha (Ibn Faris)
"""
from __future__ import annotations
import json
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "arabic_linguistics_tables.json"
_TABLES = None

# Positional compound detection
COMPOUND_POSITIONS = {
    3: ("عمر", "عاكف"),
    5: ("محمد", "وصفي"),
}


def _load_tables() -> dict:
    global _TABLES
    if _TABLES is None:
        _TABLES = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    return _TABLES


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    tables = _load_tables()
    root_table = tables["name_roots"]
    abjad = constants["arabic_letters"]["abjad_kabir"]

    words = profile.arabic.split()
    word_roots = []
    all_root_letters = []

    for word in words:
        entry = root_table.get(word)
        if entry:
            root_letters = entry["root_letters"]
            word_roots.append({
                "word": word,
                "root": entry["root"],
                "root_letters": root_letters,
                "primary_meaning": entry["primary_meaning"],
                "semantic_field": entry["semantic_field"],
                "form": entry.get("form", "I"),
                "lane_ref": entry.get("lane_ref", ""),
            })
            all_root_letters.extend(root_letters)
        else:
            word_roots.append({
                "word": word,
                "root": None,
                "root_letters": [],
                "primary_meaning": "unclassified",
                "semantic_field": "unclassified",
                "form": None,
                "lane_ref": "",
            })

    # Build compound_roots: group roots by generational unit
    compound_roots = []
    i = 0
    while i < len(words):
        compound = COMPOUND_POSITIONS.get(i)
        if compound and i + 1 < len(words) and words[i] == compound[0] and words[i + 1] == compound[1]:
            roots = []
            for j in (i, i + 1):
                entry = root_table.get(words[j])
                if entry:
                    roots.append(entry["root"])
            compound_roots.append({
                "unit": f"{words[i]} {words[i + 1]}",
                "is_compound": True,
                "roots": roots,
            })
            i += 2
        else:
            entry = root_table.get(words[i])
            compound_roots.append({
                "unit": words[i],
                "is_compound": False,
                "roots": [entry["root"]] if entry and entry["root"] else [],
            })
            i += 1

    # Compute abjad sum of all root letters
    root_abjad_total = sum(abjad.get(ch, 0) for ch in all_root_letters)
    root_abjad_root = reduce_number(root_abjad_total, keep_masters=())

    # Count unique roots
    unique_roots = set()
    for wr in word_roots:
        if wr["root"]:
            unique_roots.add(wr["root"])

    # Semantic field distribution
    field_counts = {}
    for wr in word_roots:
        f = wr["semantic_field"]
        if f != "unclassified":
            field_counts[f] = field_counts.get(f, 0) + 1

    dominant_field = max(field_counts, key=field_counts.get) if field_counts else "none"

    return SystemResult(
        id="arabic_roots",
        name="Arabic Root Extraction (علم الاشتقاق)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "arabic_name": profile.arabic,
            "word_roots": word_roots,
            "compound_roots": compound_roots,
            "root_count": len(unique_roots),
            "root_abjad_total": root_abjad_total,
            "root_abjad_root": root_abjad_root,
            "semantic_fields": field_counts,
            "dominant_field": dominant_field,
            "all_root_letters": all_root_letters,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Lane's Arabic-English Lexicon",
            "Lisan al-Arab (Ibn Manzur)",
            "Maqayis al-Lugha (Ibn Faris)",
        ],
        question="Q1_IDENTITY"
    )
