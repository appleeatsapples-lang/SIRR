#!/usr/bin/env python3
"""Activation Detector — Layer B: tag_overlap thresholds for axis activation state.

Determines whether each axis is ACTIVE, DORMANT, or TRANSITIONAL based on
timing cycle overlap scores. Does NOT vote in convergence.

Thresholds:
  tag_overlap >= 0.6 → ACTIVE
  tag_overlap < 0.3  → DORMANT
  else               → TRANSITIONAL

Returns INDETERMINATE if cyclic axis not wired (expected during bootstrap).
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional


ACTIVE_THRESHOLD = 0.6
DORMANT_THRESHOLD = 0.3


def activation_layer(
    axis_signals: dict,
    combination_data: Optional[dict] = None,
) -> List[dict]:
    """Determine activation state per axis.

    Args:
        axis_signals: Dict of axis_id -> AxisSignal (dict or dataclass)
        combination_data: Optional combination engine result (overlap_score)

    Returns:
        List of dicts with axis_id, state, overlap_score, note
    """
    results = []

    # Check if cyclic axis has data
    cyclic = axis_signals.get("cyclic")
    cyclic_count = 0
    if cyclic:
        cyclic_count = cyclic.get("module_count", 0) if isinstance(cyclic, dict) else cyclic.module_count

    if cyclic_count == 0:
        # Cyclic axis not wired — return INDETERMINATE for all
        for axis_id in axis_signals:
            results.append({
                "axis_id": axis_id,
                "state": "INDETERMINATE",
                "overlap_score": None,
                "note": "Cyclic axis not wired — activation detection requires timing data",
            })
        return results

    # Use combination overlap_score if available
    global_overlap = None
    if combination_data and isinstance(combination_data, dict):
        global_overlap = combination_data.get("overlap_score")

    for axis_id, sig in axis_signals.items():
        if isinstance(sig, dict):
            mod_count = sig.get("module_count", 0)
            timing = sig.get("timing_quality")
        else:
            mod_count = sig.module_count
            timing = sig.timing_quality

        if mod_count == 0:
            results.append({
                "axis_id": axis_id,
                "state": "INACTIVE",
                "overlap_score": None,
                "note": "No modules in axis",
            })
            continue

        # Determine overlap score for this axis
        # Priority: timing_quality > combination overlap > default
        if timing == "EXPANSIVE":
            score = 0.7
        elif timing == "CONTRACTIVE":
            score = 0.2
        elif timing == "TRANSITIONAL":
            score = 0.45
        elif global_overlap is not None:
            score = global_overlap
        else:
            score = 0.5  # Default: TRANSITIONAL

        # Classify
        if score >= ACTIVE_THRESHOLD:
            state = "ACTIVE"
        elif score < DORMANT_THRESHOLD:
            state = "DORMANT"
        else:
            state = "TRANSITIONAL"

        results.append({
            "axis_id": axis_id,
            "state": state,
            "overlap_score": round(score, 3),
            "note": None,
        })

    return results
