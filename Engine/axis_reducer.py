#!/usr/bin/env python3
"""Axis Reducer — routes module results to semantic axes and extracts dominant signals.

Loads axis_taxonomy.json and reduces 150 module outputs into 9 AxisSignal summaries.
Each axis gets: dominant root, dominant element, dominant sign, dominant planet,
timing quality, module count, and contributing module IDs.

CLI: python axis_reducer.py [output.json]
"""
from __future__ import annotations
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

ENGINE = os.path.dirname(os.path.abspath(__file__))
TAXONOMY_PATH = os.path.join(ENGINE, "semantic_layer", "axis_taxonomy.json")

ELEMENTS = ["fire", "water", "earth", "air", "wood", "metal", "ether"]

# Per-module whitelist of fields that contain genuine element classifications.
# Only these fields are read for element extraction — prevents inflation from
# compound strings like "Yin Fire Snake" in bazi_pillars descriptions.
ELEMENT_FIELD_WHITELIST: dict[str, set[str]] = {
    "bazi_daymaster":    {"day_master_element"},
    "bazi_ten_gods":     {"day_master_element"},
    "chinese_zodiac":    {"stem_element"},
    "temperament":       {"primary_element", "secondary_element"},
    "elemental_letters": {"dominant_element", "secondary_element"},
    "nakshatra":         {"element"},
    "nine_star_ki":      {"year_element", "month_element"},
    "tibetan_mewa":      {"mewa_element", "parkha_element"},
    "onmyodo":           {"birth_element"},
    "nayin":             {"element"},
    "bazhai":            {"gua_element"},
    "taiyi":             {"taiyi_palace_element"},
}

ZODIAC_SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

PLANETS = [
    "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
    "uranus", "neptune", "pluto", "rahu", "ketu", "north node", "south node"
]


@dataclass
class AxisSignal:
    axis_id: str
    dominant_root: Optional[int] = None
    root_votes: Dict[int, int] = field(default_factory=dict)
    dominant_element: Optional[str] = None
    element_votes: Dict[str, int] = field(default_factory=dict)
    dominant_sign: Optional[str] = None
    dominant_planet: Optional[str] = None
    timing_quality: Optional[str] = None
    module_count: int = 0
    contributing_modules: List[str] = field(default_factory=list)


def load_taxonomy() -> dict:
    """Load axis_taxonomy.json."""
    with open(TAXONOMY_PATH) as f:
        return json.load(f)


def _build_module_to_axes(taxonomy: dict) -> Dict[str, List[str]]:
    """Build reverse mapping: module_id -> list of axis IDs."""
    mapping = {}
    for axis_id, axis_data in taxonomy["axes"].items():
        for mod_id in axis_data["modules"]:
            mapping.setdefault(mod_id, []).append(axis_id)
    # Add multi-axis assignments
    for mod_id, axes in taxonomy.get("multi_axis_modules", {}).items():
        for ax in axes:
            if ax not in mapping.get(mod_id, []):
                mapping.setdefault(mod_id, []).append(ax)
    return mapping


def _get_data(result) -> dict:
    """Get data dict from either a SystemResult object or a dict."""
    if isinstance(result, dict):
        return result.get("data", {})
    return getattr(result, "data", {})


def _get_id(result) -> str:
    """Get module ID from either a SystemResult object or a dict."""
    if isinstance(result, dict):
        return result.get("id", "")
    return getattr(result, "id", "")


def _extract_roots(data: dict) -> List[int]:
    """Extract root numbers (1-33) from a module's data dict."""
    roots = []
    for key, val in data.items():
        if isinstance(val, int) and 1 <= val <= 33:
            roots.append(val)
        elif isinstance(val, dict):
            for k2, v2 in val.items():
                if isinstance(v2, int) and 1 <= v2 <= 33:
                    roots.append(v2)
    return roots


def _extract_elements(data: dict, module_id: str = "") -> List[str]:
    """Extract element references from a module's data dict.

    Uses ELEMENT_FIELD_WHITELIST to only read fields that contain genuine
    element classifications.  Modules not in the whitelist contribute nothing.
    """
    allowed_fields = ELEMENT_FIELD_WHITELIST.get(module_id)
    if allowed_fields is None:
        return []

    found = []
    for key, val in data.items():
        if key not in allowed_fields:
            continue
        if isinstance(val, str):
            val_lower = val.lower()
            for elem in ELEMENTS:
                if elem in val_lower:
                    found.append(elem.capitalize())
    return found


def _extract_signs(data: dict) -> List[str]:
    """Extract zodiac sign references from a module's data dict."""
    found = []
    for key, val in data.items():
        if isinstance(val, str):
            val_lower = val.lower()
            for sign in ZODIAC_SIGNS:
                if sign in val_lower:
                    found.append(sign.capitalize())
        elif isinstance(val, dict):
            for k2, v2 in val.items():
                if isinstance(v2, str):
                    v2_lower = v2.lower()
                    for sign in ZODIAC_SIGNS:
                        if sign in v2_lower:
                            found.append(sign.capitalize())
    return found


def _extract_planets(data: dict) -> List[str]:
    """Extract planet references from a module's data dict."""
    found = []
    for key, val in data.items():
        if isinstance(val, str):
            val_lower = val.lower()
            for planet in PLANETS:
                if planet in val_lower:
                    found.append(planet.title())
        elif isinstance(val, dict):
            for k2, v2 in val.items():
                if isinstance(v2, str):
                    v2_lower = v2.lower()
                    for planet in PLANETS:
                        if planet in v2_lower:
                            found.append(planet.title())
    return found


def _dominant(counter: Counter) -> Optional[Any]:
    """Return the most common item, or None if empty."""
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def reduce_axes(results: list, taxonomy: dict = None) -> Dict[str, AxisSignal]:
    """Route each module result to its axis(es) and extract dominant signals.

    Args:
        results: List of SystemResult objects or dicts
        taxonomy: Pre-loaded taxonomy dict (loads from file if None)

    Returns:
        Dict mapping axis_id -> AxisSignal
    """
    if taxonomy is None:
        taxonomy = load_taxonomy()

    module_to_axes = _build_module_to_axes(taxonomy)

    # Initialize axis accumulators
    axis_roots: Dict[str, Counter] = {}
    axis_elements: Dict[str, Counter] = {}
    axis_signs: Dict[str, Counter] = {}
    axis_planets: Dict[str, Counter] = {}
    axis_modules: Dict[str, List[str]] = {}

    for axis_id in taxonomy["axes"]:
        axis_roots[axis_id] = Counter()
        axis_elements[axis_id] = Counter()
        axis_signs[axis_id] = Counter()
        axis_planets[axis_id] = Counter()
        axis_modules[axis_id] = []

    # Route each result to its axes
    for result in results:
        mod_id = _get_id(result)
        data = _get_data(result)
        axes = module_to_axes.get(mod_id, [])

        if not axes:
            continue

        roots = _extract_roots(data)
        elements = _extract_elements(data, mod_id)
        signs = _extract_signs(data)
        planets = _extract_planets(data)

        for axis_id in axes:
            if axis_id not in axis_modules:
                continue
            axis_modules[axis_id].append(mod_id)
            for r in roots:
                axis_roots[axis_id][r] += 1
            for e in elements:
                axis_elements[axis_id][e] += 1
            for s in signs:
                axis_signs[axis_id][s] += 1
            for p in planets:
                axis_planets[axis_id][p] += 1

    # Build AxisSignal for each axis
    signals = {}
    for axis_id in taxonomy["axes"]:
        root_counter = axis_roots[axis_id]
        elem_counter = axis_elements[axis_id]

        signals[axis_id] = AxisSignal(
            axis_id=axis_id,
            dominant_root=_dominant(root_counter),
            root_votes=dict(root_counter),
            dominant_element=_dominant(elem_counter),
            element_votes=dict(elem_counter),
            dominant_sign=_dominant(axis_signs[axis_id]),
            dominant_planet=_dominant(axis_planets[axis_id]),
            timing_quality=None,  # Filled by activation_detector
            module_count=len(axis_modules[axis_id]),
            contributing_modules=axis_modules[axis_id],
        )

    # ── Inject timing_quality from cyclic modules' period_quality ──────────
    # Collect period_quality votes from all cyclic-axis modules
    CONTRACTIVE_SIGNALS = {"contractive", "challenging", "difficult", "unfavorable",
                           "mixed", "karmic"}
    EXPANSIVE_SIGNALS   = {"expansive", "favorable", "beneficial", "positive",
                           "auspicious", "growth"}

    cyclic_pq_votes: list[str] = []
    for result in results:
        mod_id = _get_id(result)
        if "cyclic" not in module_to_axes.get(mod_id, []):
            continue
        data = _get_data(result)
        pq = data.get("period_quality")
        if pq and isinstance(pq, str):
            cyclic_pq_votes.append(pq.lower())

    if cyclic_pq_votes and "cyclic" in signals:
        from collections import Counter as _PQCounter
        vote_counts = _PQCounter(cyclic_pq_votes)
        top_vote = vote_counts.most_common(1)[0][0]

        # Map to activation_detector vocabulary
        if any(s in top_vote for s in CONTRACTIVE_SIGNALS):
            consensus_quality = "CONTRACTIVE"
        elif any(s in top_vote for s in EXPANSIVE_SIGNALS):
            consensus_quality = "EXPANSIVE"
        else:
            consensus_quality = "TRANSITIONAL"

        signals["cyclic"].timing_quality = consensus_quality
    # ── End timing_quality injection ───────────────────────────────────────

    return signals


def signals_to_dict(signals: Dict[str, AxisSignal]) -> dict:
    """Convert AxisSignal dict to JSON-serializable dict."""
    return {k: asdict(v) for k, v in signals.items()}


def main():
    """CLI entry point."""
    output_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ENGINE, "output.json")

    with open(output_path) as f:
        output = json.load(f)

    results = output.get("results", [])
    taxonomy = load_taxonomy()
    signals = reduce_axes(results, taxonomy)

    print("Axis Reduction Summary:")
    print("=" * 60)
    for axis_id, sig in signals.items():
        if sig.module_count == 0:
            print(f"  {axis_id:12s}: (no modules)")
            continue
        print(f"  {axis_id:12s}: {sig.module_count:3d} modules | "
              f"root={sig.dominant_root or '?':>2} | "
              f"elem={sig.dominant_element or '?':>6} | "
              f"sign={sig.dominant_sign or '?'}")

    # Write to file for inspection
    out_path = os.path.join(ENGINE, "axis_reduction.json")
    with open(out_path, "w") as f:
        json.dump(signals_to_dict(signals), f, indent=2, ensure_ascii=False)
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
