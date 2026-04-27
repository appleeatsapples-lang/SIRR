"""Name Semantics — Semantic Field Convergence (علم المعاني) — LOOKUP_FIXED
Map each name to its semantic field and detect thematic clusters.
Uses pre-classified semantic taxonomy from Round 3 data.

Nasab structure: the name is grouped into generational UNITS, not raw words.
Compound names (two adjacent words referring to one ancestor) are treated as
a single semantic unit. Compound positions are supplied per profile via
``profile.compound_metadata`` (see ``InputProfile``); the module never
hardcodes profile-specific compound data (V-3c calibration boundary).
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
COMPOUND_POSITIONS: dict = {}

# Semantic field taxonomy: which fields belong to which cluster
CLUSTER_TAXONOMY = {
    "sacred_devotional": {
        "fields": {"veneration_awe", "theophory_audition", "stillness_devotion", "praise_recognition"},
        "label_en": "Sacred / Devotional",
        "label_ar": "القدسي / العبادي",
    },
    "construction": {
        "fields": {"time_cultivation", "chemistry_synthesis"},
        "label_en": "Construction / Building",
        "label_ar": "البناء / التعمير",
    },
    "observation": {
        "fields": {"definition_form"},
        "label_en": "Observation / Description",
        "label_ar": "المراقبة / الوصف",
    },
}


def _load_tables() -> dict:
    global _TABLES
    if _TABLES is None:
        public = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
        _TABLES = load_and_merge(public)
    return _TABLES


def _group_into_units(words: list[str], compounds: dict) -> list[dict]:
    """Group raw words into generational units, merging compound names.

    Uses positional detection from the per-profile compound metadata: compound
    names are identified by their position in the nasab chain, not by word
    alone. Returns list of dicts: ``{words: [...], label: str, is_compound: bool}``.
    """
    units = []
    i = 0
    while i < len(words):
        compound = compounds.get(i)
        if compound and len(compound) >= 2 and i + 1 < len(words) and words[i] == compound[0] and words[i + 1] == compound[1]:
            units.append({
                "words": [words[i], words[i + 1]],
                "label": f"{words[i]} {words[i + 1]}",
                "is_compound": True,
            })
            i += 2
        else:
            units.append({
                "words": [words[i]],
                "label": words[i],
                "is_compound": False,
            })
            i += 1
    return units


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    tables = _load_tables()
    root_table = tables.get("name_roots", {}) or {}
    has_lookups = overlay_provides_lookups(tables)

    words = profile.arabic.split()
    compounds = profile.compound_metadata or {}
    units = _group_into_units(words, compounds)

    unit_semantics = []
    field_list = []

    for unit in units:
        unit_fields = []
        unit_meanings = []
        for w in unit["words"]:
            entry = root_table.get(w)
            if entry:
                unit_fields.append(entry["semantic_field"])
                unit_meanings.append(entry["primary_meaning"])
            else:
                unit_fields.append("unclassified")
                unit_meanings.append("unclassified")

        unit_semantics.append({
            "unit": unit["label"],
            "is_compound": unit["is_compound"],
            "words": unit["words"],
            "semantic_fields": unit_fields,
            "primary_meanings": unit_meanings,
        })
        classified = [f for f in unit_fields if f != "unclassified"]
        field_list.extend(classified)

    # Cluster analysis — counts how many classified fields fall into each cluster
    total_classified = len(field_list)
    cluster_scores = {}
    cluster_units = {}
    for cluster_id, cluster_def in CLUSTER_TAXONOMY.items():
        matching = [f for f in field_list if f in cluster_def["fields"]]
        count = len(matching)
        cluster_scores[cluster_id] = count
        cluster_units[cluster_id] = [
            us["unit"] for us in unit_semantics
            if any(f in cluster_def["fields"] for f in us["semantic_fields"])
        ]

    dominant_cluster = max(cluster_scores, key=cluster_scores.get) if cluster_scores else "none"
    dominant_count = cluster_scores.get(dominant_cluster, 0)
    dominant_ratio = round(dominant_count / total_classified * 100, 1) if total_classified > 0 else 0

    # Build cluster detail
    clusters = []
    for cid, cdef in CLUSTER_TAXONOMY.items():
        clusters.append({
            "id": cid,
            "label_en": cdef["label_en"],
            "label_ar": cdef["label_ar"],
            "count": cluster_scores[cid],
            "units": cluster_units[cid],
        })

    return SystemResult(
        id="name_semantics",
        name="Name Semantics (علم المعاني)",
        certainty="LOOKUP_FIXED" if has_lookups else "APPROX",
        data={
            "module_class": "primary",
            "arabic_name": profile.arabic,
            "unit_count": len(units),
            "word_count": len(words),
            "unit_semantics": unit_semantics,
            "clusters": clusters,
            "dominant_cluster": dominant_cluster,
            "dominant_cluster_count": dominant_count,
            "dominant_cluster_ratio": dominant_ratio,
            "total_classified": total_classified,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Lane's Arabic-English Lexicon — semantic field classification",
            "Annemarie Schimmel, 'Islamic Names'",
        ],
        question="Q1_IDENTITY"
    )
