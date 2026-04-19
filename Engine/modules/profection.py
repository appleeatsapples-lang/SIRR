"""Annual Profection — COMPUTED_STRICT"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1

    house = (age % 12) + 1
    house_info = constants["profection"]["houses"].get(str(house), "Unknown")

    return SystemResult(
        id="profection",
        name="Annual Profection",
        certainty="COMPUTED_STRICT",
        data={"age": age, "house": house, "house_info": house_info},
        interpretation="Hellenistic timing technique. Pure modular arithmetic.",
        constants_version=constants["version"],
        references=["Profection = (age mod 12) + 1"],
        question="Q4_TIMING"
    )
