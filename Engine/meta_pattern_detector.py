#!/usr/bin/env python3
"""Meta-Pattern Detector — 10 cross-system patterns for Axis 8c (resonance).

Observational layer. Does NOT vote in convergence.
Patterns are structural observations across axes, not predictions.

Common patterns: Triple Gate, Heaven-Calendar Lock, Threshold Birth.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional


def detect_all(
    axis_signals: dict,
    resonance: dict,
    results: Optional[list] = None,
    profile_core: Optional[dict] = None,
) -> List[dict]:
    """Run all 10 meta-pattern detectors.

    Args:
        axis_signals: Dict of axis_id -> AxisSignal (dict)
        resonance: ResonanceResult (dict) from inter_axis_synthesizer
        results: Raw module results list (for deep inspection)
        profile_core: Core profile data (dob, life_path, etc.)

    Returns:
        List of dicts: pattern_id, name, fired, evidence, note
    """
    patterns = [
        _triple_gate(axis_signals, resonance),
        _echoed_name(axis_signals, resonance),
        _heaven_calendar_lock(axis_signals, resonance),
        _missing_fifth(axis_signals),
        _dominant_current(axis_signals, resonance),
        _split_crown(axis_signals, resonance),
        _catalyst_crown(axis_signals, resonance),
        _silent_core(axis_signals),
        _threshold_birth(profile_core),
        _outlier_witness(axis_signals, resonance),
    ]
    return patterns


def _get_dominant_root(sig: dict) -> Optional[int]:
    if isinstance(sig, dict):
        return sig.get("dominant_root")
    return getattr(sig, "dominant_root", None)


def _get_dominant_element(sig: dict) -> Optional[str]:
    if isinstance(sig, dict):
        return sig.get("dominant_element")
    return getattr(sig, "dominant_element", None)


def _get_module_count(sig: dict) -> int:
    if isinstance(sig, dict):
        return sig.get("module_count", 0)
    return getattr(sig, "module_count", 0)


def _get_root_votes(sig) -> dict:
    if isinstance(sig, dict):
        return sig.get("root_votes", {})
    return getattr(sig, "root_votes", {})


def _vote_margin(root_votes: dict, dominant) -> int:
    """Return votes(dominant) - votes(second_place). 0 if no second place."""
    if dominant is None or not root_votes:
        return 0
    top = root_votes.get(dominant, 0)
    others = [v for k, v in root_votes.items() if k != dominant]
    second = max(others, default=0)
    return top - second


# ── Pattern 1: Triple Gate ──
def _triple_gate(axis_signals: dict, resonance: dict) -> dict:
    """3+ axes share the same dominant root.

    Includes a ``strength`` field: how many axes agree on the strongest root.
    This distinguishes a bare 3/7 from a near-total 6/7.
    """
    root_agreement = resonance.get("root_agreement", {})
    best_root = None
    best_axes: list = []
    for root, axes in root_agreement.items():
        if len(axes) > len(best_axes):
            best_root = root
            best_axes = axes

    if best_root is not None and len(best_axes) >= 3:
        total_active = sum(1 for sig in axis_signals.values()
                          if _get_module_count(sig) > 0)
        return {
            "pattern_id": "triple_gate",
            "name": "Triple Gate",
            "fired": True,
            "strength": len(best_axes),
            "total_axes": total_active,
            "evidence": f"Root {best_root} dominant in {len(best_axes)}/{total_active} axes: {', '.join(best_axes)}",
            "note": "Three or more axes converge on the same root number",
        }
    return {
        "pattern_id": "triple_gate",
        "name": "Triple Gate",
        "fired": False,
        "strength": 0,
        "total_axes": sum(1 for sig in axis_signals.values()
                         if _get_module_count(sig) > 0),
        "evidence": None,
        "note": None,
    }


# ── Pattern 2: Echoed Name ──
def _echoed_name(axis_signals: dict, resonance: dict) -> dict:
    """Name axis dominant root matches digit axis dominant root."""
    name_sig = axis_signals.get("name", {})
    digit_sig = axis_signals.get("digit", {})
    name_root = _get_dominant_root(name_sig)
    digit_root = _get_dominant_root(digit_sig)

    if name_root is not None and digit_root is not None and name_root == digit_root:
        return {
            "pattern_id": "echoed_name",
            "name": "Echoed Name",
            "fired": True,
            "evidence": f"Name and digit axes share root {name_root}",
            "note": "Name-derived and birth-derived computations agree on the same root",
        }
    return {
        "pattern_id": "echoed_name",
        "name": "Echoed Name",
        "fired": False,
        "evidence": None,
        "note": None,
    }


# ── Pattern 3: Heaven-Calendar Lock ──
def _heaven_calendar_lock(axis_signals: dict, resonance: dict) -> dict:
    """Sky axis and calendar axis share dominant element or root."""
    sky = axis_signals.get("sky", {})
    cal = axis_signals.get("calendar", {})

    sky_root = _get_dominant_root(sky)
    cal_root = _get_dominant_root(cal)
    sky_elem = _get_dominant_element(sky)
    cal_elem = _get_dominant_element(cal)

    matches = []
    if sky_root is not None and cal_root is not None and sky_root == cal_root:
        matches.append(f"root {sky_root}")
    if sky_elem is not None and cal_elem is not None and sky_elem == cal_elem:
        matches.append(f"element {sky_elem}")

    if matches:
        return {
            "pattern_id": "heaven_calendar_lock",
            "name": "Heaven-Calendar Lock",
            "fired": True,
            "evidence": f"Sky and calendar axes share {', '.join(matches)}",
            "note": "Astronomical and calendar-based systems agree",
        }
    return {
        "pattern_id": "heaven_calendar_lock",
        "name": "Heaven-Calendar Lock",
        "fired": False,
        "evidence": None,
        "note": None,
    }


# ── Pattern 4: Missing Fifth ──
def _missing_fifth(axis_signals: dict) -> dict:
    """An element present in 4+ axes but absent from one key axis."""
    from collections import Counter
    elem_presence = Counter()
    active_axes = []

    for axis_id, sig in axis_signals.items():
        if _get_module_count(sig) == 0:
            continue
        active_axes.append(axis_id)
        elem = _get_dominant_element(sig)
        if elem:
            elem_presence[elem] += 1

    for elem, count in elem_presence.items():
        if count >= 4:
            missing_from = [a for a in active_axes
                           if _get_dominant_element(axis_signals.get(a, {})) != elem
                           and _get_module_count(axis_signals.get(a, {})) > 0]
            if missing_from:
                return {
                    "pattern_id": "missing_fifth",
                    "name": "Missing Fifth",
                    "fired": True,
                    "evidence": f"{elem} in {count} axes but absent from {', '.join(missing_from[:3])}",
                    "note": "One element dominates most axes but is notably absent from others",
                }
    return {
        "pattern_id": "missing_fifth",
        "name": "Missing Fifth",
        "fired": False,
        "evidence": None,
        "note": None,
    }


# ── Pattern 5: Dominant Current ──
def _dominant_current(axis_signals: dict, resonance: dict) -> dict:
    """One root appears in 5+ axes (overwhelming dominance)."""
    root_agreement = resonance.get("root_agreement", {})
    for root, axes in root_agreement.items():
        if len(axes) >= 5:
            return {
                "pattern_id": "dominant_current",
                "name": "Dominant Current",
                "fired": True,
                "evidence": f"Root {root} dominates {len(axes)} axes",
                "note": "Single root overwhelms the entire chart — monothematic signal",
            }
    return {
        "pattern_id": "dominant_current",
        "name": "Dominant Current",
        "fired": False,
        "evidence": None,
        "note": None,
    }


# ── Pattern 6: Split Crown ──
def _split_crown(axis_signals: dict, resonance: dict) -> dict:
    """Two roots each dominate 3+ axes (competing signals)."""
    root_agreement = resonance.get("root_agreement", {})
    strong_roots = [(r, a) for r, a in root_agreement.items() if len(a) >= 3]
    if len(strong_roots) >= 2:
        return {
            "pattern_id": "split_crown",
            "name": "Split Crown",
            "fired": True,
            "evidence": f"Roots {strong_roots[0][0]} and {strong_roots[1][0]} each dominate 3+ axes",
            "note": "Two competing root signals create internal dialectic",
        }
    return {
        "pattern_id": "split_crown",
        "name": "Split Crown",
        "fired": False,
        "evidence": None,
        "note": None,
    }


# ── Pattern 7: Catalyst Crown ──
def _catalyst_crown(axis_signals: dict, resonance: dict) -> dict:
    """A master number (11, 22, 33) appears as dominant root in any axis."""
    master_numbers = {11, 22, 33}
    for axis_id, sig in axis_signals.items():
        root = _get_dominant_root(sig)
        if root in master_numbers:
            return {
                "pattern_id": "catalyst_crown",
                "name": "Catalyst Crown",
                "fired": True,
                "evidence": f"Master number {root} dominates {axis_id} axis",
                "note": "Master number as axis dominant signals heightened potential",
            }
    return {
        "pattern_id": "catalyst_crown",
        "name": "Catalyst Crown",
        "fired": False,
        "evidence": None,
        "note": None,
    }


# ── Pattern 8: Silent Core ──
def _silent_core(axis_signals: dict) -> dict:
    """An axis with high module count but no clear dominant root or element."""
    for axis_id, sig in axis_signals.items():
        count = _get_module_count(sig)
        root = _get_dominant_root(sig)
        elem = _get_dominant_element(sig)
        if count >= 10 and root is None and elem is None:
            return {
                "pattern_id": "silent_core",
                "name": "Silent Core",
                "fired": True,
                "evidence": f"{axis_id} has {count} modules but no dominant root or element",
                "note": "High activity but no convergent signal — diffuse energy",
            }
    return {
        "pattern_id": "silent_core",
        "name": "Silent Core",
        "fired": False,
        "evidence": None,
        "note": None,
    }


# ── Pattern 9: Threshold Birth ──
def _threshold_birth(profile_core: Optional[dict]) -> dict:
    """Birth on a cusp date (day 19-23 of month) or equinox/solstice proximity."""
    if not profile_core:
        return {
            "pattern_id": "threshold_birth",
            "name": "Threshold Birth",
            "fired": False,
            "evidence": None,
            "note": "No profile data available",
        }

    day = profile_core.get("day")
    month = profile_core.get("month")

    if day is None:
        return {
            "pattern_id": "threshold_birth",
            "name": "Threshold Birth",
            "fired": False,
            "evidence": None,
            "note": None,
        }

    # Cusp days: 19-23 of any month
    is_cusp = 19 <= day <= 23

    # Equinox/solstice proximity (±2 days)
    equinox_dates = [(3, 20), (6, 21), (9, 22), (12, 21)]
    is_threshold = False
    for eq_m, eq_d in equinox_dates:
        if month == eq_m and abs(day - eq_d) <= 2:
            is_threshold = True
            break

    if is_cusp or is_threshold:
        reasons = []
        if is_cusp:
            reasons.append(f"day {day} is a zodiac cusp date")
        if is_threshold:
            reasons.append("near equinox/solstice")
        return {
            "pattern_id": "threshold_birth",
            "name": "Threshold Birth",
            "fired": True,
            "evidence": "; ".join(reasons),
            "note": "Birth at a transitional boundary — liminal qualities amplified",
        }

    return {
        "pattern_id": "threshold_birth",
        "name": "Threshold Birth",
        "fired": False,
        "evidence": None,
        "note": None,
    }


# ── Pattern 10: Outlier Witness ──
_OUTLIER_MIN_MODULES = 5   # axis must have ≥5 modules to qualify
_OUTLIER_MIN_MARGIN  = 3   # dominant root must lead second-place by ≥3 votes


def _outlier_witness(axis_signals: dict, resonance: dict) -> dict:
    """One axis has a dominant root that no other axis shares, and holds
    that root with a clear vote margin (≥ _OUTLIER_MIN_MARGIN).

    Both gates together prevent trivial misfires:
    - module gate: axis must have ≥5 contributing modules
    - margin gate: dominant root must lead second-place by ≥3 votes
    An axis that barely plurality-selects a root isn't confidently disagreeing.
    """
    root_agreement = resonance.get("root_agreement", {})
    agreed_roots = set()
    for root, axes in root_agreement.items():
        agreed_roots.add(int(root) if isinstance(root, str) else root)

    for axis_id, sig in axis_signals.items():
        mod_count = _get_module_count(sig)
        if mod_count < _OUTLIER_MIN_MODULES:
            continue
        root = _get_dominant_root(sig)
        if root is None or root in agreed_roots:
            continue
        margin = _vote_margin(_get_root_votes(sig), root)
        if margin < _OUTLIER_MIN_MARGIN:
            continue
        return {
            "pattern_id": "outlier_witness",
            "name": "Outlier Witness",
            "fired": True,
            "evidence": (f"{axis_id} axis ({mod_count} modules) has unique root {root} "
                         f"not shared by any other axis (margin +{margin})"),
            "note": "Counterpoint signal — this axis speaks independently",
        }
    return {
        "pattern_id": "outlier_witness",
        "name": "Outlier Witness",
        "fired": False,
        "evidence": None,
        "note": None,
    }
