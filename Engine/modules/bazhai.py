"""Eight Mansions / Ba Zhai (八宅) — COMPUTED_STRICT
Personal Gua number from DOB → 8 directional influences.
Male: (100 - last 2 digits of year) / 9, remainder = Gua.
Female: (last 2 digits of year - 4) / 9, remainder = Gua.
Source: Classical Ba Zhai Ming Jing (Eight Mansions text)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

GUA_NAMES = {
    1: ("Kan", "Water", "☵", "North"),
    2: ("Kun", "Earth", "☷", "Southwest"),
    3: ("Zhen", "Thunder", "☳", "East"),
    4: ("Xun", "Wind", "☴", "Southeast"),
    5: ("Kun/Gen", "Earth", "☷/☶", "Center"),  # 5 → 2(M) or 8(F)
    6: ("Qian", "Heaven", "☰", "Northwest"),
    7: ("Dui", "Lake", "☱", "West"),
    8: ("Gen", "Mountain", "☶", "Northeast"),
    9: ("Li", "Fire", "☲", "South"),
}

EAST_GROUP = {1, 3, 4, 9}
WEST_GROUP = {2, 6, 7, 8}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    y = profile.dob.year
    last2 = y % 100

    # Use lunar year cutoff: before Feb 4 = previous year
    if profile.dob.month < 2 or (profile.dob.month == 2 and profile.dob.day < 4):
        last2 = (y - 1) % 100

    # Male formula (default — SIRR doesn't store gender, use male)
    gua_num = (100 - last2) % 9
    if gua_num == 0:
        gua_num = 9
    if gua_num == 5:
        gua_num = 2  # Male 5→Kun(2)

    name, element, symbol, direction = GUA_NAMES.get(gua_num, ("?","?","?","?"))
    group = "East" if gua_num in EAST_GROUP else "West"

    return SystemResult(
        id="bazhai", name="Eight Mansions / Ba Zhai (八宅)",
        certainty="COMPUTED_STRICT",
        data={
            "gua_number": gua_num, "gua_name": name,
            "gua_element": element, "gua_symbol": symbol,
            "gua_direction": direction, "life_group": group,
            "note": "Male formula used (5→2). Female would use (last2-4)/9, 5→8."
        },
        interpretation=None, constants_version=constants["version"],
        references=["Ba Zhai Ming Jing (八宅明镜): Personal Gua from birth year"],
        question="Q5_ENVIRONMENT"
    )
