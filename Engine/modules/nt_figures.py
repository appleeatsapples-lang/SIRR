"""NT Figures — pattern match (not lineage) — LOOKUP_FIXED

Scholarship fidelity (§4.5 rules 3 + 5):
  Early-Christian isopsephy (Revelation 13:18 tradition) names specific
  numbers but does NOT compare personal names to apostolic figures.
  This module is SIRR pattern-detection — numeric-signature resemblance
  against 34 NT figure isopsephies — not a continuation of any Christian
  gematria tradition or claim of spiritual inheritance.

34 New Testament figures with Greek Isopsephy.
Computation locked: Claude = DeepSeek across all 34 figures, 0 discrepancies.
Pipeline: 6-model orchestration (Gemini, ChatGPT, Grok, DeepSeek, Kimi).
Constitutional mode: mirror_not_crystal_ball.
"""
from __future__ import annotations
import json
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult

_DATA_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "scripture"

ISOPSEPHY = {
    "α": 1, "β": 2, "γ": 3, "δ": 4, "ε": 5,
    "ζ": 7, "η": 8, "θ": 9, "ι": 10, "κ": 20,
    "λ": 30, "μ": 40, "ν": 50, "ξ": 60, "ο": 70,
    "π": 80, "ρ": 100, "σ": 200, "ς": 200, "τ": 300,
    "υ": 400, "φ": 500, "χ": 600, "ψ": 700, "ω": 800,
}

BLOCKED_PHRASES = [
    "proves divine code", "hidden encoding", "destined", "predicts",
    "fate", "guarantees", "cosmic confirmation", "hidden fate",
    "prophetically encoded", "mathematically proves", "evil number",
    "holy number proves", "moral superiority by value",
    "lower number means corruption",
]


def _reduce(n: int) -> int:
    """Reduce to single digit."""
    x = abs(n)
    while x > 9:
        x = sum(int(d) for d in str(x))
    return x


def _reduction_chain(n: int) -> str:
    """Build reduction chain string."""
    x = abs(n)
    if x <= 9:
        return str(x)
    steps = []
    while x > 9:
        x = sum(int(d) for d in str(x))
        steps.append(str(x))
    return "→".join(steps)


def _passes_through_11(n: int) -> bool:
    """Check if reduction chain passes through 11."""
    x = abs(n)
    while x > 9:
        x = sum(int(d) for d in str(x))
        if x == 11:
            return True
    return False


def _load_json(filename: str):
    return json.loads((_DATA_DIR / filename).read_text(encoding="utf-8"))


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    """NT Figures module.
    Certainty: LOOKUP_FIXED
    feeds_convergence: False
    feeds_synthesis: True
    """
    figures = _load_json("nt_figures_locked.json")

    all_records = []
    grand_sum = 0
    final_dist = {}

    for fig in figures:
        name_gr = fig["name_gr"]
        isopsephy = fig["isopsephy"]
        chain = fig["chain"]
        final = fig["final"]
        master = fig["master"]

        grand_sum += isopsephy

        final_dist.setdefault(final, []).append(name_gr)

        record = {
            "index": fig["index"],
            "name_gr": name_gr,
            "name_en": fig["name_en"],
            "isopsephy_value": isopsephy,
            "reduction_chain": chain,
            "final_value": final,
            "master_11": master,
            "passes_through_11": _passes_through_11(isopsephy),
            "convergence_tags": ["LOCKED_COMPUTATION", "GREEK_ISOPSEPHY"],
        }
        all_records.append(record)

    # Master 11 figures
    master_11_figures = [r for r in all_records if r["master_11"]]

    # Historically attested
    jesus = next(r for r in all_records if r["name_en"] == "Jesus")
    historically_attested = [{
        "figure": "Ἰησοῦς",
        "value": 888,
        "reduced": 6,
        "source": "Sibylline Oracles Book 1:324-331 + Irenaeus, Adv. Haer. 1.15.5",
        "tag": "HISTORICALLY_ATTESTED",
    }]

    # Subject root match
    subject_matches = []
    if profile.arabic:
        from modules.quranic_figures import _compute_abjad, _reduce as abjad_reduce
        subj_abjad = _compute_abjad(profile.arabic)
        subj_root = abjad_reduce(subj_abjad)
        for rec in all_records:
            if rec["final_value"] == subj_root:
                subject_matches.append({
                    "name_gr": rec["name_gr"],
                    "name_en": rec["name_en"],
                    "shared_root": subj_root,
                })

    return SystemResult(
        id="nt_figures",
        name="NT Figures — pattern match (not lineage)",
        certainty="LOOKUP_FIXED",
        data={
            "figures": all_records,
            "figure_count": len(all_records),
            "grand_sum": grand_sum,
            "grand_sum_reduced": _reduce(grand_sum),
            "final_value_distribution": {str(k): v for k, v in sorted(final_dist.items())},
            "master_11_figures": [
                {"name_gr": r["name_gr"], "name_en": r["name_en"], "isopsephy": r["isopsephy_value"]}
                for r in master_11_figures
            ],
            "master_11_count": len(master_11_figures),
            "historically_attested": historically_attested,
            "subject_root_matches": subject_matches,
            "constitutional_mode": "mirror_not_crystal_ball",
            # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
            "scholarship_fidelity": "CLASSICAL_METHOD_MODERN_APPLICATION",
            "scholarship_note": 'Pattern-detection, NOT continuation of Christian gematria tradition. Resemblance is mathematics, not lineage.',
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "New Testament (Greek) — 34 named figures",
            "Greek Isopsephy — standard letter-value table (α=1 through ω=800)",
            "No value 6 — digamma absent from koine Greek; ζ=7",
            "Computation locked: Claude = DeepSeek — 0 discrepancies across 34 figures",
            "Ἰησοῦς = 888: HISTORICALLY_ATTESTED (Sibylline Oracles + Irenaeus)",
            "SOURCE_TIER: A — Greek text primary, computation verified by 2 independent models",
        ],
        question="Q1_IDENTITY",
    )
