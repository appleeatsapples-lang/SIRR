"""Execution Pattern Analysis — Void/Expression Structural Compound — COMPUTED_STRICT (comparative)
Analyzes how multiple structural factors compound at the private→public threshold:
void center (missing 5), missing execution digits (4,7,8), Expression=11, Root 1.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    results = kwargs.get("all_results", [])

    # Gather structural factors
    lo_shu_missing = []
    void_center = False
    for r in results:
        if r.id == "void_matrix":
            lo_shu_missing = r.data.get("lo_shu_missing", [])
            void_center = r.data.get("void_center", False)
            break

    expression = profile.expression or 0
    life_path = profile.life_path or 0
    abjad_root = 0
    for r in results:
        if r.id == "abjad_kabir":
            abjad_root = r.data.get("root", 0)
            break

    # Dominant voice
    dominant_voice = "unknown"
    for r in results:
        if r.id == "arabic_morphology":
            dominant_voice = r.data.get("dominant_voice", "unknown")
            break

    # Structural factors that compound
    factors = []

    if void_center:
        factors.append({
            "factor": "void_center",
            "description": "Missing 5 in Lo Shu = no center digit",
            "structural_note": "Center absent — identity constructed from edges",
        })

    # Missing execution digits
    execution_missing = [d for d in lo_shu_missing if d in (4, 7, 8)]
    if execution_missing:
        factors.append({
            "factor": "missing_execution_digits",
            "digits": execution_missing,
            "description": f"Missing {execution_missing} — practical execution gaps",
        })

    if expression in (11, 22, 33):
        factors.append({
            "factor": "master_expression",
            "value": expression,
            "description": f"Expression {expression} — master number amplifies private→public gap",
        })

    if dominant_voice == "passive":
        factors.append({
            "factor": "passive_voice_dominant",
            "description": "Name structurally passive — identity received, not initiated",
        })

    # Compound score: how many factors stack
    compound_count = len(factors)

    # Classification
    if compound_count >= 4:
        pattern = "heavily_compounded"
    elif compound_count >= 3:
        pattern = "moderately_compounded"
    elif compound_count >= 2:
        pattern = "lightly_compounded"
    else:
        pattern = "minimal"

    return SystemResult(
        id="execution_pattern_analysis",
        name="Execution Pattern Analysis (تحليل نمط التنفيذ)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "comparative",
            "factors": factors,
            "compound_count": compound_count,
            "pattern": pattern,
            "void_center": void_center,
            "lo_shu_missing": lo_shu_missing,
            "expression": expression,
            "life_path": life_path,
            "abjad_root": abjad_root,
            "dominant_voice": dominant_voice,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Structural compounding analysis — void/expression/voice interaction"],
        question="Q6_SYNTHESIS"
    )
