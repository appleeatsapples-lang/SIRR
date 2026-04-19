"""
Element Consensus (Cross-Tradition Element Bridge)
────────────────────────────────────────────────────
Collects element votes from multiple tradition-specific element systems
and finds consensus/conflict across them.

Systems polled:
  - Vedic: Panchamahabhuta (5 elements)
  - Chinese: Four Pillars Balance (5 elements)
  - Western: Hermetic Element Balance (4 elements)
  - Arabic: Elemental Letters (4 elements)
  - Temperament (4 elements)

Algorithm:
  1. Normalize all systems to 4+1 element space (Fire/Earth/Air/Water + Ether)
  2. Tally dominant element from each system
  3. Compute agreement score (how many systems agree on dominant)
  4. Map Chinese→Western: Wood→Air, Metal→Air, Water→Water, Fire→Fire, Earth→Earth

Source: Cross-tradition structural comparison
SOURCE_TIER: B (bridge module — deterministic aggregation)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Chinese 5-element → Western 4-element normalization
CHINESE_TO_WESTERN = {
    "Wood": "Air",
    "Fire": "Fire",
    "Earth": "Earth",
    "Metal": "Air",
    "Water": "Water",
}

# Vedic 5-element → Western 4-element normalization
VEDIC_TO_WESTERN = {
    "Akasha": "Air",  # Ether closest to Air in 4-element system
    "Vayu": "Air",
    "Agni": "Fire",
    "Jala": "Water",
    "Prithvi": "Earth",
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    all_results = kwargs.get("all_results", [])

    votes = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    system_votes = {}

    for r in all_results:
        dominant = None

        if r.id == "panchamahabhuta" and r.data:
            raw = r.data.get("dominant_element")
            dominant = VEDIC_TO_WESTERN.get(raw)
            if dominant:
                system_votes["vedic_panchamahabhuta"] = {"raw": raw, "normalized": dominant}

        elif r.id == "four_pillars_balance" and r.data:
            raw = r.data.get("dominant_element")
            dominant = CHINESE_TO_WESTERN.get(raw)
            if dominant:
                system_votes["chinese_four_pillars"] = {"raw": raw, "normalized": dominant}

        elif r.id == "hermetic_element_balance" and r.data:
            dominant = r.data.get("dominant_element")
            if dominant and dominant in votes:
                system_votes["western_hermetic"] = {"raw": dominant, "normalized": dominant}

        elif r.id == "elemental_letters" and r.data:
            dominant = r.data.get("dominant_element")
            if dominant and dominant in votes:
                system_votes["arabic_elemental"] = {"raw": dominant, "normalized": dominant}

        elif r.id == "temperament" and r.data:
            dominant = r.data.get("primary_element")
            if dominant and dominant in votes:
                system_votes["temperament"] = {"raw": dominant, "normalized": dominant}

        if dominant and dominant in votes:
            votes[dominant] += 1

    total_systems = len(system_votes)
    consensus_element = max(votes, key=votes.get) if total_systems > 0 else None
    consensus_count = votes.get(consensus_element, 0) if consensus_element else 0

    # Agreement score: fraction of systems agreeing on dominant
    agreement_score = round(consensus_count / total_systems, 3) if total_systems > 0 else 0.0

    # Detect conflict (no clear majority)
    conflict = consensus_count < (total_systems / 2 + 0.5) if total_systems > 1 else False

    return SystemResult(
        id="element_consensus",
        name="Element Consensus (Cross-Tradition)",
        certainty="COMPUTED_STRICT",
        data={
            "votes": votes,
            "consensus_element": consensus_element,
            "consensus_count": consensus_count,
            "total_systems": total_systems,
            "agreement_score": agreement_score,
            "conflict": conflict,
            "system_votes": system_votes,
            "module_class": "comparative",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Cross-tradition structural comparison"],
        question="Q6_SYNTHESIS",
    )
