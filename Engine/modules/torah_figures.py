"""Torah Figures — pattern match (not lineage) — LOOKUP_FIXED

Scholarship fidelity (§4.5 rules 3 + 5):
  Classical kabbalistic practice does NOT compare a subject to Torah
  figures via personal-name gematria. This module is SIRR
  pattern-detection — numeric-signature resemblance against 68 named
  Torah figures — not a continuation of kabbalistic practice or claim
  of inherited identity.

68 named Torah figures with Hebrew Gematria (Mispar Gadol / Standard).
Standard (non-sofit) values throughout — constitutional ruling.
Computation locked: Claude = DeepSeek across all 68 figures, 0 discrepancies.
Pipeline: 6-model orchestration (Gemini, ChatGPT, Grok, DeepSeek, Kimi).
Constitutional mode: mirror_not_crystal_ball.
"""
from __future__ import annotations
import json
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult

_DATA_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "scripture"

GEMATRIA_STANDARD = {
    "א": 1,  "ב": 2,  "ג": 3,  "ד": 4,  "ה": 5,
    "ו": 6,  "ז": 7,  "ח": 8,  "ט": 9,  "י": 10,
    "כ": 20, "ל": 30, "מ": 40, "נ": 50, "ס": 60,
    "ע": 70, "פ": 80, "צ": 90, "ק": 100, "ר": 200,
    "ש": 300, "ת": 400,
    # Sofit letter forms → STANDARD values (never sofit values)
    "ך": 20, "ם": 40, "ן": 50, "ף": 80, "ץ": 90,
}

BLOCKED_PHRASES = [
    "proves divine code", "hidden encoding", "destined", "predicts",
    "fate", "guarantees", "cosmic confirmation", "hidden fate",
    "prophetically encoded", "mathematically proves", "evil number",
    "holy number proves", "moral superiority by value",
    "lower number means corruption",
]

# Within-Torah exact matches (Source Tier A)
WITHIN_TORAH_MATCHES = [
    {"figures": ["יוסף", "יחזקאל"], "shared_value": 156, "source": "Zohar — both connected to Tzion", "tier": "A"},
    {"figures": ["יצחק", "הגר"], "shared_value": 208, "source": "Baal HaTurim — parallel destinies", "tier": "A"},
    {"figures": ["יהושע", "ציפורה"], "shared_value": 391, "source": None, "tier": "B"},
]


def _reduce(n: int) -> int:
    """Reduce to single digit (no master number retention for gematria)."""
    x = abs(n)
    while x > 9:
        x = sum(int(d) for d in str(x))
    return x


def _reduction_chain(n: int) -> str:
    """Build reduction chain string, e.g. '14→5' or '9'."""
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


def _compute_gematria(name_he: str) -> int:
    """Sum gematria standard values (spaces ignored)."""
    return sum(GEMATRIA_STANDARD.get(ch, 0) for ch in name_he)


def _letter_breakdown(name_he: str) -> list:
    """Break name into (letter, value) pairs."""
    result = []
    for ch in name_he:
        if ch in GEMATRIA_STANDARD:
            result.append({"letter": ch, "value": GEMATRIA_STANDARD[ch]})
    return result


def _load_json(filename: str):
    return json.loads((_DATA_DIR / filename).read_text(encoding="utf-8"))


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    """Torah Figures module.
    Certainty: LOOKUP_FIXED
    feeds_convergence: False
    feeds_synthesis: True
    """
    figures = _load_json("torah_figures_locked.json")

    all_records = []
    grand_sum = 0
    final_dist = {}

    for fig in figures:
        name_he = fig["name_he"]
        gematria = fig["gematria"]
        chain = fig["chain"]
        final = fig["final"]
        master = fig["master"]
        book = fig["book"]

        grand_sum += gematria

        final_dist.setdefault(final, []).append(name_he)

        record = {
            "index": fig["index"],
            "name_he": name_he,
            "name_en": fig["name_en"],
            "book": book,
            "gematria_value": gematria,
            "letter_breakdown": _letter_breakdown(name_he),
            "reduction_chain": chain,
            "final_value": final,
            "master_11": master,
            "passes_through_11": _passes_through_11(gematria),
            "convergence_tags": ["LOCKED_COMPUTATION", "STANDARD_GEMATRIA_ONLY"],
        }
        all_records.append(record)

    # Master 11 figures
    master_11_figures = [r for r in all_records if r["master_11"]]

    # Within-Torah exact matches
    within_matches = []
    name_to_gem = {fig["name_he"]: fig["gematria"] for fig in figures}
    for match in WITHIN_TORAH_MATCHES:
        within_matches.append({
            "figures": match["figures"],
            "figures_en": [
                next(f["name_en"] for f in figures if f["name_he"] == n)
                for n in match["figures"]
            ],
            "shared_value": match["shared_value"],
            "source": match["source"],
            "source_tier": match["tier"],
            "verified": all(name_to_gem.get(n) == match["shared_value"] for n in match["figures"]),
        })

    # Subject root match
    subject_matches = []
    if profile.arabic:
        from modules.quranic_figures import _compute_abjad, _reduce as abjad_reduce
        subj_abjad = _compute_abjad(profile.arabic)
        subj_root = abjad_reduce(subj_abjad)
        for rec in all_records:
            if rec["final_value"] == subj_root:
                subject_matches.append({
                    "name_he": rec["name_he"],
                    "name_en": rec["name_en"],
                    "shared_root": subj_root,
                })

    return SystemResult(
        id="torah_figures",
        name="Torah Figures — pattern match (not lineage)",
        certainty="LOOKUP_FIXED",
        data={
            "figures": all_records,
            "figure_count": len(all_records),
            "grand_sum": grand_sum,
            "grand_sum_reduced": _reduce(grand_sum),
            "final_value_distribution": {str(k): v for k, v in sorted(final_dist.items())},
            "master_11_figures": [
                {"name_he": r["name_he"], "name_en": r["name_en"], "gematria": r["gematria_value"]}
                for r in master_11_figures
            ],
            "master_11_count": len(master_11_figures),
            "within_torah_matches": within_matches,
            "subject_root_matches": subject_matches,
            "sofit_ruling": "NEVER_USED — standard (non-sofit) values only, constitutional for SIRR",
            "constitutional_mode": "mirror_not_crystal_ball",
            # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
            "scholarship_fidelity": "CLASSICAL_METHOD_MODERN_APPLICATION",
            "scholarship_note": 'Pattern-detection, NOT continuation of kabbalistic practice. Resemblance is mathematics, not lineage.',
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Hebrew Bible (Tanakh) — 68 named figures",
            "Gematria Standard (Mispar Gadol) — non-sofit values only",
            "Computation locked: Claude = DeepSeek — 0 discrepancies across 68 figures",
            "Within-Torah matches: Zohar (Joseph=Ezekiel=156), Baal HaTurim (Isaac=Hagar=208)",
            "SOURCE_TIER: A — Hebrew text primary, computation verified by 2 independent models",
        ],
        question="Q1_IDENTITY",
    )
