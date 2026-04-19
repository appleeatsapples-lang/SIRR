"""ZWDS Si Hua Palace (Four Transformations) — COMPUTED_STRICT
Apply the Four Transformations (Hua Lu/Quan/Ke/Ji) based on birth year stem
to ZWDS star positions. Each stem activates 4 specific stars.
Source: Classical Zi Wei Dou Shu transformation rules
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Ten Heavenly Stems
STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]

# Four Transformations (Si Hua): stem → (Lu, Quan, Ke, Ji) star assignments
# Each stem activates exactly 4 stars with specific transformations
SI_HUA = {
    "Jia": {"Lu": "Lian Zhen", "Quan": "Po Jun", "Ke": "Wu Qu", "Ji": "Tai Yang"},
    "Yi":  {"Lu": "Tian Ji", "Quan": "Tian Liang", "Ke": "Zi Wei", "Ji": "Tai Yin"},
    "Bing": {"Lu": "Tian Tong", "Quan": "Tian Ji", "Ke": "Wen Chang", "Ji": "Lian Zhen"},
    "Ding": {"Lu": "Tai Yin", "Quan": "Tian Tong", "Ke": "Tian Ji", "Ji": "Ju Men"},
    "Wu":  {"Lu": "Tan Lang", "Quan": "Tai Yin", "Ke": "You Bi", "Ji": "Tian Ji"},
    "Ji":  {"Lu": "Wu Qu", "Quan": "Tan Lang", "Ke": "Tian Liang", "Ji": "Wen Qu"},
    "Geng": {"Lu": "Tai Yang", "Quan": "Wu Qu", "Ke": "Tai Yin", "Ji": "Tian Tong"},
    "Xin": {"Lu": "Ju Men", "Quan": "Tai Yang", "Ke": "Wen Qu", "Ji": "Wen Chang"},
    "Ren": {"Lu": "Tian Liang", "Quan": "Zi Wei", "Ke": "Zuo Fu", "Ji": "Wu Qu"},
    "Gui": {"Lu": "Po Jun", "Quan": "Ju Men", "Ke": "Tai Yin", "Ji": "Tan Lang"},
}

# Transformation meanings
HUA_MEANINGS = {
    "Lu": "Prosperity/Wealth (禄)",
    "Quan": "Authority/Power (权)",
    "Ke": "Fame/Examination (科)",
    "Ji": "Obstruction/Taboo (忌)",
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    # Get year stem from birth year
    stem_idx = (profile.dob.year - 4) % 10  # 4 CE = Jia
    year_stem = STEMS[stem_idx]

    transformations = SI_HUA.get(year_stem, {})

    # Build detailed output
    hua_details = []
    for hua_type in ("Lu", "Quan", "Ke", "Ji"):
        star = transformations.get(hua_type, "Unknown")
        hua_details.append({
            "transformation": hua_type,
            "meaning": HUA_MEANINGS.get(hua_type, ""),
            "star": star,
        })

    return SystemResult(
        id="zwds_si_hua_palace",
        name="ZWDS Si Hua (Four Transformations)",
        certainty="COMPUTED_STRICT",
        data={
            "year_stem": year_stem,
            "year_stem_index": stem_idx,
            "transformations": hua_details,
            "lu_star": transformations.get("Lu", ""),
            "quan_star": transformations.get("Quan", ""),
            "ke_star": transformations.get("Ke", ""),
            "ji_star": transformations.get("Ji", ""),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Classical Zi Wei Dou Shu: Si Hua (四化) Four Transformations by year stem",
            "SOURCE_TIER:A — Classical Chinese metaphysics text.",
        ],
        question="Q1_IDENTITY",
    )
