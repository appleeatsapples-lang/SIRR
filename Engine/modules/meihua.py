"""Plum Blossom Numerology / Meihua Yishu (梅花易数) — COMPUTED_STRICT
Shao Yong's method: DOB digits → upper/lower trigrams + moving line → hexagram.
Upper = (year + month + day) mod 8, Lower = (year + month + day + hour) mod 8,
Moving line = total mod 6.
Source: Shao Yong, Meihua Yishu (宋·邵雍, 11th century)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

TRIGRAMS = {
    0: ("Kun", "Earth", "☷"), 1: ("Qian", "Heaven", "☰"),
    2: ("Dui", "Lake", "☱"), 3: ("Li", "Fire", "☲"),
    4: ("Zhen", "Thunder", "☳"), 5: ("Xun", "Wind", "☴"),
    6: ("Kan", "Water", "☵"), 7: ("Gen", "Mountain", "☶"),
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    y = profile.dob.year
    m = profile.dob.month
    d = profile.dob.day
    h = 10  # default hour
    if profile.birth_time_local:
        try:
            h = int(profile.birth_time_local.split(":")[0])
        except ValueError:
            pass

    # Chinese hour branch index (2-hour blocks from 23:00)
    hour_branch = ((h + 1) // 2) % 12

    upper_num = (y + m + d) % 8
    lower_num = (y + m + d + hour_branch) % 8
    moving_line = (y + m + d + hour_branch) % 6 + 1

    up_name, up_elem, up_sym = TRIGRAMS[upper_num]
    lo_name, lo_elem, lo_sym = TRIGRAMS[lower_num]

    return SystemResult(
        id="meihua", name="Plum Blossom Numerology (梅花易数)",
        certainty="COMPUTED_STRICT",
        data={
            "upper_trigram": {"number": upper_num, "name": up_name, "element": up_elem, "symbol": up_sym},
            "lower_trigram": {"number": lower_num, "name": lo_name, "element": lo_elem, "symbol": lo_sym},
            "moving_line": moving_line,
            "hexagram_symbol": f"{up_sym}{lo_sym}",
        },
        interpretation=None, constants_version=constants["version"],
        references=["Shao Yong, Meihua Yishu (梅花易数): DOB → trigram pair + moving line"],
        question="Q1_IDENTITY"
    )
