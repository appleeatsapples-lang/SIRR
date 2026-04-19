"""
Timing Consensus (Cross-Tradition Period Quality Bridge)
──────────────────────────────────────────────────────────
Aggregates period_quality from all timing systems and determines
overall timing consensus.

Systems polled:
  - Firdaria, Vimshottari, Biorhythm, Yogini Dasha
  - BaZi 10-Year Forecast (current period quality)
  - Zodiacal Releasing (peak/trough)
  - Any module with period_quality in data

Algorithm:
  1. Scan all results for period_quality or timing-quality fields
  2. Normalize to EXPANSIVE/CONTRACTIVE/MIXED
  3. Majority vote → consensus
  4. Compute agreement strength

Source: Cross-tradition structural comparison
SOURCE_TIER: B (bridge module — deterministic aggregation)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Normalize various quality labels to canonical form
QUALITY_MAP = {
    "benefic": "EXPANSIVE",
    "expansive": "EXPANSIVE",
    "supportive": "EXPANSIVE",
    "productive": "EXPANSIVE",
    "peak": "EXPANSIVE",
    "malefic": "CONTRACTIVE",
    "contractive": "CONTRACTIVE",
    "challenging": "CONTRACTIVE",
    "trough": "CONTRACTIVE",
    "mixed": "MIXED",
    "neutral": "MIXED",
    "transitional": "MIXED",
}

# Timing module IDs to check
TIMING_IDS = {
    "firdaria", "vimshottari", "biorhythm", "yogini_dasha",
    "bazi_10_year_forecast", "zodiacal_releasing", "solar_return",
    "ashtottari_dasha", "kalachakra_dasha", "dorothean_chronocrators",
    "chara_dasha",
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    all_results = kwargs.get("all_results", [])

    votes = {"EXPANSIVE": 0, "CONTRACTIVE": 0, "MIXED": 0}
    system_votes = {}

    for r in all_results:
        if r.id not in TIMING_IDS:
            continue
        if not r.data:
            continue

        quality = None
        # Check multiple possible field names
        for field in ["period_quality", "quality", "current_quality"]:
            raw = r.data.get(field)
            if raw:
                quality = raw
                break

        # Special handling for bazi_10_year_forecast
        if r.id == "bazi_10_year_forecast" and not quality:
            cp = r.data.get("current_period")
            if cp:
                quality = cp.get("quality")

        if not quality:
            continue

        normalized = QUALITY_MAP.get(quality.lower(), "MIXED")
        votes[normalized] += 1
        system_votes[r.id] = {"raw": quality, "normalized": normalized}

    total = len(system_votes)
    if total == 0:
        consensus = None
        agreement = 0.0
    else:
        consensus = max(votes, key=votes.get)
        agreement = round(votes[consensus] / total, 3)

    return SystemResult(
        id="timing_consensus",
        name="Timing Consensus (Cross-Tradition)",
        certainty="COMPUTED_STRICT",
        data={
            "votes": votes,
            "consensus": consensus,
            "consensus_count": votes.get(consensus, 0) if consensus else 0,
            "total_systems": total,
            "agreement_score": agreement,
            "system_votes": system_votes,
            "module_class": "comparative",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Cross-tradition structural comparison"],
        question="Q4_TIMING",
    )
