"""Minimum Viable Signature — Irreducible Profile Facts — COMPUTED_STRICT (comparative)
Distills the entire engine output to the 5 irreducible structural facts
about this profile — what cannot be removed without losing identity.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    results = kwargs.get("all_results", [])

    facts = []

    # Fact 1: Dominant numerical root (from convergence)
    dominant_root = None
    dominant_root_count = 0
    for r in results:
        if r.id == "hermetic_alignment":
            dominant_root = r.data.get("dominant_value", 0)
            dominant_root_count = r.data.get("dominant_count", 0)
            break
    if dominant_root:
        facts.append({
            "rank": 1,
            "fact": "dominant_root",
            "value": dominant_root,
            "support": dominant_root_count,
            "source": "hermetic_alignment",
            "statement": f"Root {dominant_root} dominates across {dominant_root_count} axes",
        })

    # Fact 2: Structural voice (active/passive)
    for r in results:
        if r.id == "arabic_morphology":
            voice = r.data.get("dominant_voice", "unknown")
            facts.append({
                "rank": 2,
                "fact": "structural_voice",
                "value": voice,
                "source": "arabic_morphology",
                "statement": f"Name is structurally {voice} — identity is {voice}ly constructed",
            })
            break

    # Fact 3: Dominant semantic field
    for r in results:
        if r.id == "name_semantics":
            cluster = r.data.get("dominant_cluster", "none")
            ratio = r.data.get("dominant_cluster_ratio", 0)
            facts.append({
                "rank": 3,
                "fact": "semantic_center",
                "value": cluster,
                "ratio": ratio,
                "source": "name_semantics",
                "statement": f"Semantic center: {cluster} ({ratio}% of name)",
            })
            break

    # Fact 4: Barzakh classification
    for r in results:
        if r.id == "barzakh_coefficient":
            classification = r.data.get("classification", "unknown")
            coefficient = r.data.get("coefficient", 0)
            facts.append({
                "rank": 4,
                "fact": "structural_balance",
                "value": classification,
                "coefficient": coefficient,
                "source": "barzakh_coefficient",
                "statement": f"Structural balance: {classification} (coefficient {coefficient})",
            })
            break

    # Fact 5: Void geometry
    for r in results:
        if r.id == "void_matrix":
            void_center = r.data.get("void_center", False)
            total_voids = r.data.get("total_voids", 0)
            facts.append({
                "rank": 5,
                "fact": "void_geometry",
                "void_center": void_center,
                "total_voids": total_voids,
                "source": "void_matrix",
                "statement": f"Void geometry: {'center absent' if void_center else 'center present'}, {total_voids} total voids",
            })
            break

    return SystemResult(
        id="minimum_viable_signature",
        name="Minimum Viable Signature (التوقيع الأدنى)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "comparative",
            "facts": facts,
            "fact_count": len(facts),
            "signature_string": " | ".join(f["statement"] for f in facts),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Structural distillation — the 5 irreducible facts of a SIRR profile"],
        question="Q6_SYNTHESIS"
    )
