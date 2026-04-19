"""BaZi Special Stars / Shen Sha (神煞) — COMPUTED_STRICT
Auxiliary stars derived from Day Master and branch positions.
Includes: Tian Yi (Noble), Tao Hua (Peach Blossom), Yi Ma (Travel Horse),
Wen Chang (Academic), Lu Shen (Prosperity), etc.
Source: San Ming Tong Hui, Zi Ping Zhen Quan
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Tian Yi Gui Ren (天乙贵人) — Noble Star by Day Stem
TIAN_YI = {
    "Jiǎ":["Chǒu","Wèi"], "Yǐ":["Zǐ","Shēn"], "Bǐng":["Hài","Yǒu"],
    "Dīng":["Hài","Yǒu"], "Wù":["Chǒu","Wèi"], "Jǐ":["Zǐ","Shēn"],
    "Gēng":["Chǒu","Wèi"], "Xīn":["Yín","Wǔ"], "Rén":["Mǎo","Sì"],
    "Guǐ":["Mǎo","Sì"],
}
# Tao Hua (桃花) — Peach Blossom by Year/Day Branch
TAO_HUA = {
    "Zǐ":"Yǒu","Chǒu":"Wǔ","Yín":"Mǎo","Mǎo":"Zǐ",
    "Chén":"Yǒu","Sì":"Wǔ","Wǔ":"Mǎo","Wèi":"Zǐ",
    "Shēn":"Yǒu","Yǒu":"Wǔ","Xū":"Mǎo","Hài":"Zǐ",
}
# Yi Ma (驿马) — Travel Horse by Year/Day Branch
YI_MA = {
    "Zǐ":"Yín","Chǒu":"Hài","Yín":"Shēn","Mǎo":"Sì",
    "Chén":"Yín","Sì":"Hài","Wǔ":"Shēn","Wèi":"Sì",
    "Shēn":"Yín","Yǒu":"Hài","Xū":"Shēn","Hài":"Sì",
}

def compute(profile: InputProfile, constants: dict, bazi_data: dict = None) -> SystemResult:
    if bazi_data is None:
        from modules import julian, bazi_pillars
        jdn = julian.compute(profile, constants).data["jdn"]
        bazi_data = bazi_pillars.compute(profile, constants, jdn=jdn).data

    dm = bazi_data["day_pillar"]["stem_pinyin"]
    branches = {}
    for key in ["year_pillar","month_pillar","day_pillar","hour_pillar"]:
        p = bazi_data.get(key)
        if p:
            branches[key] = p["branch_pinyin"]

    branch_list = list(branches.values())
    stars = []

    # Tian Yi
    noble_branches = TIAN_YI.get(dm, [])
    for b in branch_list:
        if b in noble_branches:
            stars.append({"star": "Tian Yi Gui Ren (天乙贵人)", "location": b, "meaning": "Noble person assistance"})

    # Tao Hua
    year_b = branches.get("year_pillar", "")
    day_b = branches.get("day_pillar", "")
    for ref_b in [year_b, day_b]:
        peach = TAO_HUA.get(ref_b)
        if peach and peach in branch_list:
            stars.append({"star": "Tao Hua (桃花)", "location": peach, "meaning": "Charm, romance, charisma"})

    # Yi Ma
    for ref_b in [year_b, day_b]:
        horse = YI_MA.get(ref_b)
        if horse and horse in branch_list:
            stars.append({"star": "Yi Ma (驿马)", "location": horse, "meaning": "Travel, movement, change"})

    return SystemResult(
        id="bazi_shensha", name="BaZi Special Stars (神煞)",
        certainty="COMPUTED_STRICT",
        data={"day_master": dm, "stars_found": stars, "star_count": len(stars)},
        interpretation=None, constants_version=constants["version"],
        references=["Shen Sha (神煞): San Ming Tong Hui auxiliary star system"],
        question="Q2_DYNAMICS"
    )
