"""Aztec Tonalpohualli (260-day count) — COMPUTED_STRICT
Parallel to Mayan Tzolkin: 20 day signs × 13 numbers.
Uses same correlation constant as the engine's Mayan module.
Source: Aztec calendric tradition (Codex Borbonicus, Codex Tonalamatl)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

DAY_SIGNS = [
    "Cipactli (Crocodile)","Ehecatl (Wind)","Calli (House)","Cuetzpalin (Lizard)",
    "Coatl (Serpent)","Miquiztli (Death)","Mazatl (Deer)","Tochtli (Rabbit)",
    "Atl (Water)","Itzcuintli (Dog)","Ozomatli (Monkey)","Malinalli (Grass)",
    "Acatl (Reed)","Ocelotl (Jaguar)","Cuauhtli (Eagle)","Cozcacuauhtli (Vulture)",
    "Ollin (Movement)","Tecpatl (Flint)","Quiahuitl (Rain)","Xochitl (Flower)",
]

# Correlation: Aztec Tonalpohualli aligns with Mayan Tzolkin
# Known ref: Aug 13, 3114 BCE (JDN 584283) = 4 Ahau = Aztec day 160
EPOCH_JDN = 584283
EPOCH_TRECENA = 4
EPOCH_VEINTENA = 20  # Xochitl = index 19 (0-based), but 20th position

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    y, m, d = profile.dob.year, profile.dob.month, profile.dob.day
    a = (14 - m) // 12
    jy = y + 4800 - a
    jm = m + 12 * a - 3
    jdn = d + (153 * jm + 2) // 5 + 365 * jy + jy // 4 - jy // 100 + jy // 400 - 32045

    days = jdn - EPOCH_JDN
    trecena = ((days + EPOCH_TRECENA - 1) % 13) + 1
    veintena = (days + EPOCH_VEINTENA - 1) % 20
    sign = DAY_SIGNS[veintena]

    return SystemResult(
        id="tonalpohualli", name="Aztec Tonalpohualli",
        certainty="COMPUTED_STRICT",
        data={
            "trecena": trecena, "day_sign": sign,
            "day_sign_index": veintena + 1,
            "tonalli": f"{trecena} {sign}",
        },
        interpretation=None, constants_version=constants["version"],
        references=["Aztec Tonalpohualli 260-day count, GMT correlation"],
        question="Q1_IDENTITY"
    )
