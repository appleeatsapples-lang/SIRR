"""Sabian Symbol — LOOKUP_FIXED
Indexing policy: Sabian_ordinal = floor(degree_in_sign) + 1
At exact integer degrees (e.g., 15.000°), floor(15)+1 = 16 (not 15).
Source: Jones (1953), Rudhyar "An Astrological Mandala" — both use 1-30 ordinal.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Approximate solar degree from birth date (no ephemeris needed for degree-level accuracy)
ZODIAC_STARTS = [
    (3, 21, "ARI"), (4, 20, "TAU"), (5, 21, "GEM"), (6, 21, "CAN"),
    (7, 23, "LEO"), (8, 23, "VIR"), (9, 23, "LIB"), (10, 23, "SCO"),
    (11, 22, "SAG"), (12, 22, "CAP"), (1, 20, "AQU"), (2, 19, "PIS")
]

def _approx_solar_sign(month: int, day: int) -> tuple:
    """Returns (sign, degree within sign)."""
    # Simple approximation: Sun moves ~1 degree/day
    signs = [
        (1, 20, "AQU"), (2, 19, "PIS"), (3, 21, "ARI"), (4, 20, "TAU"),
        (5, 21, "GEM"), (6, 21, "CAN"), (7, 23, "LEO"), (8, 23, "VIR"),
        (9, 23, "LIB"), (10, 23, "SCO"), (11, 22, "SAG"), (12, 22, "CAP")
    ]
    # Find which sign
    for i, (sm, sd, sign) in enumerate(signs):
        next_i = (i + 1) % 12
        nm, nd, _ = signs[next_i]
        if sm == month and day >= sd:
            degree = day - sd
            return sign, degree
        if sm == month and day < sd:
            # Previous sign
            prev_i = (i - 1) % 12
            _, _, prev_sign = signs[prev_i]
            return prev_sign, 30 - (sd - day)

    # Fallback for edge cases
    if month == 9 and day == 23:
        return "LIB", 0
    return "UNK", 0

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    sign, degree = _approx_solar_sign(profile.dob.month, profile.dob.day)

    # Sabian ordinal = floor(degree) + 1. Constants use 1-30 range per sign.
    sabian_key = f"{sign}-{degree + 1}"
    symbols = constants["sabian"]["symbols"]
    entry = symbols.get(sabian_key, None)

    data = {
        "solar_sign": sign,
        "solar_degree": degree,
        "sabian_degree": f"{degree}-{degree+1} {sign}",
        "sabian_key": sabian_key,
    }

    if entry:
        data["symbol"] = entry["symbol"]
        data["keynote"] = entry["keynote"]
        data["rudhyar"] = entry.get("rudhyar", "")

    return SystemResult(
        id="sabian",
        name="Sabian Symbol (Solar Degree)",
        certainty="LOOKUP_FIXED",
        data=data,
        interpretation="Approximate solar degree from date. Exact degree needs ephemeris.",
        constants_version=constants["version"],
        references=[constants["sabian"]["source"]],
        question="Q1_IDENTITY"
    )
