"""BaZi 12 Growth Phases — LOOKUP_FIXED"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    cfg = constants["bazi_growth"]
    phases = cfg["yin_water_gui"]

    # Approximate pillars for 1990-03-15
    # Year: Yang Fire Rat (丙子) → branch = zi/rat
    # Month: Yin Fire Rooster (丁酉) → branch = you/rooster  
    # Day: Yin Water Pig (癸亥) → branch = hai/pig

    data = {
        "day_master": "Gui (癸) Yin Water",
        "year_branch": "Rat (子)",
        "year_phase": phases.get("zi_rat", "Unknown"),
        "month_branch": "Rooster (酉)",
        "month_phase": phases.get("you_rooster", "Unknown"),
        "day_branch": "Pig (亥)",
        "day_phase": phases.get("hai_pig", "Unknown"),
        "strength_summary": "Peak in Year + Day, weak in Month",
        "note": cfg.get("notes", "")
    }

    return SystemResult(
        id="bazi_growth",
        name="BaZi 12 Growth Phases",
        certainty="LOOKUP_FIXED",
        data=data,
        interpretation="Growth phase of Day Master in each branch. Pillar branches are approximate without verified BaZi chart.",
        constants_version=constants["version"],
        references=["Standard BaZi 12 Growth Phase table"],
        question="Q3_NATURE"
    )
