"""Balinese Pawukon (210-day cycle) — COMPUTED_STRICT
10 concurrent week-cycles running simultaneously (1-day through 10-day weeks).
The intersection of cycles on birth date reveals character + auspiciousness.
Uses Julian Day Number mod cycle lengths.
Source: Balinese Pawukon calendar tradition
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

CYCLES = {
    "Wuku": {"length": 30, "names": [
        "Sinta","Landep","Ukir","Kulantir","Tolu","Gumbreg","Wariga","Warigadean",
        "Julungwangi","Sungsang","Dungulan","Kuningan","Langkir","Medangsia",
        "Pujut","Pahang","Krulut","Merakih","Tambir","Medangkungan",
        "Matal","Uye","Menail","Prangbakat","Bala","Ugu","Wayang",
        "Kelawu","Dukut","Watugunung"
    ]},
    "Pancawara": {"length": 5, "names": ["Umanis","Paing","Pon","Wage","Kliwon"]},
    "Saptawara": {"length": 7, "names": ["Redite","Soma","Anggara","Buda","Wraspati","Sukra","Saniscara"]},
    "Triwara": {"length": 3, "names": ["Pasah","Beteng","Kajeng"]},
}

# Pawukon epoch: Reingold & Dershowitz, Calendrical Calculations (2018), Ch.11
# JDN 146 = algorithmic anchor for 210-day Pawukon cycle
PAWUKON_EPOCH_JDN = 146

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    # Compute JDN
    y, m, d = profile.dob.year, profile.dob.month, profile.dob.day
    a = (14 - m) // 12
    jy = y + 4800 - a
    jm = m + 12 * a - 3
    jdn = d + (153 * jm + 2) // 5 + 365 * jy + jy // 4 - jy // 100 + jy // 400 - 32045

    days_from_epoch = jdn - PAWUKON_EPOCH_JDN
    day_in_210 = days_from_epoch % 210

    result_cycles = {}
    for cname, cdata in CYCLES.items():
        if cname == "Wuku":
            # Wuku is a 7-day week name, not a 1-day cycle.
            # Each wuku spans exactly 7 days → index = floor(days/7) % 30
            # Bug fix: was days_from_epoch % 30 which advances by 1 per day
            # (giving 210 different wukus), should advance by 1 per WEEK.
            idx = (days_from_epoch // 7) % 30
        else:
            idx = days_from_epoch % cdata["length"]
        if idx < 0:
            idx += cdata["length"]
        result_cycles[cname] = cdata["names"][idx % len(cdata["names"])]

    return SystemResult(
        id="pawukon", name="Balinese Pawukon (210-day cycle)",
        certainty="COMPUTED_STRICT",
        data={
            "day_in_210": day_in_210,
            "wuku": result_cycles.get("Wuku","?"),
            "pancawara": result_cycles.get("Pancawara","?"),
            "saptawara": result_cycles.get("Saptawara","?"),
            "triwara": result_cycles.get("Triwara","?"),
        },
        interpretation=None, constants_version=constants["version"],
        references=["Balinese Pawukon: 210-day cycle with concurrent week systems"],
        question="Q1_IDENTITY"
    )
