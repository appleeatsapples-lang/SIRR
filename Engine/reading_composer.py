#!/usr/bin/env python3
"""Reading Composer — assembles the final semantic reading from axis signals.

Ordering: digit → calendar → archetypal → sky → elemental → derived → cyclic
Shadow: multi-tradition (qliphah/Ketu/inversion)
Counterpoint: "Witness Signal" from axis tensions
Provenance: which modules contributed per section

Three thesis variants: Islamic, Kabbalistic, Chinese.
"""
from __future__ import annotations
import json
import os
from typing import Any, Dict, List, Optional

ENGINE = os.path.dirname(os.path.abspath(__file__))
ROOTS_PATH = os.path.join(ENGINE, "semantic_layer", "sirr_semantic_roots.json")
GLOSSARY_PATH = os.path.join(ENGINE, "semantic_layer", "arabic_glossary.json")

READING_ORDER = ["digit", "calendar", "archetypal", "sky", "elemental", "derived", "cyclic"]


def _load_json(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _get(sig: dict, key: str, default=None):
    """Get a value from either a dict or dataclass-like object."""
    if isinstance(sig, dict):
        return sig.get(key, default)
    return getattr(sig, key, default)


def compose_reading(
    axis_signals: dict,
    cross_axis: dict,
    combination: Optional[dict],
    profile_core: Optional[dict] = None,
    activation: Optional[list] = None,
    meta_patterns: Optional[list] = None,
) -> dict:
    """Compose the full semantic reading.

    Args:
        axis_signals: Dict of axis_id -> AxisSignal (dict)
        cross_axis: ResonanceResult (dict) from inter_axis_synthesizer
        combination: Combination engine result (dict)
        profile_core: Core profile data (name, dob, life_path, etc.)
        activation: Activation layer results (list of dicts)
        meta_patterns: Meta-pattern detector results (list of dicts)

    Returns:
        Complete reading dict with sections, shadow, counterpoint, provenance
    """
    roots_data = _load_json(ROOTS_PATH)
    glossary = _load_json(GLOSSARY_PATH)

    # Build per-axis sections in reading order
    sections = []
    provenance = {}

    for axis_id in READING_ORDER:
        sig = axis_signals.get(axis_id)
        if not sig or _get(sig, "module_count", 0) == 0:
            continue

        dom_root = _get(sig, "dominant_root")
        # Normalise: bool (True/False) must never reach JSON as a boolean — coerce to int or None
        if isinstance(dom_root, bool):
            dom_root = int(dom_root)  # True→1, False→0; upstream should fix the signal source
        dom_elem = _get(sig, "dominant_element")
        dom_sign = _get(sig, "dominant_sign")
        dom_planet = _get(sig, "dominant_planet")
        modules = _get(sig, "contributing_modules", [])

        # Get root label
        root_label = ""
        if dom_root is not None:
            root_info = roots_data.get("roots", {}).get(str(dom_root), {})
            root_label = root_info.get("label", "")

        section = {
            "axis": axis_id,
            "dominant_root": dom_root,
            "root_label": root_label,
            "dominant_element": dom_elem,
            "dominant_sign": dom_sign,
            "dominant_planet": dom_planet,
            "module_count": _get(sig, "module_count", 0),
        }

        # Activation state if available
        if activation:
            for act in activation:
                if act.get("axis_id") == axis_id:
                    section["activation_state"] = act.get("state")
                    break

        sections.append(section)
        provenance[axis_id] = modules

    # Shadow layer: multi-tradition shadow from dominant root
    shadow = _build_shadow(cross_axis, roots_data)

    # Counterpoint: witness signal from axis tensions
    counterpoint = _build_counterpoint(cross_axis)

    # Thesis variants
    theses = _build_theses(cross_axis, roots_data, glossary)

    # Fired meta-patterns
    fired_patterns = []
    if meta_patterns:
        fired_patterns = [p for p in meta_patterns if p.get("fired")]

    return {
        "sections": sections,
        "shadow": shadow,
        "counterpoint": counterpoint,
        "theses": theses,
        "meta_patterns_fired": fired_patterns,
        "provenance": provenance,
        "agreement_score": cross_axis.get("agreement_score", 0.0),
        "dominant_cross_root": cross_axis.get("dominant_cross_root"),
        "dominant_cross_element": cross_axis.get("dominant_cross_element"),
    }


def _build_shadow(cross_axis: dict, roots_data: dict) -> dict:
    """Multi-tradition shadow from the dominant cross-axis root."""
    dom_root = cross_axis.get("dominant_cross_root")
    if dom_root is None:
        return {"note": "No dominant cross-axis root — shadow indeterminate"}

    root_info = roots_data.get("roots", {}).get(str(dom_root), {})
    shadow_tags = root_info.get("shadow_tags", [])
    qliphah = root_info.get("qliphah", "")

    return {
        "root": dom_root,
        "shadow_tags": shadow_tags,
        "qliphah": qliphah,
        "note": "Multi-tradition shadow: these are the inversion/excess tendencies of the dominant root",
    }


def _build_counterpoint(cross_axis: dict) -> dict:
    """Witness Signal from axis tensions."""
    tensions = cross_axis.get("axis_tensions", [])
    if not tensions:
        return {"note": "No axis tensions detected — no counterpoint signal"}

    witnesses = []
    for t in tensions:
        witnesses.append({
            "axis_a": t.get("axis_a"),
            "axis_b": t.get("axis_b"),
            "pole_a": t.get("pole_a"),
            "pole_b": t.get("pole_b"),
            "root_a": t.get("root_a"),
            "root_b": t.get("root_b"),
        })

    return {
        "witness_count": len(witnesses),
        "witnesses": witnesses,
        "note": "These axes pull in opposing directions — the dialectic is structural, not accidental",
    }


def _build_theses(cross_axis: dict, roots_data: dict, glossary: dict) -> dict:
    """Three thesis variants: Islamic, Kabbalistic, Chinese."""
    dom_root = cross_axis.get("dominant_cross_root")
    dom_elem = cross_axis.get("dominant_cross_element")

    if dom_root is None:
        return {"note": "Insufficient data for thesis generation"}

    root_info = roots_data.get("roots", {}).get(str(dom_root), {})
    core_tags = root_info.get("core_tags", [])
    label = root_info.get("label", "")
    arabic_term = root_info.get("arabic_term", "")

    return {
        "islamic": {
            "frame": f"Through the lens of {arabic_term}: root {dom_root} as {label}",
            "element": dom_elem,
            "core_signal": core_tags[:2] if core_tags else [],
        },
        "kabbalistic": {
            "frame": f"Sephirotic path: {root_info.get('qliphah', 'unknown')} inverted → {label}",
            "element": dom_elem,
            "core_signal": core_tags[:2] if core_tags else [],
        },
        "chinese": {
            "frame": f"Wu Xing lens: {dom_elem or 'unknown'} phase with root {dom_root}",
            "element": dom_elem,
            "core_signal": core_tags[:2] if core_tags else [],
        },
    }
