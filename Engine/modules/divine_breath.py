"""Divine Breath — Makhraj Distribution as Breath Texture — COMPUTED_STRICT
Treats the phonetic articulation distribution as a "breath signature" —
how the name distributes across the vocal apparatus.
Computes Shannon entropy of the makhraj distribution.
"""
from __future__ import annotations
import json
import math
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
    artic = tables["letter_articulation"]

    name = profile.arabic.replace(" ", "")
    letters = [ch for ch in name if ch in artic]
    total = len(letters)

    # Makhraj distribution
    makhraj_counts = {}
    for ch in letters:
        m = artic[ch]["makhraj"]
        makhraj_counts[m] = makhraj_counts.get(m, 0) + 1

    # Category-level distribution (broader grouping)
    category_counts = {}
    for ch in letters:
        cat = artic[ch]["category_en"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Shannon entropy of makhraj distribution
    entropy = 0.0
    if total > 0:
        for count in makhraj_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

    # Max possible entropy (uniform distribution across all makhraj points)
    n_categories = len(makhraj_counts)
    max_entropy = math.log2(n_categories) if n_categories > 1 else 0
    normalized_entropy = round(entropy / max_entropy, 3) if max_entropy > 0 else 0

    entropy = round(entropy, 3)

    # Breath zones: how much comes from deep (throat) vs mid (tongue) vs outer (lips)
    deep = sum(v for k, v in category_counts.items() if k == "guttural")
    mid = sum(v for k, v in category_counts.items() if k not in ("guttural", "bilabial", "labio-dental"))
    outer = sum(v for k, v in category_counts.items() if k in ("bilabial", "labio-dental"))

    deep_ratio = round(deep / total * 100, 1) if total > 0 else 0
    mid_ratio = round(mid / total * 100, 1) if total > 0 else 0
    outer_ratio = round(outer / total * 100, 1) if total > 0 else 0

    # Dominant zone
    zones = {"deep_throat": deep, "mid_tongue": mid, "outer_lips": outer}
    dominant_zone = max(zones, key=zones.get)

    return SystemResult(
        id="divine_breath",
        name="Divine Breath (النفس الإلهي)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "total_letters": total,
            "makhraj_distribution": makhraj_counts,
            "category_distribution": category_counts,
            "entropy": entropy,
            "max_entropy": round(max_entropy, 3),
            "normalized_entropy": normalized_entropy,
            "deep_throat_count": deep,
            "mid_tongue_count": mid,
            "outer_lips_count": outer,
            "deep_ratio": deep_ratio,
            "mid_ratio": mid_ratio,
            "outer_ratio": outer_ratio,
            "dominant_zone": dominant_zone,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Al-Khalil ibn Ahmad — articulation zones",
            "Nafas al-Rahman — breath as vehicle of divine speech",
        ],
        question="Q3_NATURE"
    )
