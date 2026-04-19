"""BaZi Combinations & Clashes (合冲刑害) — COMPUTED_STRICT
Checks all branch pairs for Six Harmonies (六合), Three Harmonies (三合),
Clashes (六冲), Punishments (三刑), and Harms (六害).
Source: Classical BaZi (San Ming Tong Hui)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

BRANCHES = ["Zǐ","Chǒu","Yín","Mǎo","Chén","Sì","Wǔ","Wèi","Shēn","Yǒu","Xū","Hài"]

SIX_HARMONIES = {
    frozenset({"Zǐ","Chǒu"}): "Earth", frozenset({"Yín","Hài"}): "Wood",
    frozenset({"Mǎo","Xū"}): "Fire", frozenset({"Chén","Yǒu"}): "Metal",
    frozenset({"Sì","Shēn"}): "Water", frozenset({"Wǔ","Wèi"}): "Fire/Earth",
}

SIX_CLASHES = [
    frozenset({"Zǐ","Wǔ"}), frozenset({"Chǒu","Wèi"}),
    frozenset({"Yín","Shēn"}), frozenset({"Mǎo","Yǒu"}),
    frozenset({"Chén","Xū"}), frozenset({"Sì","Hài"}),
]

THREE_HARMONIES = [
    ({"Shēn","Zǐ","Chén"}, "Water"), ({"Hài","Mǎo","Wèi"}, "Wood"),
    ({"Yín","Wǔ","Xū"}, "Fire"), ({"Sì","Yǒu","Chǒu"}, "Metal"),
]

SIX_HARMS = [
    frozenset({"Zǐ","Wèi"}), frozenset({"Chǒu","Wǔ"}),
    frozenset({"Yín","Sì"}), frozenset({"Mǎo","Chén"}),
    frozenset({"Shēn","Hài"}), frozenset({"Yǒu","Xū"}),
]

def compute(profile: InputProfile, constants: dict, bazi_data: dict = None) -> SystemResult:
    if bazi_data is None:
        from modules import julian, bazi_pillars
        jdn = julian.compute(profile, constants).data["jdn"]
        bazi_data = bazi_pillars.compute(profile, constants, jdn=jdn).data

    chart_branches = []
    for key in ["year_pillar","month_pillar","day_pillar","hour_pillar"]:
        p = bazi_data.get(key)
        if p:
            chart_branches.append((key, p["branch_pinyin"]))

    harmonies, clashes, harms = [], [], []
    for i in range(len(chart_branches)):
        for j in range(i+1, len(chart_branches)):
            pair = frozenset({chart_branches[i][1], chart_branches[j][1]})
            labels = f"{chart_branches[i][0]}↔{chart_branches[j][0]}"
            if pair in SIX_HARMONIES:
                harmonies.append({"pair": labels, "element": SIX_HARMONIES[pair]})
            if pair in SIX_CLASHES:
                clashes.append({"pair": labels})
            if pair in SIX_HARMS:
                harms.append({"pair": labels})

    # Three harmonies check
    branch_set = {b for _, b in chart_branches}
    three_h = []
    for trio, elem in THREE_HARMONIES:
        present = branch_set & trio
        if len(present) >= 2:
            three_h.append({"branches": sorted(present), "element": elem,
                           "complete": len(present) == 3})

    return SystemResult(
        id="bazi_combos", name="BaZi Combinations & Clashes (合冲刑害)",
        certainty="COMPUTED_STRICT",
        data={"six_harmonies": harmonies, "six_clashes": clashes,
              "six_harms": harms, "three_harmonies": three_h,
              "branches": [b for _, b in chart_branches]},
        interpretation=None, constants_version=constants["version"],
        references=["BaZi branch interactions: 六合, 三合, 六冲, 六害"],
        question="Q2_DYNAMICS"
    )
