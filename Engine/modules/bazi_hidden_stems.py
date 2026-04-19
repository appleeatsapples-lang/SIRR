"""BaZi Hidden Stems (藏干) — COMPUTED_STRICT
Each Earthly Branch contains 1-3 hidden Heavenly Stems.
These reveal the 'inner nature' of each pillar beyond the visible stem.
Source: Classical BaZi texts (Zi Ping Zhen Quan, Di Tian Sui)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Branch pinyin → list of hidden stem pinyin (main, middle, residual)
HIDDEN_STEMS = {
    "Zǐ":   ["Guǐ"],
    "Chǒu": ["Jǐ", "Guǐ", "Xīn"],
    "Yín":  ["Jiǎ", "Bǐng", "Wù"],
    "Mǎo":  ["Yǐ"],
    "Chén": ["Wù", "Yǐ", "Guǐ"],
    "Sì":   ["Bǐng", "Wù", "Gēng"],
    "Wǔ":   ["Dīng", "Jǐ"],
    "Wèi":  ["Jǐ", "Dīng", "Yǐ"],
    "Shēn": ["Gēng", "Rén", "Wù"],
    "Yǒu":  ["Xīn"],
    "Xū":   ["Wù", "Xīn", "Dīng"],
    "Hài":  ["Rén", "Jiǎ"],
}

STEM_ELEMENTS = {
    "Jiǎ": "Yang Wood", "Yǐ": "Yin Wood",
    "Bǐng": "Yang Fire", "Dīng": "Yin Fire",
    "Wù": "Yang Earth", "Jǐ": "Yin Earth",
    "Gēng": "Yang Metal", "Xīn": "Yin Metal",
    "Rén": "Yang Water", "Guǐ": "Yin Water",
}

def _extract_branch_pinyin(pillar_data: dict) -> str:
    return pillar_data.get("branch_pinyin", "")

def compute(profile: InputProfile, constants: dict, bazi_data: dict = None) -> SystemResult:
    # bazi_data should be the .data dict from bazi_pillars result
    if bazi_data is None:
        from modules import julian, bazi_pillars
        jdn = julian.compute(profile, constants).data["jdn"]
        bazi_data = bazi_pillars.compute(profile, constants, jdn=jdn).data

    pillars = {}
    for key in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]:
        p = bazi_data.get(key)
        if not p:
            continue
        bp = _extract_branch_pinyin(p)
        hidden = HIDDEN_STEMS.get(bp, [])
        pillars[key] = {
            "branch": bp,
            "hidden_stems": hidden,
            "hidden_elements": [STEM_ELEMENTS.get(s, s) for s in hidden],
            "main_qi": hidden[0] if hidden else None,
        }

    # Collect all hidden elements for element distribution
    all_hidden = []
    for v in pillars.values():
        all_hidden.extend(v["hidden_elements"])
    element_count = {}
    for e in all_hidden:
        base = e.split()[-1]  # "Yang Wood" → "Wood"
        element_count[base] = element_count.get(base, 0) + 1

    return SystemResult(
        id="bazi_hidden_stems", name="BaZi Hidden Stems (藏干)",
        certainty="COMPUTED_STRICT",
        data={"pillars": pillars, "hidden_element_distribution": element_count},
        interpretation=None, constants_version=constants["version"],
        references=["BaZi Hidden Stems (藏干): Zi Ping Zhen Quan"],
        question="Q1_IDENTITY"
    )
