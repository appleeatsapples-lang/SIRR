"""Tibetan Mewa & Parkha — COMPUTED_STRICT
9 Mewa (colored numbers) + 8 Parkha (trigrams) from birth year.
Mewa cycles every 9 years descending. Parkha cycles every 8 years.
Source: Tibetan Elemental Astrology (Jungtsi)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

MEWA = {
    1: ("1 White", "Iron", "Compassion, authority"),
    2: ("2 Black", "Water", "Accumulation, service"),
    3: ("3 Blue", "Water", "Ambition, impulsiveness"),
    4: ("4 Green", "Wood", "Romance, diplomacy"),
    5: ("5 Yellow", "Earth", "Power, centrality"),
    6: ("6 White", "Metal", "Heaven, leadership"),
    7: ("7 Red", "Metal", "Joy, communication"),
    8: ("8 White", "Earth", "Stability, spirituality"),
    9: ("9 Red", "Fire", "Fame, brilliance"),
}

PARKHA = {
    0: ("Kham", "Water", "☵", "Danger, depth"),
    1: ("Li", "Fire", "☲", "Clarity, beauty"),
    2: ("Gin", "Mountain", "☶", "Stillness, meditation"),
    3: ("Da", "Lake", "☱", "Joy, openness"),
    4: ("Khen", "Heaven", "☰", "Strength, creativity"),
    5: ("Zon", "Wind", "☴", "Gentle penetration"),
    6: ("Zin", "Water", "☵", "Danger/depth variant"),
    7: ("Khon", "Earth", "☷", "Receptivity, nurturing"),
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    y = profile.dob.year
    # Tibetan year starts ~Feb, use same cutoff as Chinese
    eff_year = y if profile.dob.month >= 2 else y - 1

    # Mewa: descending cycle. Reference: 1927 = Mewa 1
    mewa_num = ((1927 - eff_year) % 9) + 1
    mewa_name, mewa_elem, mewa_meaning = MEWA[mewa_num]

    # Parkha: 8-year cycle. Reference: 1927 = Parkha Li(1)
    parkha_idx = (eff_year - 1927) % 8
    if parkha_idx < 0:
        parkha_idx += 8
    parkha_name, parkha_elem, parkha_sym, parkha_meaning = PARKHA[parkha_idx]

    return SystemResult(
        id="tibetan_mewa", name="Tibetan Mewa & Parkha",
        certainty="COMPUTED_STRICT",
        data={
            "mewa_number": mewa_num, "mewa_name": mewa_name,
            "mewa_element": mewa_elem, "mewa_meaning": mewa_meaning,
            "parkha_name": parkha_name, "parkha_element": parkha_elem,
            "parkha_symbol": parkha_sym, "parkha_meaning": parkha_meaning,
        },
        interpretation=None, constants_version=constants["version"],
        references=["Tibetan Jungtsi: 9 Mewa (descending) + 8 Parkha (trigrams)"],
        question="Q1_IDENTITY"
    )
