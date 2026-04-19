"""BaZi Ten Gods (十神) — COMPUTED_STRICT
Determines the relationship between Day Master and every other stem
in the chart using the Five-Element producing/controlling cycle.
Source: Classical BaZi (Zi Ping Zhen Quan, Di Tian Sui)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

STEM_INFO = {
    "Jiǎ":("Wood","Yang"), "Yǐ":("Wood","Yin"),
    "Bǐng":("Fire","Yang"), "Dīng":("Fire","Yin"),
    "Wù":("Earth","Yang"), "Jǐ":("Earth","Yin"),
    "Gēng":("Metal","Yang"), "Xīn":("Metal","Yin"),
    "Rén":("Water","Yang"), "Guǐ":("Water","Yin"),
}

PRODUCES = {"Wood":"Fire","Fire":"Earth","Earth":"Metal","Metal":"Water","Water":"Wood"}
CONTROLS = {"Wood":"Earth","Earth":"Water","Water":"Fire","Fire":"Metal","Metal":"Wood"}

def _ten_god(dm_elem, dm_pol, other_elem, other_pol):
    same_pol = (dm_pol == other_pol)
    if other_elem == dm_elem:
        return "Companion (比肩)" if same_pol else "Rob Wealth (劫财)"
    if PRODUCES[dm_elem] == other_elem:
        return "Eating God (食神)" if same_pol else "Hurting Officer (伤官)"
    if CONTROLS[dm_elem] == other_elem:
        return "Indirect Wealth (偏财)" if same_pol else "Direct Wealth (正财)"
    if CONTROLS[other_elem] == dm_elem:
        return "7 Killings (七杀)" if same_pol else "Direct Officer (正官)"
    if PRODUCES[other_elem] == dm_elem:
        return "Indirect Seal (偏印)" if same_pol else "Direct Seal (正印)"
    return "Unknown"

def compute(profile: InputProfile, constants: dict, bazi_data: dict = None) -> SystemResult:
    if bazi_data is None:
        from modules import julian, bazi_pillars
        jdn = julian.compute(profile, constants).data["jdn"]
        bazi_data = bazi_pillars.compute(profile, constants, jdn=jdn).data

    dm_pinyin = bazi_data["day_pillar"]["stem_pinyin"]
    dm_elem, dm_pol = STEM_INFO[dm_pinyin]

    gods = {}
    for key in ["year_pillar", "month_pillar", "hour_pillar"]:
        p = bazi_data.get(key)
        if not p:
            continue
        sp = p["stem_pinyin"]
        se, spo = STEM_INFO[sp]
        gods[key] = {"stem": sp, "element": se, "polarity": spo,
                     "ten_god": _ten_god(dm_elem, dm_pol, se, spo)}

    return SystemResult(
        id="bazi_ten_gods", name="BaZi Ten Gods (十神)",
        certainty="COMPUTED_STRICT",
        data={"day_master": dm_pinyin, "day_master_element": f"{dm_pol} {dm_elem}",
              "pillar_gods": gods},
        interpretation=None, constants_version=constants["version"],
        references=["Ten Gods (十神): Five-Element relationship to Day Master"],
        question="Q1_IDENTITY"
    )
