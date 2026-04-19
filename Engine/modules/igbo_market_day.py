"""Igbo Market Day — COMPUTED_STRICT
Days from epoch (Jan 1, 1970 = Eke) mod 4.
Map: 0=Eke(Fire), 1=Orie(Water), 2=Afor(Earth), 3=Nkwo(Air).
Source: Uchendu, Victor C. "The Igbo of Southeast Nigeria", p.45
"""
from __future__ import annotations
from datetime import date
from sirr_core.types import InputProfile, SystemResult

# Igbo 4-day market week
MARKET_DAYS = [
    {"name": "Eke", "element": "Fire", "deity": "Ala (Earth Goddess)", "quality": "creation"},
    {"name": "Orie", "element": "Water", "deity": "Amadioha (Thunder)", "quality": "flow"},
    {"name": "Afor", "element": "Earth", "deity": "Ifejioku (Harvest)", "quality": "stability"},
    {"name": "Nkwo", "element": "Air", "deity": "Anyanwu (Sun)", "quality": "movement"},
]

# Epoch: Jan 1, 1970 = Eke (index 0)
EPOCH = date(1970, 1, 1)


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    dob = profile.dob
    days_from_epoch = (dob - EPOCH).days
    idx = days_from_epoch % 4

    market_day = MARKET_DAYS[idx]

    return SystemResult(
        id="igbo_market_day",
        name="Igbo Market Day",
        certainty="COMPUTED_STRICT",
        data={
            "days_from_epoch": days_from_epoch,
            "market_day": market_day["name"],
            "igbo_element": market_day["element"],
            "deity": market_day["deity"],
            "quality": market_day["quality"],
            "cycle_index": idx,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Uchendu, Victor C. 'The Igbo of Southeast Nigeria', p.45",
            "Igbo Izu (4-day market week): Eke, Orie, Afor, Nkwo",
            "SOURCE_TIER:A — Primary ethnographic text.",
        ],
        question="Q1_IDENTITY",
    )
