"""Celtic Tree Calendar (Graves) — COMPUTED_STRICT
Robert Graves' 13-month lunar tree calendar from The White Goddess (1948).
Each month maps to a tree, ogham letter, and symbolic association.
Source: Robert Graves, The White Goddess
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# (month_start, month_end, tree, ogham_letter)
TREES = [
    ((12,24),(1,20), "Birch", "Beth", "New beginnings"),
    ((1,21),(2,17), "Rowan", "Luis", "Protection"),
    ((2,18),(3,17), "Ash", "Nion", "Connection"),
    ((3,18),(4,14), "Alder", "Fearn", "Foundation"),
    ((4,15),(5,12), "Willow", "Saille", "Intuition"),
    ((5,13),(6,9), "Hawthorn", "Huath", "Purification"),
    ((6,10),(7,7), "Oak", "Duir", "Strength"),
    ((7,8),(8,4), "Holly", "Tinne", "Challenge"),
    ((8,5),(9,1), "Hazel", "Coll", "Wisdom"),
    ((9,2),(9,29), "Vine", "Muin", "Harvest"),
    ((9,30),(10,27), "Ivy", "Gort", "Persistence"),
    ((10,28),(11,24), "Reed", "Ngetal", "Direction"),
    ((11,25),(12,23), "Elder", "Ruis", "Transformation"),
]

def _match(dob, start, end):
    m, d = dob.month, dob.day
    sm, sd = start
    em, ed = end
    if sm > em:  # wraps year (Dec→Jan)
        return (m == sm and d >= sd) or (m == em and d <= ed) or (sm < m or m < em)
    return (m == sm and d >= sd) or (m == em and d <= ed) or (sm < m < em)

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    tree_name, ogham, meaning = "Unknown", "?", ""
    for start, end, t, o, desc in TREES:
        if _match(profile.dob, start, end):
            tree_name, ogham, meaning = t, o, desc
            break

    return SystemResult(
        id="celtic_tree", name="Celtic Tree Calendar (Graves)",
        certainty="COMPUTED_STRICT",
        data={"tree": tree_name, "ogham_letter": ogham, "meaning": meaning,
              "dob": str(profile.dob)},
        interpretation=None, constants_version=constants["version"],
        references=["Robert Graves, The White Goddess (1948), 13-month tree calendar"],
        question="Q1_IDENTITY"
    )
