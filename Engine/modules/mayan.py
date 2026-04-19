"""Mayan Calendar Systems — G-Lord + Haab + Tzolkin (Traditional Long Count)"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

LORD_NAMES = {
    1: "G1 - Xiuhtecuhtli (Fire Lord)",
    2: "G2 - Tlaltecuhtli (Earth Lord)",
    3: "G3 - Piltzintecuhtli (Young Prince)",
    4: "G4 - Centeotl (Corn God)",
    5: "G5 - Mictlantecuhtli (Death Lord)",
    6: "G6 - Chalchiuhtlicue (Water Goddess)",
    7: "G7 - Tlazolteotl (Purification)",
    8: "G8 - Tepeyollotl (Heart of Mountain)",
    9: "G9 - Tlaloc (Rain God)"
}

HAAB_MONTHS = [
    "Pop","Wo","Sip","Sotz'","Sek","Xul","Yaxk'in","Mol",
    "Ch'en","Yax","Sak","Keh","Mak","K'ank'in","Muwan",
    "Pax","K'ayab","Kumk'u","Wayeb"
]

DAY_SIGNS = [
    "Imix","Ik","Akbal","Kan","Chicchan","Cimi","Manik","Lamat",
    "Muluc","Oc","Chuen","Eb","Ben","Ix","Men","Cib",
    "Caban","Etznab","Cauac","Ahau"
]


def compute(profile: InputProfile, constants: dict, jdn: int) -> SystemResult:
    mc = constants["mayan"]
    gmt = int(mc["gmt_correlation"])  # Standard: 584283

    # Total kin from Mayan epoch (0.0.0.0.0 = 4 Ahau 8 Cumku)
    total_kin = jdn - gmt

    # G-Lord (Lords of the Night): 9-day cycle from epoch
    # Verified: 13.0.0.0.0 (JDN 2456283) → G9 ✓, epoch → G9 ✓
    g = total_kin % 9
    if g == 0:
        g = 9
    g_name = LORD_NAMES.get(g, f"G{g}")

    # Tzolkin (Traditional Long Count, NOT Dreamspell)
    # Epoch 0.0.0.0.0 = 4 Ahau
    # Verified: epoch → 4 Ahau ✓, 13.0.0.0.0 → 4 Ahau ✓
    tzolkin_number = (total_kin + 3) % 13 + 1
    tzolkin_name_idx = (total_kin + 19) % 20
    tzolkin_name = DAY_SIGNS[tzolkin_name_idx]
    tzolkin = f"{tzolkin_number} {tzolkin_name}"

    # Haab (365-day civil calendar)
    haab_off = int(mc["haab_offset"])
    haab_count = (jdn - gmt + haab_off) % 365
    mi = haab_count // 20
    day = haab_count % 20
    month = HAAB_MONTHS[mi] if mi < 18 else "Wayeb"

    return SystemResult(
        id="mayan",
        name="Mayan Calendar (G-Lord + Tzolkin + Haab)",
        certainty="COMPUTED_STRICT",
        data={
            "jdn": jdn,
            "total_kin": total_kin,
            "glord": f"G{g}",
            "glord_name": g_name,
            "tzolkin": tzolkin,
            "tzolkin_number": tzolkin_number,
            "tzolkin_sign": tzolkin_name,
            "tzolkin_sign_index": tzolkin_name_idx,
            "haab_day": day,
            "haab_month": month,
        },
        interpretation=f"Traditional Long Count Tzolkin: {tzolkin}. G-Lord: {g_name}.",
        constants_version=constants["version"],
        references=[
            f"GMT correlation {gmt}",
            "G-Lord: (total_kin % 9), verified against 13.0.0.0.0 → G9",
            "Tzolkin: epoch 4 Ahau, number=(kin+3)%13+1, sign=(kin+19)%20",
            "Note: This is traditional Long Count, NOT Dreamspell/Arguelles",
        ],
        question="Q1_IDENTITY"
    )
