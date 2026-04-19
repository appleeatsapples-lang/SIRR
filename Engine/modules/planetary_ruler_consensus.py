"""
Planetary Ruler Consensus (Cross-Tradition Ruling Planet Bridge)
─────────────────────────────────────────────────────────────────
Collects planetary ruler assignments from multiple traditions and
finds which planet dominates across systems.

Systems polled:
  - Day ruler (weekday planet)
  - Firdaria (current period ruler)
  - Essential dignities (almuten / chart ruler)
  - Arabic letter nature (Al-Buni dominant planet)
  - Solomonic correspondences (birth day planet)
  - Vedic gem prescription (ascendant lord)

Algorithm:
  1. Extract dominant/ruling planet from each system
  2. Tally votes across systems
  3. Compute consensus planet and agreement score

Source: Cross-tradition structural comparison
SOURCE_TIER: B (bridge module — deterministic aggregation)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


PLANET_IDS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
              "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"}


def _extract_planet(value: str | None) -> str | None:
    """Try to match a string to a known planet name."""
    if not value:
        return None
    for p in PLANET_IDS:
        if p.lower() in value.lower():
            return p
    return None


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    all_results = kwargs.get("all_results", [])

    votes: dict[str, int] = {}
    system_votes = {}

    for r in all_results:
        if not r.data:
            continue

        planet = None

        if r.id == "day_ruler":
            planet = r.data.get("ruler") or r.data.get("ruling_planet")
        elif r.id == "firdaria":
            planet = r.data.get("current_planet") or r.data.get("major_ruler")
        elif r.id == "almuten":
            planet = r.data.get("almuten") or r.data.get("almuten_planet")
        elif r.id == "arabic_letter_nature":
            planet = r.data.get("dominant_planet")
        elif r.id == "solomonic_correspondences":
            planet = r.data.get("dominant_planet")
        elif r.id == "vedic_gem_prescription":
            planet = r.data.get("ascendant_lord")
        elif r.id == "essential_dignities":
            planet = r.data.get("most_dignified_planet") or r.data.get("chart_ruler")
        elif r.id == "sect":
            planet = r.data.get("sect_light")  # Diurnal = Sun, Nocturnal = Moon
        elif r.id == "god_of_day":
            planet = r.data.get("ruling_planet")

        if planet:
            # Normalize
            matched = _extract_planet(planet) or planet
            if matched:
                votes[matched] = votes.get(matched, 0) + 1
                system_votes[r.id] = matched

    total = len(system_votes)
    if total == 0:
        consensus = None
        agreement = 0.0
    else:
        consensus = max(votes, key=votes.get)
        agreement = round(votes[consensus] / total, 3)

    # Secondary planet (second most votes)
    sorted_planets = sorted(votes.items(), key=lambda x: -x[1])
    secondary = sorted_planets[1][0] if len(sorted_planets) > 1 else None

    return SystemResult(
        id="planetary_ruler_consensus",
        name="Planetary Ruler Consensus (Cross-Tradition)",
        certainty="COMPUTED_STRICT",
        data={
            "votes": votes,
            "consensus_planet": consensus,
            "consensus_count": votes.get(consensus, 0) if consensus else 0,
            "secondary_planet": secondary,
            "total_systems": total,
            "agreement_score": agreement,
            "system_votes": system_votes,
            "module_class": "comparative",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Cross-tradition structural comparison"],
        question="Q1_IDENTITY",
    )
