"""Cross-Scripture Intersection — pattern (not convergence) — LOOKUP_FIXED

Scholarship fidelity (§4.5 rules 2 + 3 + 5):
  Hebrew-Arabic cognate matches between scripture-figure gematria are
  tautological (shared proto-Semitic letter roots produce identical
  values by construction, not by historical agreement). Only non-cognate
  or Greek matches carry potential convergence weight — and even those
  are PATTERN detection, not tradition-agreement claims.

  Display name now reads "pattern (not convergence)" to prevent buyers
  from reading the output as cross-tradition sacred correspondence.

Cross-tradition analysis across Quranic (Abjad), Torah (Hebrew Gematria),
and NT (Greek Isopsephy) figure corpora. Grok ruling surfaced in display.
Constitutional mode: mirror_not_crystal_ball.
"""
from __future__ import annotations
import json
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult

_DATA_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "scripture"

BLOCKED_PHRASES = [
    "proves divine code", "hidden encoding", "destined", "predicts",
    "fate", "guarantees", "cosmic confirmation", "hidden fate",
    "prophetically encoded", "mathematically proves", "evil number",
    "holy number proves", "moral superiority by value",
    "lower number means corruption",
]


def _reduce(n: int) -> int:
    x = abs(n)
    while x > 9:
        x = sum(int(d) for d in str(x))
    return x


def _passes_through_11(n: int) -> bool:
    x = abs(n)
    while x > 9:
        x = sum(int(d) for d in str(x))
        if x == 11:
            return True
    return False


def _load_json(filename: str):
    return json.loads((_DATA_DIR / filename).read_text(encoding="utf-8"))


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    """Cross-Scripture module.
    Certainty: LOOKUP_FIXED
    feeds_convergence: False
    feeds_synthesis: True
    """
    findings = _load_json("cross_scripture_findings.json")
    torah = _load_json("torah_figures_locked.json")
    nt = _load_json("nt_figures_locked.json")

    # Cross-tradition reduced matches
    cross_matches = findings["cross_tradition_reduced_matches"]

    # Within-Torah matches
    within_matches = findings["within_tradition_matches"]

    # Master 11 cross-tradition chain
    master_11 = findings["master_11_cross_tradition"]

    # Count master 11 per tradition
    torah_master_11 = [f for f in torah if f["master"]]
    nt_master_11 = [f for f in nt if f["master"]]

    # Aggregate stats
    torah_count = len(torah)
    nt_count = len(nt)
    quranic_count = 46  # from quranic_figures module

    # Final value distribution across all three corpora
    combined_dist = {}
    for f in torah:
        combined_dist.setdefault(f["final"], {"torah": 0, "nt": 0, "quranic": 0})
        combined_dist[f["final"]]["torah"] += 1
    for f in nt:
        combined_dist.setdefault(f["final"], {"torah": 0, "nt": 0, "quranic": 0})
        combined_dist[f["final"]]["nt"] += 1

    # Subject root match across all three traditions
    subject_cross_matches = []
    if profile.arabic:
        from modules.quranic_figures import _compute_abjad, _reduce as abjad_reduce
        subj_abjad = _compute_abjad(profile.arabic)
        subj_root = abjad_reduce(subj_abjad)

        torah_matches = [f["name_en"] for f in torah if f["final"] == subj_root]
        nt_matches = [f["name_en"] for f in nt if f["final"] == subj_root]

        subject_cross_matches = {
            "subject_root": subj_root,
            "torah_matches": torah_matches,
            "torah_match_count": len(torah_matches),
            "nt_matches": nt_matches,
            "nt_match_count": len(nt_matches),
        }

    return SystemResult(
        id="cross_scripture",
        name="Cross-Scripture Intersection — pattern (not convergence)",
        certainty="LOOKUP_FIXED",
        data={
            "cross_tradition_reduced_matches": cross_matches,
            "cross_match_count": len(cross_matches),
            "within_tradition_matches": within_matches,
            "within_match_count": len(within_matches),
            "master_11_cross_tradition": master_11,
            "master_11_total": master_11["total_count"],
            "historically_attested": findings["historically_attested"],
            "retired_findings": findings["retired_findings"],
            "corpus_stats": {
                "torah_figures": torah_count,
                "nt_figures": nt_count,
                "quranic_figures": quranic_count,
                "total": torah_count + nt_count + quranic_count,
            },
            "combined_final_distribution": {
                str(k): v for k, v in sorted(combined_dist.items())
            },
            "subject_cross_matches": subject_cross_matches,
            "grok_ruling": "Hebrew-Arabic cognate matches are tautological (shared proto-Semitic substrate). Only non-cognate or Greek matches carry convergence weight.",
            "constitutional_mode": "mirror_not_crystal_ball",
            # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
            "scholarship_fidelity": "CLASSICAL_METHOD_MODERN_APPLICATION",
            "scholarship_note": 'Hebrew-Arabic cognate matches are tautological (Grok ruling). Only non-cognate/Greek matches carry weight.',
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Cross-tradition analysis: Quranic Abjad × Torah Gematria × NT Isopsephy",
            "Grok ruling: cognate matches tautological, only non-cognate/Greek carry weight",
            "2 cross-tradition reduced matches (Isa/Jesus=6, Musa/Moses=8)",
            "3 within-Torah matches (Joseph=Ezekiel=156, Isaac=Hagar=208, Joshua=Zipporah=391)",
            "Master 11 chain spans all 3 traditions: 5 Arabic + 5 Hebrew + 2 Greek = 12 total",
            "SOURCE_TIER: A — computation verified, cross-tradition independence audited by Grok",
        ],
        question="Q1_IDENTITY",
    )
