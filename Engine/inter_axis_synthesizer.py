#!/usr/bin/env python3
"""Inter-Axis Synthesizer — detects cross-axis convergence and tension.

Takes AxisSignal dict from axis_reducer and finds:
- Root agreement: which axes share the same dominant root
- Element agreement: which axes share the same dominant element
- Cross-axis nodes: (axis_a, axis_b, shared_value) triples
- Axis tensions: opposing bipolar signals between axes

CLI: python inter_axis_synthesizer.py [axis_reduction.json]
"""
from __future__ import annotations
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

ENGINE = os.path.dirname(os.path.abspath(__file__))
BIPOLAR_PATH = os.path.join(ENGINE, "semantic_layer", "bipolar_pairs.json")
ROOTS_PATH = os.path.join(ENGINE, "semantic_layer", "sirr_semantic_roots.json")


@dataclass
class ResonanceResult:
    root_agreement: Dict[int, List[str]] = field(default_factory=dict)
    element_agreement: Dict[str, List[str]] = field(default_factory=dict)
    cross_axis_nodes: List[Dict[str, Any]] = field(default_factory=list)
    axis_tensions: List[Dict[str, Any]] = field(default_factory=list)
    dominant_cross_root: Optional[int] = None
    dominant_cross_element: Optional[str] = None
    agreement_score: float = 0.0


def _load_bipolar_pairs() -> dict:
    """Load bipolar_pairs.json."""
    try:
        with open(BIPOLAR_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _load_roots() -> dict:
    """Load sirr_semantic_roots.json."""
    try:
        with open(ROOTS_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _build_opposition_map(bipolar: dict) -> Dict[str, str]:
    """Build a map of bipolar_axis value -> its opposite."""
    opposites = {}
    for pair in bipolar.get("pairs", []):
        a = pair.get("pole_a", "")
        b = pair.get("pole_b", "")
        if a and b:
            opposites[a] = b
            opposites[b] = a
    return opposites


def synthesize_across_axes(axis_signals: dict) -> ResonanceResult:
    """Find cross-axis agreement and tension.

    Args:
        axis_signals: Dict of axis_id -> AxisSignal (as dict or dataclass)

    Returns:
        ResonanceResult with agreement and tension data
    """
    bipolar = _load_bipolar_pairs()
    roots_data = _load_roots()
    opposites = _build_opposition_map(bipolar)

    # Extract root's bipolar axis from semantic roots
    root_bipolar = {}
    for root_key, root_info in roots_data.get("roots", {}).items():
        if isinstance(root_info, dict):
            bp = root_info.get("bipolar_axis")
            if bp:
                root_bipolar[int(root_key)] = bp

    result = ResonanceResult()

    # Collect dominant roots and elements per axis
    root_axes = defaultdict(list)  # root_number -> [axis_ids]
    elem_axes = defaultdict(list)  # element -> [axis_ids]

    active_axes = []
    for axis_id, sig in axis_signals.items():
        if isinstance(sig, dict):
            dom_root = sig.get("dominant_root")
            dom_elem = sig.get("dominant_element")
            mod_count = sig.get("module_count", 0)
        else:
            dom_root = sig.dominant_root
            dom_elem = sig.dominant_element
            mod_count = sig.module_count

        if mod_count == 0:
            continue
        active_axes.append(axis_id)

        if dom_root is not None:
            root_axes[dom_root].append(axis_id)
        if dom_elem is not None:
            elem_axes[dom_elem].append(axis_id)

    # Root agreement: roots that appear as dominant in 2+ axes
    for root, axes in root_axes.items():
        if len(axes) >= 2:
            result.root_agreement[root] = axes
            for i, a in enumerate(axes):
                for b in axes[i + 1:]:
                    result.cross_axis_nodes.append({
                        "type": "root",
                        "value": root,
                        "axis_a": a,
                        "axis_b": b,
                    })

    # Element agreement: elements dominant in 2+ axes
    for elem, axes in elem_axes.items():
        if len(axes) >= 2:
            result.element_agreement[elem] = axes
            for i, a in enumerate(axes):
                for b in axes[i + 1:]:
                    result.cross_axis_nodes.append({
                        "type": "element",
                        "value": elem,
                        "axis_a": a,
                        "axis_b": b,
                    })

    # Axis tensions: detect opposing bipolar axes between dominant roots
    seen_tensions = set()
    for axis_a in active_axes:
        sig_a = axis_signals[axis_a]
        root_a = sig_a.get("dominant_root") if isinstance(sig_a, dict) else sig_a.dominant_root
        if root_a is None:
            continue
        bp_a = root_bipolar.get(root_a)
        if not bp_a:
            continue

        for axis_b in active_axes:
            if axis_b <= axis_a:
                continue
            sig_b = axis_signals[axis_b]
            root_b = sig_b.get("dominant_root") if isinstance(sig_b, dict) else sig_b.dominant_root
            if root_b is None:
                continue
            bp_b = root_bipolar.get(root_b)
            if not bp_b:
                continue

            # Check if these roots are bipolar opposites
            if opposites.get(bp_a) == bp_b:
                tension_key = tuple(sorted([axis_a, axis_b]))
                if tension_key not in seen_tensions:
                    seen_tensions.add(tension_key)
                    result.axis_tensions.append({
                        "axis_a": axis_a,
                        "axis_b": axis_b,
                        "root_a": root_a,
                        "root_b": root_b,
                        "pole_a": bp_a,
                        "pole_b": bp_b,
                    })

    # Dominant cross-axis root: the root with most axis agreement
    if result.root_agreement:
        best_root = max(result.root_agreement.items(), key=lambda x: len(x[1]))
        result.dominant_cross_root = best_root[0]

    # Dominant cross-axis element
    if result.element_agreement:
        best_elem = max(result.element_agreement.items(), key=lambda x: len(x[1]))
        result.dominant_cross_element = best_elem[0]

    # Agreement score: fraction of active axes that share a root or element
    if active_axes:
        agreeing = set()
        for axes in result.root_agreement.values():
            agreeing.update(axes)
        for axes in result.element_agreement.values():
            agreeing.update(axes)
        result.agreement_score = round(len(agreeing) / len(active_axes), 3)

    return result


def resonance_to_dict(res: ResonanceResult) -> dict:
    """Convert ResonanceResult to JSON-serializable dict."""
    return asdict(res)


def main():
    """CLI entry point."""
    input_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ENGINE, "axis_reduction.json")

    with open(input_path) as f:
        axis_signals = json.load(f)

    res = synthesize_across_axes(axis_signals)

    print("Inter-Axis Resonance:")
    print("=" * 60)
    if res.root_agreement:
        print(f"  Root agreement:")
        for root, axes in res.root_agreement.items():
            print(f"    Root {root}: {', '.join(axes)}")
    else:
        print("  No root agreement across axes")

    if res.element_agreement:
        print(f"  Element agreement:")
        for elem, axes in res.element_agreement.items():
            print(f"    {elem}: {', '.join(axes)}")
    else:
        print("  No element agreement across axes")

    if res.axis_tensions:
        print(f"  Tensions:")
        for t in res.axis_tensions:
            print(f"    {t['axis_a']} ({t['pole_a']}) vs {t['axis_b']} ({t['pole_b']})")

    print(f"  Agreement score: {res.agreement_score}")
    print(f"  Cross-axis nodes: {len(res.cross_axis_nodes)}")

    out_path = os.path.join(ENGINE, "inter_axis_resonance.json")
    with open(out_path, "w") as f:
        json.dump(resonance_to_dict(res), f, indent=2, ensure_ascii=False)
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
