"""Julian Day Number — COMPUTED_STRICT"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    y, m, d = profile.dob.year, profile.dob.month, profile.dob.day
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    jdn = d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045

    return SystemResult(
        id="julian",
        name="Julian Day Number (Gregorian)",
        certainty="COMPUTED_STRICT",
        data={"jdn": jdn},
        interpretation=None,
        constants_version=constants["version"],
        references=["Gregorian JDN formula (Fliegel-Van Flandern)"],
        question="infrastructure"
    )
