"""Zoroastrian Day Yazata — LOOKUP_FIXED
Convert Gregorian DOB to Zoroastrian Fasli calendar (fixed 365-day + leap).
Extract day name (1-30 Roj/Yazata). Map to divine association + elemental traits.
Source: Zoroastrian Avestan/Pahlavi calendar texts
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# 30 Roj (day) names with Yazata (divine being) and element associations
YAZATAS = [
    {"roj": 1, "name": "Ohrmazd", "yazata": "Ahura Mazda", "element": "All/Light", "domain": "Creation, wisdom"},
    {"roj": 2, "name": "Bahman", "yazata": "Vohu Manah", "element": "Air", "domain": "Good mind, cattle"},
    {"roj": 3, "name": "Ardibehesht", "yazata": "Asha Vahishta", "element": "Fire", "domain": "Truth, righteousness"},
    {"roj": 4, "name": "Shahrevar", "yazata": "Khshathra Vairya", "element": "Metal", "domain": "Desirable dominion"},
    {"roj": 5, "name": "Spandarmad", "yazata": "Spenta Armaiti", "element": "Earth", "domain": "Holy devotion"},
    {"roj": 6, "name": "Khordad", "yazata": "Haurvatat", "element": "Water", "domain": "Wholeness, health"},
    {"roj": 7, "name": "Amordad", "yazata": "Ameretat", "element": "Wood/Plant", "domain": "Immortality"},
    {"roj": 8, "name": "Dae-pa-Adar", "yazata": "Dadvah (Creator)", "element": "Fire", "domain": "Creator aspect"},
    {"roj": 9, "name": "Adar", "yazata": "Atar (Fire)", "element": "Fire", "domain": "Sacred fire"},
    {"roj": 10, "name": "Aban", "yazata": "Apam Napat", "element": "Water", "domain": "Waters"},
    {"roj": 11, "name": "Khorshed", "yazata": "Hvare Khshaeta", "element": "Fire", "domain": "Sun"},
    {"roj": 12, "name": "Mohor", "yazata": "Mah (Moon)", "element": "Water", "domain": "Moon"},
    {"roj": 13, "name": "Tir", "yazata": "Tishtrya", "element": "Water", "domain": "Star Sirius, rain"},
    {"roj": 14, "name": "Gosh", "yazata": "Geush Urvan", "element": "Earth", "domain": "Soul of the Ox"},
    {"roj": 15, "name": "Dae-pa-Meher", "yazata": "Dadvah (Creator)", "element": "Fire", "domain": "Creator aspect"},
    {"roj": 16, "name": "Meher", "yazata": "Mithra", "element": "Fire", "domain": "Covenant, light"},
    {"roj": 17, "name": "Srosh", "yazata": "Sraosha", "element": "Air", "domain": "Obedience, prayer"},
    {"roj": 18, "name": "Rashne", "yazata": "Rashnu", "element": "Air", "domain": "Justice, judgment"},
    {"roj": 19, "name": "Fravardin", "yazata": "Fravashis", "element": "All", "domain": "Guardian spirits"},
    {"roj": 20, "name": "Behram", "yazata": "Verethraghna", "element": "Fire", "domain": "Victory"},
    {"roj": 21, "name": "Ram", "yazata": "Raman", "element": "Air", "domain": "Joy, peace"},
    {"roj": 22, "name": "Govad", "yazata": "Vayu", "element": "Air", "domain": "Wind"},
    {"roj": 23, "name": "Dae-pa-Din", "yazata": "Dadvah (Creator)", "element": "Fire", "domain": "Creator aspect"},
    {"roj": 24, "name": "Din", "yazata": "Daena", "element": "Air", "domain": "Religion, conscience"},
    {"roj": 25, "name": "Ashishvangh", "yazata": "Ashi", "element": "Earth", "domain": "Blessing, reward"},
    {"roj": 26, "name": "Ashtad", "yazata": "Arshtat", "element": "Earth", "domain": "Rectitude"},
    {"roj": 27, "name": "Asman", "yazata": "Asman", "element": "Air", "domain": "Sky"},
    {"roj": 28, "name": "Zamyad", "yazata": "Zam", "element": "Earth", "domain": "Earth"},
    {"roj": 29, "name": "Mahraspand", "yazata": "Manthra Spenta", "element": "Air", "domain": "Holy Word"},
    {"roj": 30, "name": "Aneran", "yazata": "Anaghra Raochah", "element": "Fire", "domain": "Endless Light"},
]

# Fasli calendar months (each 30 days, except last month has 5-6 Gatha days)
# Fasli New Year = March 21 (Nowruz)
FASLI_MONTH_STARTS = [
    (3, 21),   # 1. Farvardin
    (4, 20),   # 2. Ardibehesht
    (5, 20),   # 3. Khordad
    (6, 19),   # 4. Tir
    (7, 19),   # 5. Amordad
    (8, 18),   # 6. Shahrevar
    (9, 17),   # 7. Mehr
    (10, 17),  # 8. Aban
    (11, 16),  # 9. Azar
    (12, 16),  # 10. Dey
    (1, 15),   # 11. Bahman
    (2, 14),   # 12. Esfand (then 5 Gatha days)
]


def _fasli_day(dob):
    """Get Fasli calendar day (1-30) from Gregorian DOB."""
    m, d = dob.month, dob.day

    # Find which Fasli month we're in
    for i in range(len(FASLI_MONTH_STARTS) - 1, -1, -1):
        fm, fd = FASLI_MONTH_STARTS[i]
        if (m, d) >= (fm, fd):
            # Day within this Fasli month
            from datetime import date as dt
            start = dt(dob.year if fm <= m else dob.year - 1, fm, fd)
            day_in_month = (dob - start).days + 1
            if day_in_month <= 30:
                return day_in_month
            else:
                return ((day_in_month - 1) % 30) + 1  # Gatha days wrap
            break
    # Before Jan 15 = still in Bahman (month 11)
    from datetime import date as dt
    start = dt(dob.year - 1, 1, 15)
    day_in_month = (dob - start).days + 1
    return min(day_in_month, 30)


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    roj = _fasli_day(profile.dob)
    roj_idx = max(0, min(roj - 1, 29))  # 0-indexed, clamp to valid range
    yazata = YAZATAS[roj_idx]

    return SystemResult(
        id="zoroastrian_day_yazata",
        name="Zoroastrian Day Yazata",
        certainty="LOOKUP_FIXED",
        data={
            "roj_number": yazata["roj"],
            "roj_name": yazata["name"],
            "yazata_name": yazata["yazata"],
            "yazata_element": yazata["element"],
            "yazata_domain": yazata["domain"],
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Zoroastrian Fasli calendar: 12 months × 30 days + 5 Gatha days",
            "Avestan Roj (day) names and Yazata associations",
            "SOURCE_TIER:A — Avestan/Pahlavi calendar texts.",
        ],
        question="Q1_IDENTITY",
    )
