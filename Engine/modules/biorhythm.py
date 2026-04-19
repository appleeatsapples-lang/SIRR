"""Biorhythm — COMPUTED_STRICT"""
from __future__ import annotations
import math
from sirr_core.types import InputProfile, SystemResult

def _level(x: float) -> str:
    if x > 30: return "HIGH"
    if x < -30: return "LOW"
    return "NEUTRAL"

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    days = (profile.today - profile.dob).days
    p = math.sin(2 * math.pi * days / 23) * 100
    e = math.sin(2 * math.pi * days / 28) * 100
    i = math.sin(2 * math.pi * days / 33) * 100

    # Derive period quality from physical + emotional composite
    if p > 30 and e > 30:
        pq = "benefic"
    elif p < -30 and e < -30:
        pq = "malefic"
    elif p < -30 or e < -30:
        pq = "challenging"
    elif p > 30 or e > 30:
        pq = "mixed"
    else:
        pq = "neutral"

    return SystemResult(
        id="biorhythm",
        name="Biorhythm (23/28/33)",
        certainty="COMPUTED_STRICT",
        data={
            "days_alive": days,
            "physical_pct": round(p, 1), "physical_level": _level(p),
            "emotional_pct": round(e, 1), "emotional_level": _level(e),
            "intellectual_pct": round(i, 1), "intellectual_level": _level(i),
            "cycle_pos": f"P:{days%23}/23  E:{days%28}/28  I:{days%33}/33",
            "period_quality": pq,
        },
        interpretation="Strict sine-wave model. Treat as timing-flavor, not fate.",
        constants_version=constants["version"],
        references=["Standard biorhythm sine cycles: 23/28/33 days",
                    "SOURCE_TIER:C — Proposed by Wilhelm Fliess (late 19th c.). No ancient or classical cycle backing."],
        question="Q4_TIMING"
    )
