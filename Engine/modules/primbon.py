"""Javanese Primbon / Weton — COMPUTED_STRICT
Combines 5-day Pasaran cycle with 7-day week. The Neptu sum determines
character and compatibility. Each day pair has a specific Neptu value.
Source: Javanese Primbon divination tradition
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

PASARAN = ["Legi","Pahing","Pon","Wage","Kliwon"]
PASARAN_NEPTU = {"Legi":5,"Pahing":9,"Pon":7,"Wage":4,"Kliwon":8}
WEEKDAY_NAMES = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
WEEKDAY_NEPTU = {"Senin":4,"Selasa":3,"Rabu":7,"Kamis":8,"Jumat":6,"Sabtu":9,"Minggu":5}

# Pasaran cycle: verified against Aug 17, 1945 = JDN 2431685 = Friday Legi
# (Indonesian Independence Day, universally documented as Jumat Legi)
# Direct method: JDN % 5 gives Pasaran index.
# Mapping: 0=Legi, 1=Pahing, 2=Pon, 3=Wage, 4=Kliwon
# Note: Gemini provided JDN 2431457 for Aug 17 1945 which is WRONG (off by 228).
# Correct JDN verified against Jan 1 2000 = JDN 2451545.
PASARAN_EPOCH_JDN = 2431685  # Aug 17 1945 = Legi. Any JDN where (JDN-EPOCH)%5=0 is Legi.

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    y, m, d = profile.dob.year, profile.dob.month, profile.dob.day
    a = (14 - m) // 12
    jy = y + 4800 - a
    jm = m + 12 * a - 3
    jdn = d + (153 * jm + 2) // 5 + 365 * jy + jy // 4 - jy // 100 + jy // 400 - 32045

    pasaran_idx = (jdn - PASARAN_EPOCH_JDN) % 5
    if pasaran_idx < 0:
        pasaran_idx += 5
    pasaran = PASARAN[pasaran_idx]

    weekday_idx = profile.dob.weekday()  # Mon=0
    # Convert to Javanese: Mon=Senin(0)...Sun=Minggu(6)
    weekday = WEEKDAY_NAMES[weekday_idx]

    neptu = PASARAN_NEPTU[pasaran] + WEEKDAY_NEPTU[weekday]
    weton = f"{weekday} {pasaran}"

    return SystemResult(
        id="primbon", name="Javanese Primbon / Weton",
        certainty="COMPUTED_STRICT",
        data={
            "weton": weton, "weekday": weekday, "pasaran": pasaran,
            "neptu_sum": neptu,
            "weekday_neptu": WEEKDAY_NEPTU[weekday],
            "pasaran_neptu": PASARAN_NEPTU[pasaran],
        },
        interpretation=None, constants_version=constants["version"],
        references=["Javanese Primbon: 5-day Pasaran + 7-day week, Neptu sum"],
        question="Q1_IDENTITY"
    )
