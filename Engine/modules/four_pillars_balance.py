"""
Four Pillars Element Balance (五行平衡)
────────────────────────────────────────
Counts all five elements across the 8 characters (4 stems + 4 branches)
of the BaZi chart, with seasonal bonus.

Algorithm (from chinese_african_lookups.json):
  1. Map each of the 4 Heavenly Stems → element
  2. Map each of the 4 Earthly Branches → primary element
  3. Apply 1.25× seasonal bonus to the Month Branch element
  4. Compute dominant and weakest elements

Source: Zi Ping Zhen Quan; San Ming Tong Hui
SOURCE_TIER: A (classical BaZi text)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


STEM_ELEMENT = {
    "jia": "Wood", "yi": "Wood", "bing": "Fire", "ding": "Fire",
    "wu": "Earth", "ji": "Earth", "geng": "Metal", "xin": "Metal",
    "ren": "Water", "gui": "Water",
}

BRANCH_ELEMENT = {
    "zi": "Water", "chou": "Earth", "yin": "Wood", "mao": "Wood",
    "chen": "Earth", "si": "Fire", "wu_br": "Fire", "wei": "Earth",
    "shen": "Metal", "you": "Metal", "xu": "Earth", "hai": "Water",
}

# Season → element that gets bonus
SEASON_ELEMENT = {
    "yin": "Wood", "mao": "Wood", "chen": "Wood",     # Spring
    "si": "Fire", "wu_br": "Fire", "wei": "Fire",      # Summer
    "shen": "Metal", "you": "Metal", "xu": "Metal",    # Autumn
    "hai": "Water", "zi": "Water", "chou": "Water",    # Winter
}

SEASONAL_BONUS = 1.25

# Pinyin tone mark → plain mapping
_TONE_STRIP = {
    "jiǎ": "jia", "yǐ": "yi", "bǐng": "bing", "dīng": "ding",
    "wù": "wu", "jǐ": "ji", "gēng": "geng", "xīn": "xin",
    "rén": "ren", "guǐ": "gui",
    "zǐ": "zi", "chǒu": "chou", "yín": "yin", "mǎo": "mao",
    "chén": "chen", "sì": "si", "wǔ": "wu_br", "wèi": "wei",
    "shēn": "shen", "yǒu": "you", "xū": "xu", "hài": "hai",
}


def _normalize_pinyin(s: str) -> str:
    lower = s.strip().lower()
    return _TONE_STRIP.get(lower, lower)


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    bazi = kwargs.get("bazi_data")
    if not bazi:
        return SystemResult(
            id="four_pillars_balance",
            name="Four Pillars Element Balance",
            certainty="NEEDS_INPUT",
            data={"scores": None, "reason": "No BaZi pillar data"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["Zi Ping Zhen Quan"],
            question="Q1_IDENTITY",
        )

    scores = {"Wood": 0.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0}
    breakdown = []

    # Process all 4 pillars
    for pillar_name in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]:
        pillar = bazi.get(pillar_name, {})
        if not pillar:
            continue

        stem = _normalize_pinyin(pillar.get("stem_pinyin", ""))
        branch = _normalize_pinyin(pillar.get("branch_pinyin", ""))

        stem_el = STEM_ELEMENT.get(stem)
        branch_el = BRANCH_ELEMENT.get(branch)

        if stem_el:
            scores[stem_el] += 1.0
            breakdown.append({"source": f"{pillar_name}_stem", "value": stem, "element": stem_el, "weight": 1.0})
        if branch_el:
            weight = 1.0
            # Seasonal bonus for month branch
            if pillar_name == "month_pillar":
                season_el = SEASON_ELEMENT.get(branch)
                if season_el and season_el == branch_el:
                    weight = SEASONAL_BONUS
            scores[branch_el] += weight
            breakdown.append({"source": f"{pillar_name}_branch", "value": branch, "element": branch_el, "weight": weight})

    # Round scores
    scores = {k: round(v, 2) for k, v in scores.items()}
    total = sum(scores.values())

    dominant = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)

    # Balance assessment
    if total > 0:
        pcts = {k: round(v / total * 100, 1) for k, v in scores.items()}
        spread = max(pcts.values()) - min(pcts.values())
        if spread < 10:
            balance = "well_balanced"
        elif spread < 25:
            balance = "moderately_balanced"
        else:
            balance = "imbalanced"
    else:
        pcts = {k: 0.0 for k in scores}
        balance = "unknown"

    # Missing elements (score = 0)
    missing = [k for k, v in scores.items() if v == 0]

    return SystemResult(
        id="four_pillars_balance",
        name="Four Pillars Element Balance",
        certainty="COMPUTED_STRICT",
        data={
            "scores": scores,
            "percentages": pcts,
            "dominant_element": dominant,
            "weakest_element": weakest,
            "missing_elements": missing,
            "balance_assessment": balance,
            "total_weight": round(total, 2),
            "breakdown": breakdown,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Zi Ping Zhen Quan", "San Ming Tong Hui", "chinese_african_lookups.json"],
        question="Q1_IDENTITY",
    )
