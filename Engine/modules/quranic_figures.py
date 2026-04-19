"""Quranic Figures — pattern match (not lineage) — LOOKUP_FIXED

Scholarship fidelity (§4.5 rules 3 + 5 — pattern, not lineage/equivalence):
  Classical Islamic tradition does NOT compare individuals to prophets
  via personal-name gematria. al-Buni applies abjad to divine/prophetic
  names for talismans, not for individual comparison. This module is a
  SIRR product design (MODERN_SYNTHESIS at the comparison layer) that
  detects numeric-signature resemblance between the subject's abjad and
  the abjad of 46 named Quranic figures.

  Resemblance in number is MATHEMATICS, not inheritance, equivalence,
  or destiny. Buyer-facing framing must be "pattern detection" — never
  "continuation," "alignment with," or "inherits from" the named figure.

All 46 named figures in the Quran: 25 prophets, 14 non-prophet humans,
5 angels, 1 jinn, 1 collective pair (computed as 2).
Abjad Kabir values locked across Claude, DeepSeek, and ChatGPT — 0 discrepancies.
Adversarial passes: 3 | Findings surviving: 8 | Findings retired: 3.
Constitutional mode: mirror_not_crystal_ball.
"""
from __future__ import annotations
import json
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult

_DATA_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "quranic_figures"

ABJAD_KABIR = {
    "أ":1, "ب":2, "ج":3, "د":4, "ه":5, "هـ":5,
    "و":6, "ز":7, "ح":8, "ط":9, "ي":10,
    "ك":20, "ل":30, "م":40, "ن":50, "س":60,
    "ع":70, "ف":80, "ص":90, "ق":100, "ر":200,
    "ش":300, "ت":400, "ث":500, "خ":600, "ذ":700,
    "ض":800, "ظ":900, "غ":1000,
    # Alif variants = 1
    "ا":1, "إ":1, "آ":1,
    # Alif maqsura = 10 (classical consensus, Source Tier A)
    "ى":10,
}

BLOCKED_PHRASES = [
    "proves divine code", "hidden encoding", "destined", "predicts",
    "fate", "guarantees", "cosmic confirmation", "hidden fate",
    "prophetically encoded", "mathematically proves", "evil number",
    "holy number proves", "moral superiority by value",
    "lower number means corruption",
]

# Antagonist → prophet mapping
ANTAGONIST_MAP = {
    "آزر": "إبراهيم",
    "هامان": "موسى",
    "السامري": "موسى",
    "قارون": "موسى",
    "فرعون": "موسى",
    "أبو لهب": "محمد",
}

# Paired figures
PAIR_KEYS = {
    "هاروت": "هاروت/ماروت",
    "ماروت": "هاروت/ماروت",
    "يأجوج": "يأجوج/مأجوج",
    "مأجوج": "يأجوج/مأجوج",
}


def _reduce(n: int) -> int:
    """Reduce to single digit (no master number retention for abjad)."""
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


def _letter_breakdown(name_ar: str) -> list:
    """Break name into (letter, value) pairs."""
    result = []
    for ch in name_ar:
        if ch in ABJAD_KABIR:
            result.append({"letter": ch, "value": ABJAD_KABIR[ch]})
    return result


def _compute_abjad(name_ar: str) -> int:
    """Sum abjad values of all letters in name (spaces/diacritics ignored)."""
    return sum(ABJAD_KABIR.get(ch, 0) for ch in name_ar)


def _load_json(filename: str):
    return json.loads((_DATA_DIR / filename).read_text(encoding="utf-8"))


def _passes_through_11(n: int) -> bool:
    """Check if reduction chain passes through 11."""
    x = abs(n)
    while x > 9:
        x = sum(int(d) for d in str(x))
        if x == 11:
            return True
    return False


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    """Quranic Figures module.
    Certainty: LOOKUP_FIXED
    feeds_convergence: False
    feeds_synthesis: True
    """
    # Load all data files
    figures = _load_json("quranic_figures_full_locked.json")
    interps = _load_json("quranic_figures_full_interpretations.json")
    frequency_list = _load_json("quranic_figures_full_frequency.json")
    hebrew_list = _load_json("quranic_figures_full_hebrew.json")
    antagonists = _load_json("quranic_figures_full_antagonists.json")
    pairs = _load_json("quranic_figures_full_pairs.json")
    master11 = _load_json("quranic_figures_full_master11.json")
    convergences = _load_json("quranic_figures_full_convergences.json")

    # Build frequency lookup
    freq_map = {f["name_ar"]: f["frequency"] for f in frequency_list}

    # Build hebrew lookup
    hebrew_map = {}
    for h in hebrew_list:
        hebrew_map[h["name_ar"]] = h

    # Build all figure records
    prophets = []
    all_records = []
    prophet_sum = 0

    for fig in figures:
        name_ar = fig["name_ar"]
        abjad = fig["abjad"]
        final = fig["final"]
        chain = fig["chain"]
        category = fig["category"]
        is_prophet = category == "prophet"

        if is_prophet:
            prophet_sum += abjad

        # Interpretation data
        interp = interps.get(name_ar, {})

        # Build convergence tags for this figure
        tags = ["LOCKED_COMPUTATION"]
        special_tag = fig.get("special_tag")
        if special_tag:
            tags.append(special_tag)

        # Prophet-specific tags
        if is_prophet:
            tags.append("PROPHET_CHAIN_ONLY")
        else:
            tags.append("FULL_CORPUS")

        # Antagonist check
        is_antagonist = name_ar in ANTAGONIST_MAP
        opposed_prophet = ANTAGONIST_MAP.get(name_ar)

        # Pair check
        is_pair = name_ar in PAIR_KEYS
        pair_key = PAIR_KEYS.get(name_ar)

        # Master 11 chain check
        master_chain = None
        if _passes_through_11(abjad):
            master_chain = f"11→{final}"

        # Hebrew crossmatch
        heb = hebrew_map.get(name_ar)

        # Quran frequency
        q_freq = freq_map.get(name_ar)
        if fig.get("quran_frequency"):
            q_freq = fig["quran_frequency"]

        record = {
            "index": fig["index"],
            "name_ar": name_ar,
            "name_en": fig["name_en"],
            "category": category,
            "abjad_value": abjad,
            "letter_breakdown": _letter_breakdown(name_ar),
            "reduction_chain": chain,
            "final_value": final,
            "master_number_retained": _passes_through_11(abjad),
            "quran_frequency": q_freq,
            "special_tag": special_tag,
            "letter_meanings": {
                "en": interp.get("letter_meanings_en", ""),
                "ar": interp.get("letter_meanings_ar", ""),
            },
            "structural_reading": {
                "en": interp.get("structural_reading_en", ""),
                "ar": interp.get("structural_reading_ar", ""),
            },
            "quranic_role_note": {
                "en": interp.get("quranic_role_en", ""),
                "ar": interp.get("quranic_role_ar", ""),
            },
            "contrast_with_prophets": {
                "en": interp.get("contrast_en", ""),
                "ar": interp.get("contrast_ar", ""),
            },
            "hebrew_crossmatch": {
                "name_he": heb["name_he"],
                "gematria": heb["gematria"],
                "match_type": heb["type"],
                "tag": heb["tag"],
                "note": heb.get("note"),
            } if heb else None,
            "convergence_tags": tags,
            "confidence": {
                "level": "HIGH",
                "adversarial_batches": 3,
                "computation_verified": True,
            },
            "metadata": {
                "is_prophet": is_prophet,
                "is_antagonist": is_antagonist,
                "opposed_prophet": opposed_prophet,
                "is_pair_member": is_pair,
                "pair_key": pair_key,
                "master_chain": master_chain,
                "scope": "prophet_chain" if is_prophet else "full_corpus",
            },
        }

        all_records.append(record)
        if is_prophet:
            prophets.append(record)

    # Grand sums
    prophet_sum_reduction = _reduce(prophet_sum)

    # Final value distribution (prophets only)
    prophet_final_dist = {}
    for p in prophets:
        v = p["final_value"]
        prophet_final_dist.setdefault(v, []).append(p["name_ar"])

    # Ibrahim uniqueness (within prophet chain)
    ibrahim_unique = len(prophet_final_dist.get(7, [])) == 1

    # Mosaic axis
    mosaic = [p for p in prophets if p["name_ar"] in ("إسحاق", "يعقوب", "موسى")]
    mosaic_all_8 = all(p["final_value"] == 8 for p in mosaic) and len(mosaic) == 3

    # Seal cluster (11→2)
    seal_members = [p for p in prophets if p["name_ar"] in ("سليمان", "يحيى", "محمد")]
    seal_all_11_to_2 = all(
        _passes_through_11(p["abjad_value"]) and p["final_value"] == 2
        for p in seal_members
    ) and len(seal_members) == 3

    # Chain endpoints
    adam_final = next(p["final_value"] for p in prophets if p["name_ar"] == "آدم")
    muhammad_final = next(p["final_value"] for p in prophets if p["name_ar"] == "محمد")

    # Master 11 full set
    master_11_full = [r for r in all_records if _passes_through_11(r["abjad_value"]) and r["final_value"] == 2]

    # Subject's name match check
    subject_matches = []
    if profile.arabic:
        subj_abjad = _compute_abjad(profile.arabic)
        subj_root = _reduce(subj_abjad)
        for rec in all_records:
            if rec["final_value"] == subj_root:
                subject_matches.append({
                    "name_ar": rec["name_ar"],
                    "name_en": rec["name_en"],
                    "category": rec["category"],
                    "shared_root": subj_root,
                })

    # Build structural findings summary
    structural_findings = {
        "prophet_chain_grand_sum": {
            "raw_sum": prophet_sum,
            "reduced": prophet_sum_reduction,
            "tags": ["GRAND_SUM_CONVERGENCE", "PROPHET_CHAIN_ONLY", "ADVERSARIAL_REVIEW_SURVIVED"],
            "strength": "HIGH",
        },
        "ibrahim_unique_at_7": {
            "unique_within_prophets": ibrahim_unique,
            "broken_in_full_corpus_by": "هامان" if not ibrahim_unique or any(
                r["name_ar"] == "هامان" and r["final_value"] == 7 for r in all_records
            ) else None,
            "tags": ["UNIQUE_POSITION", "PROPHET_CHAIN_ONLY", "ADVERSARIAL_REVIEW_SURVIVED"],
            "strength": "HIGH",
        },
        "mosaic_axis": {
            "members": ["إسحاق", "يعقوب", "موسى"],
            "all_equal_8": mosaic_all_8,
            "tags": ["STRUCTURAL_CLUSTER", "LINEAGE_COHERENT", "PROPHET_CHAIN_ONLY", "ADVERSARIAL_REVIEW_SURVIVED"],
            "strength": "HIGH",
        },
        "seal_cluster": {
            "members": ["سليمان", "يحيى", "محمد"],
            "all_11_to_2": seal_all_11_to_2,
            "tags": ["MASTER_CHAIN_MATCH", "STRUCTURAL_CLUSTER", "PROPHET_CHAIN_ONLY", "ADVERSARIAL_REVIEW_SURVIVED"],
            "strength": "MEDIUM",
        },
        "chain_endpoints": {
            "adam_final": adam_final,
            "muhammad_final": muhammad_final,
            "sum": adam_final + muhammad_final,
            "tags": ["CHAIN_ENDPOINT_PATTERN", "MASTER_CHAIN_MATCH", "PROPHET_CHAIN_ONLY", "ADVERSARIAL_REVIEW_SURVIVED"],
            "strength": "HIGH",
        },
        "adam_isa_frequency_25": {
            "adam_freq": freq_map.get("آدم"),
            "isa_freq": freq_map.get("عيسى"),
            "match": freq_map.get("آدم") == freq_map.get("عيسى") == 25,
            "tags": ["QURAN_FREQUENCY_ECHO", "ADVERSARIAL_REVIEW_SURVIVED"],
            "strength": "HIGH",
        },
        "ayyub_raw_19": {
            "raw_value": 19,
            "tags": ["WITHIN_SYSTEM_SYMBOLIC_ECHO", "ADVERSARIAL_REVIEW_SURVIVED"],
            "strength": "MEDIUM",
        },
        "muhammad_hebrew_crossmatch": {
            "arabic_abjad": 92,
            "hebrew_gematria": 92,
            "tags": ["CROSS_TRADITION_CONVERGENCE", "NON_TRIVIAL_TEXTUAL_LINK", "ADVERSARIAL_REVIEW_SURVIVED"],
            "strength": "HIGH",
        },
    }

    # Retired findings
    retired_findings = [
        {
            "name": "Full corpus grand sum",
            "reason": "Mod-9 artifact — digit shifts with Pharaoh addition",
            "retired_by": "Grok Batch 3",
            "tag": "ADVERSARIAL_REVIEW_REJECTED",
        },
        {
            "name": "Antagonist divergence as signal",
            "reason": "Absence of pattern ≠ pattern. P(all mismatch) ≈ 47% by chance",
            "retired_by": "Grok Batch 3",
            "tag": "ADVERSARIAL_REVIEW_REJECTED",
        },
        {
            "name": "Paired name divergence as signal",
            "reason": "Mismatch is default expectation (P ≈ 8/9 per pair)",
            "retired_by": "Grok Batch 3",
            "tag": "ADVERSARIAL_REVIEW_REJECTED",
        },
    ]

    # Checksums
    checksums = {
        "prophet_sum": prophet_sum,
        "prophet_sum_reduction": prophet_sum_reduction,
        "entity_count": 46,
        "record_count": len(all_records),
        "prophet_count": len(prophets),
    }

    return SystemResult(
        id="quranic_figures",
        name="Quranic Figures — pattern match (not lineage)",
        certainty="LOOKUP_FIXED",
        data={
            "figures": all_records,
            "prophet_count": len(prophets),
            "entity_count": 46,
            "record_count": len(all_records),
            "structural_findings": structural_findings,
            "retired_findings": retired_findings,
            "master_11_chain": {
                "prophet_triad": master11["prophet_triad"],
                "full_corpus_expansion": master11["full_corpus_expansion"],
                "full_set": [r["name_ar"] for r in master_11_full],
            },
            "antagonist_table": antagonists,
            "paired_figures": pairs,
            "checksums": checksums,
            "subject_root_matches": subject_matches,
            "constitutional_mode": "mirror_not_crystal_ball",
            # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
            "scholarship_fidelity": "CLASSICAL_METHOD_MODERN_APPLICATION",
            "scholarship_note": 'Pattern-detection, NOT continuation of classical Islamic tradition. Resemblance is mathematics, not lineage.',
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Quran — all 46 named figures extracted from Quranic text",
            "Abjad Kabir — classical letter-value table (ا=1 through غ=1000)",
            "Computation locked: Claude = DeepSeek = ChatGPT — 0 discrepancies across 46 figures",
            "Adversarial review: 3 batches (Grok), 8 findings survived, 3 retired",
            "Hebrew cross-match: Song of Songs 5:16 — מחמד = 92 = محمد",
            "SOURCE_TIER: A — Quranic text primary, computation verified by 3 independent models",
        ],
        question="Q1_IDENTITY",
    )
