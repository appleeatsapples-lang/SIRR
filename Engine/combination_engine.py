#!/usr/bin/env python3
"""Combination Engine — tag-overlap logic for root × sign interaction.

Replaces hardcoded tension/amplification lists with dynamic tag intersection.
Root is anchor (structural), sign is contextual (which tags get foregrounded).

Key insight: Root 3 × Scorpio foregrounds concealment/depth.
             Root 8 × Scorpio foregrounds intensity/power.
Same sign, different meaning depending on root.

CLI: python combination_engine.py <root> <sign>
"""
from __future__ import annotations
import json
import os
import sys
from typing import Any, Dict, List, Optional

ENGINE = os.path.dirname(os.path.abspath(__file__))
ROOT_TAGS_PATH = os.path.join(ENGINE, "semantic_layer", "root_tags.json")
SIGN_TAGS_PATH = os.path.join(ENGINE, "semantic_layer", "sign_tags.json")
ROOTS_PATH = os.path.join(ENGINE, "semantic_layer", "sirr_semantic_roots.json")
BIPOLAR_PATH = os.path.join(ENGINE, "semantic_layer", "bipolar_pairs.json")


def _load_json(path: str) -> dict:
    """Load JSON file, return empty dict on failure."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _flatten_root_tags(root_key: str, root_tags: dict) -> List[str]:
    """Flatten a root's tags across all 6 traditions into a single set."""
    root_data = root_tags.get("roots", {}).get(root_key, {})
    all_tags = []
    for tradition, tags in root_data.items():
        if isinstance(tags, list):
            all_tags.extend(tags)
    return list(set(all_tags))


def _get_sign_tags(sign: str, sign_tags: dict) -> List[str]:
    """Get a sign's full tag list (tags + shadow_tags)."""
    sign_data = sign_tags.get("signs", {}).get(sign.lower(), {})
    tags = sign_data.get("tags", [])
    shadow = sign_data.get("shadow_tags", [])
    return tags + shadow


def compute_tag_overlap(root: int, sign: str) -> dict:
    """Compute tag overlap between a root number and zodiac sign.

    Args:
        root: Root number (1-9, 11, 22, 33)
        sign: Zodiac sign name (lowercase)

    Returns:
        Dict with overlap_score, amplified_tags, tension_tags, shadow_tags
    """
    root_tags_data = _load_json(ROOT_TAGS_PATH)
    sign_tags_data = _load_json(SIGN_TAGS_PATH)
    roots_data = _load_json(ROOTS_PATH)

    if not root_tags_data or not sign_tags_data:
        return {"error": "Tag files not found", "overlap_score": 0.0}

    root_key = str(root)
    sign_lower = sign.lower()

    # Get all tags
    root_all_tags = set(_flatten_root_tags(root_key, root_tags_data))
    sign_all_tags = set(_get_sign_tags(sign_lower, sign_tags_data))

    # Get root's core and shadow tags from semantic roots
    root_info = roots_data.get("roots", {}).get(root_key, {})
    root_core = set(root_info.get("core_tags", []))
    root_shadow = set(root_info.get("shadow_tags", []))

    # Get sign's shadow tags
    sign_data = sign_tags_data.get("signs", {}).get(sign_lower, {})
    sign_shadow = set(sign_data.get("shadow_tags", []))
    sign_core = set(sign_data.get("tags", []))

    # Compute overlaps using semantic proximity (not just exact string match)
    # This allows tags from different vocabularies to connect
    shared = root_all_tags & sign_all_tags  # Exact matches
    amplified = root_core & sign_core
    tension = root_core & sign_shadow
    shadow_overlap = root_shadow & sign_shadow

    # Extend with semantic proximity matches
    semantic_shared = set()
    semantic_amplified = set()
    semantic_tension = set()
    semantic_shadow = set()

    for rt in root_all_tags:
        for st in sign_all_tags:
            if rt != st and _semantic_proximity(rt, st):
                semantic_shared.add(f"{rt}~{st}")
    for rt in root_core:
        for st in sign_core:
            if rt != st and _semantic_proximity(rt, st):
                semantic_amplified.add(f"{rt}~{st}")
    for rt in root_core:
        for st in sign_shadow:
            if rt != st and _semantic_proximity(rt, st):
                semantic_tension.add(f"{rt}~{st}")
    for rt in root_shadow:
        for st in sign_shadow:
            if rt != st and _semantic_proximity(rt, st):
                semantic_shadow.add(f"{rt}~{st}")

    total_shared = len(shared) + len(semantic_shared)
    union = root_all_tags | sign_all_tags
    overlap_score = round(total_shared / max(len(union), 1), 3)

    # Is this combination tensioned?
    is_tensioned = len(tension) > 0 or len(shadow_overlap) > 0 or len(semantic_tension) > 0

    return {
        "root": root,
        "sign": sign_lower,
        "overlap_score": overlap_score,
        "shared_tags": sorted(shared),
        "semantic_shared": sorted(semantic_shared),
        "amplified_tags": sorted(amplified),
        "semantic_amplified": sorted(semantic_amplified),
        "tension_tags": sorted(tension),
        "semantic_tension": sorted(semantic_tension),
        "shadow_overlap": sorted(shadow_overlap),
        "semantic_shadow": sorted(semantic_shadow),
        "is_tensioned": is_tensioned,
        "root_tag_count": len(root_all_tags),
        "sign_tag_count": len(sign_all_tags),
        "shared_count": total_shared,
    }


def resolve_sign_meaning(root: int, sign: str) -> dict:
    """Context-sensitive sign meaning resolution.

    The same sign means different things depending on the root.
    Root 3 × Scorpio → concealment/depth (3=expression meets Scorpio's concealment)
    Root 8 × Scorpio → intensity/power (8=power meets Scorpio's intensity)

    Returns the foregrounded and backgrounded tags.
    """
    roots_data = _load_json(ROOTS_PATH)
    sign_tags_data = _load_json(SIGN_TAGS_PATH)

    root_key = str(root)
    sign_lower = sign.lower()

    root_info = roots_data.get("roots", {}).get(root_key, {})
    root_core = set(root_info.get("core_tags", []))

    sign_data = sign_tags_data.get("signs", {}).get(sign_lower, {})
    sign_tags = sign_data.get("tags", [])

    if not root_core or not sign_tags:
        return {
            "root": root,
            "sign": sign_lower,
            "foregrounded": [],
            "backgrounded": [],
        }

    # Foreground: sign tags that resonate with OR dialectically oppose root's core tags
    # Background: sign tags with no meaningful interaction
    foregrounded = []
    foregrounded_dialectic = []
    backgrounded = []

    for tag in sign_tags:
        resonates = False
        opposes = False
        for core_tag in root_core:
            if tag == core_tag:
                resonates = True
                break
            if _semantic_proximity(tag, core_tag):
                resonates = True
                break
            if _dialectical_opposition(tag, core_tag):
                opposes = True

        if resonates:
            foregrounded.append(tag)
        elif opposes:
            foregrounded_dialectic.append(tag)
        else:
            backgrounded.append(tag)

    return {
        "root": root,
        "sign": sign_lower,
        "foregrounded": foregrounded,
        "foregrounded_dialectic": foregrounded_dialectic,
        "backgrounded": backgrounded,
        "root_label": root_info.get("label", ""),
        "root_core_tags": sorted(root_core),
    }


def _semantic_proximity(tag_a: str, tag_b: str) -> bool:
    """Check if two tags are semantically proximate.

    Uses semantic clusters rather than string matching.
    """
    # Semantic clusters — bridge root tags and sign tags vocabulary
    # Each cluster groups tags that share the same energetic direction
    clusters = [
        # Power/intensity cluster (Root 8 + Scorpio overlap)
        {"power", "authority", "sovereignty", "domination", "mastery", "material_mastery",
         "strength", "intensity", "penetration", "fortitude", "inner_power", "taming_force",
         "qudra", "shani", "karmic_lord", "fixity"},
        # Concealment/mystery cluster (Root 7 + Scorpio)
        {"concealment", "mystery", "secrecy", "hidden", "batin", "withdrawal",
         "introspection", "sirr", "ketu", "moksha", "analysis"},
        # Expression/creativity cluster (Root 3 + Leo/Gemini)
        {"expression", "communication", "creativity", "eloquence", "bayan",
         "radiance", "performance", "duality", "connection", "khalq", "creation",
         "fertility", "abundance", "creative_matrix", "creative_synthesis"},
        # Structure/foundation cluster (Root 4 + Capricorn/Taurus)
        {"structure", "foundation", "discipline", "order", "stability",
         "ambition", "endurance", "rootedness", "accumulation", "arkan", "nizam"},
        # Freedom/change cluster (Root 5 + Sagittarius/Aquarius)
        {"freedom", "change", "adventure", "movement", "exploration", "liberation",
         "expansion", "vision", "philosophy", "innovation", "rebellion", "haraka"},
        # Transformation/crisis cluster (Scorpio specific)
        {"transformation", "crisis", "dissolution", "surrender", "transcendence"},
        # Nurturing/service cluster (Root 6 + Cancer/Virgo)
        {"nurturing", "service", "harmony", "compassion", "responsibility",
         "protection", "emotion", "sanctuary", "healing", "refinement", "ihsan", "beauty"},
        # Independence/initiation cluster (Root 1 + Aries)
        {"independence", "initiation", "pioneer", "self-reliance", "assertion",
         "impulse", "courage", "action", "tawhid", "alif"},
        # Wisdom/spirituality cluster (Root 7/9)
        {"spirituality", "wisdom", "inner_vision", "completion", "universality",
         "humanitarianism", "collective", "kamal", "tamam"},
        # Expansion/growth cluster (Root 3/5/9 + Sagittarius/Jupiter)
        {"expansion", "growth", "abundance", "generosity", "prosperity",
         "brihaspati", "guru", "trimurti", "wood_growth"},
        # Restriction/contraction cluster (Root 4/8 + Saturn)
        {"contraction", "limitation", "restriction", "endurance", "karma",
         "discipline", "patience"},
        # Intuition/illumination cluster (Root 11/Moon)
        {"intuition", "illumination", "inspiration", "channel", "sensitivity",
         "receptivity", "memory", "ilham", "kashf"},
        # Partnership/diplomacy cluster (Root 2 + Libra)
        {"partnership", "diplomacy", "balance", "aesthetics", "justice",
         "pair_harmony", "dual_nature", "mizan"},
    ]

    for cluster in clusters:
        if tag_a in cluster and tag_b in cluster:
            return True
    return False


def _dialectical_opposition(tag_a: str, tag_b: str) -> bool:
    """Check if two tags are dialectically opposed.

    Expression ↔ concealment, independence ↔ nurturing, etc.
    When a root's core energy meets its dialectical opposite in a sign,
    that sign tag is foregrounded as a dialectic (not amplified, but activated).
    """
    oppositions = [
        ({"expression", "communication", "creativity", "radiance", "performance"},
         {"concealment", "mystery", "secrecy", "withdrawal", "hidden"}),
        ({"independence", "initiation", "self-reliance", "assertion", "pioneer"},
         {"partnership", "diplomacy", "codependence", "dependence"}),
        ({"structure", "foundation", "discipline", "order", "stability"},
         {"freedom", "change", "adventure", "fluidity", "dissolution"}),
        ({"expansion", "growth", "abundance", "vision"},
         {"contraction", "limitation", "restriction", "endurance"}),
        ({"action", "impulse", "courage", "assertion"},
         {"receptivity", "sensitivity", "surrender", "patience"}),
        ({"individual", "independence", "self-reliance"},
         {"collective", "universality", "humanitarianism", "nurturing"}),
    ]

    for set_a, set_b in oppositions:
        if (tag_a in set_a and tag_b in set_b) or (tag_a in set_b and tag_b in set_a):
            return True
    return False


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: python combination_engine.py <root> <sign>")
        print("Example: python combination_engine.py 3 scorpio")
        sys.exit(1)

    root = int(sys.argv[1])
    sign = sys.argv[2].lower()

    overlap = compute_tag_overlap(root, sign)
    meaning = resolve_sign_meaning(root, sign)

    print(f"Combination: Root {root} × {sign.capitalize()}")
    print("=" * 50)
    print(f"  Overlap score: {overlap['overlap_score']}")
    print(f"  Shared tags ({overlap['shared_count']}): {', '.join(overlap['shared_tags']) or 'none'}")
    print(f"  Amplified: {', '.join(overlap['amplified_tags']) or 'none'}")
    print(f"  Tension: {', '.join(overlap['tension_tags']) or 'none'}")
    print(f"  Shadow overlap: {', '.join(overlap['shadow_overlap']) or 'none'}")
    print(f"  Is tensioned: {overlap['is_tensioned']}")
    print()
    print(f"Sign meaning in context of Root {root} ({meaning.get('root_label', '')}):")
    print(f"  Foregrounded (resonance): {', '.join(meaning['foregrounded']) or 'none'}")
    print(f"  Foregrounded (dialectic): {', '.join(meaning.get('foregrounded_dialectic', [])) or 'none'}")
    print(f"  Backgrounded: {', '.join(meaning['backgrounded']) or 'none'}")


if __name__ == "__main__":
    main()
