"""BaZi San He + San Hui (Three Harmonies + Directional Combos) — COMPUTED_STRICT
Scan all 4 BaZi pillars for:
- San He (Harmonious Trines): Shen-Zi-Chen=Water, Hai-Mao-Wei=Wood,
  Yin-Wu-Xu=Fire, Si-You-Chou=Metal. All 3 branches must be present.
- San Hui (Directional): Yin-Mao-Chen=East/Wood, Si-Wu-Wei=South/Fire,
  Shen-You-Xu=West/Metal, Hai-Zi-Chou=North/Water. All 3 must be present.
Source: Classical BaZi combination rules
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# San He (Three Harmonies / Trines) — using Chinese characters for unambiguous matching
SAN_HE = [
    {"branches": {"申", "子", "辰"}, "element": "Water", "name": "Water Frame"},
    {"branches": {"亥", "卯", "未"}, "element": "Wood", "name": "Wood Frame"},
    {"branches": {"寅", "午", "戌"}, "element": "Fire", "name": "Fire Frame"},
    {"branches": {"巳", "酉", "丑"}, "element": "Metal", "name": "Metal Frame"},
]

# San Hui (Directional Combos)
SAN_HUI = [
    {"branches": {"寅", "卯", "辰"}, "element": "Wood", "direction": "East"},
    {"branches": {"巳", "午", "未"}, "element": "Fire", "direction": "South"},
    {"branches": {"申", "酉", "戌"}, "element": "Metal", "direction": "West"},
    {"branches": {"亥", "子", "丑"}, "element": "Water", "direction": "North"},
]


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    bazi_data = kwargs.get("bazi_data")

    if not bazi_data:
        return SystemResult(
            id="bazi_san_he_san_hui", name="BaZi San He + San Hui",
            certainty="NEEDS_INPUT",
            data={"note": "Requires bazi_pillars data"},
            interpretation=None, constants_version=constants["version"],
            references=["Classical BaZi combination rules"],
            question="Q1_IDENTITY",
        )

    # Collect all earthly branches (Chinese characters) from pillars
    branches = set()
    for pillar_key in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        p = bazi_data.get(pillar_key, {})
        b = p.get("branch", "")
        if b:
            branches.add(b)

    # Check San He
    san_he_found = []
    for combo in SAN_HE:
        if combo["branches"].issubset(branches):
            san_he_found.append({"element": combo["element"], "name": combo["name"]})

    # Check San Hui
    san_hui_found = []
    for combo in SAN_HUI:
        if combo["branches"].issubset(branches):
            san_hui_found.append({"element": combo["element"], "direction": combo["direction"]})

    # Partial matches (2 of 3 present)
    san_he_partial = []
    for combo in SAN_HE:
        overlap = combo["branches"] & branches
        if len(overlap) == 2:
            missing = (combo["branches"] - branches).pop()
            san_he_partial.append({"element": combo["element"], "present": sorted(overlap), "missing": missing})

    return SystemResult(
        id="bazi_san_he_san_hui",
        name="BaZi San He + San Hui",
        certainty="COMPUTED_STRICT",
        data={
            "branches_found": sorted(branches),
            "san_he_complete": san_he_found,
            "san_he_count": len(san_he_found),
            "san_hui_complete": san_hui_found,
            "san_hui_count": len(san_hui_found),
            "san_he_partial": san_he_partial,
            "san_he_element": san_he_found[0]["element"] if san_he_found else None,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Classical BaZi: San He (三合) Three Harmonies, San Hui (三会) Directional Combos",
            "SOURCE_TIER:A — Classical Chinese metaphysics text.",
        ],
        question="Q1_IDENTITY",
    )
