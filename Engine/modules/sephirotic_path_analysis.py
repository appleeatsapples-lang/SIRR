"""
Sephirotic Path Analysis (ניתוח ספירות)
──────────────────────────────────────────
Maps core numerological values to Sephirot on the Tree of Life and
analyzes the path pattern across multiple number systems.

Class C / META — derives from other modules' outputs.

Algorithm:
  1. Map life_path → primary Sephirah (number → sephirah)
  2. Map expression → secondary Sephirah
  3. Map abjad root → Arabic-Kabbalistic bridge Sephirah
  4. Map birthday number → tertiary Sephirah
  5. Analyze: which pillars are activated (Severity/Mercy/Middle)
  6. Detect Da'at (11) connections

Source: Sepher Yetzirah; Etz Chaim (Chaim Vital); kabbalah_solomonic_lookups.json
SOURCE_TIER: B (Kabbalistic application of classical Tree)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


SEPHIROT = {
    1: {"name": "Keter", "english": "Crown", "pillar": "Middle", "soul_level": "Yechidah"},
    2: {"name": "Chokhmah", "english": "Wisdom", "pillar": "Mercy", "soul_level": "Chayah"},
    3: {"name": "Binah", "english": "Understanding", "pillar": "Severity", "soul_level": "Neshamah"},
    4: {"name": "Chesed", "english": "Mercy/Loving-kindness", "pillar": "Mercy", "soul_level": "Ruach (upper)"},
    5: {"name": "Gevurah", "english": "Severity/Judgment", "pillar": "Severity", "soul_level": "Ruach"},
    6: {"name": "Tiferet", "english": "Beauty/Balance", "pillar": "Middle", "soul_level": "Ruach (center)"},
    7: {"name": "Netzach", "english": "Victory/Eternity", "pillar": "Mercy", "soul_level": "Ruach (lower)"},
    8: {"name": "Hod", "english": "Glory/Splendor", "pillar": "Severity", "soul_level": "Nefesh (upper)"},
    9: {"name": "Yesod", "english": "Foundation", "pillar": "Middle", "soul_level": "Nefesh"},
    10: {"name": "Malkuth", "english": "Kingdom", "pillar": "Middle", "soul_level": "Nefesh (manifest)"},
    11: {"name": "Da'at", "english": "Knowledge (Hidden)", "pillar": "Middle", "soul_level": "bridge: Yechidah-Chayah"},
}


def _map_to_sephirah(n: int) -> dict:
    """Map a number 1-11 to a Sephirah. Numbers > 10 reduce (except 11=Da'at)."""
    if n == 11:
        return SEPHIROT[11].copy()
    if n == 22:
        # Master 22 → Malkuth (10) with Chokhmah (2) overtone
        s = SEPHIROT[10].copy()
        s["master_overtone"] = SEPHIROT[2]["name"]
        return s
    if n == 33:
        # Master 33 → Binah (3) with Tiferet (6) overtone
        s = SEPHIROT[3].copy()
        s["master_overtone"] = SEPHIROT[6]["name"]
        return s
    if 1 <= n <= 10:
        return SEPHIROT[n].copy()
    # Reduce
    while n > 10:
        n = sum(int(d) for d in str(n))
    return SEPHIROT.get(n, SEPHIROT[1]).copy()


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    # Gather core numbers
    mappings = {}

    sources = {
        "life_path": profile.life_path,
        "expression": profile.expression,
        "soul_urge": profile.soul_urge,
        "personality": profile.personality,
        "birthday_number": profile.birthday_number,
    }

    # Also map abjad root if available
    abjad_root = None
    all_results = kwargs.get("all_results", [])
    for r in all_results:
        if r.id == "abjad_kabir" and r.data:
            abjad_root = r.data.get("root")
            break

    if abjad_root is not None:
        sources["abjad_root"] = abjad_root

    for key, val in sources.items():
        if val is not None:
            seph = _map_to_sephirah(val)
            seph["source_value"] = val
            mappings[key] = seph

    # Pillar analysis
    pillars = {"Mercy": 0, "Severity": 0, "Middle": 0}
    for m in mappings.values():
        p = m.get("pillar")
        if p:
            pillars[p] += 1

    dominant_pillar = max(pillars, key=pillars.get)
    # Balanced if spread ≤ 1
    vals = list(pillars.values())
    balanced = (max(vals) - min(vals)) <= 1

    # Da'at detection
    has_daat = any(m.get("name") == "Da'at" for m in mappings.values())

    # Unique sephirot activated
    active_sephirot = list({m["name"] for m in mappings.values()})

    return SystemResult(
        id="sephirotic_path_analysis",
        name="Sephirotic Path Analysis",
        certainty="META",
        data={
            "mappings": mappings,
            "pillar_counts": pillars,
            "dominant_pillar": dominant_pillar,
            "pillar_balanced": balanced,
            "daat_active": has_daat,
            "active_sephirot": active_sephirot,
            "sephirot_count": len(active_sephirot),
            "module_class": "meta",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Sepher Yetzirah", "Etz Chaim (Chaim Vital)", "kabbalah_solomonic_lookups.json"],
        question="Q2_MEANING",
    )
