"""Egyptian God-of-the-Day — COMPUTED_STRICT

Scholarship fidelity (§4.5 rule 2 — co-occurrence is pattern, not historical
alignment): The Egyptian day-deity, Ethiopian angel, and BaZi Tian Yi Gui Ren
appearing on the same birth date are three tradition-LOCAL protector signatures
co-occurring on one calendar day — NOT evidence of cross-tradition agreement
between Egyptian, Ethiopian, and Chinese metaphysical systems. Resemblance is
pattern; historical tradition-alignment would require textual demonstration.

Egyptian calendar assigned deities to each day of the year.
Uses day-of-year to index into the 36-decan system's deity assignments.
Source: Cairo Calendar / Reconstructed Egyptian day-deity assignments
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# 36 decans × ~10 days each, major deity per decan period
DECAN_DEITIES = [
    (1, "Khnum"), (11, "Hapi"), (21, "Amun"),
    (31, "Khonsu"), (41, "Hathor"), (51, "Isis"),
    (61, "Thoth"), (71, "Anubis"), (81, "Seth"),
    (91, "Bastet"), (101, "Sekhmet"), (111, "Osiris"),
    (121, "Ra"), (131, "Ptah"), (141, "Maat"),
    (151, "Horus"), (161, "Nephthys"), (171, "Sobek"),
    (181, "Nut"), (191, "Geb"), (201, "Shu"),
    (211, "Tefnut"), (221, "Wadjet"), (231, "Renenutet"),
    (241, "Min"), (251, "Serqet"), (261, "Bes"),
    (271, "Taweret"), (281, "Neith"), (291, "Seshat"),
    (301, "Khepri"), (311, "Atum"), (321, "Satis"),
    (331, "Anuket"), (341, "Meretseger"), (351, "Wepwawet"),
    (361, "Sopdet"),  # last 5 epagomenal days
]

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    doy = profile.dob.timetuple().tm_yday
    deity = "Unknown"
    for start, d in reversed(DECAN_DEITIES):
        if doy >= start:
            deity = d
            break

    return SystemResult(
        id="god_of_day", name="Egyptian God-of-the-Day",
        certainty="COMPUTED_STRICT",
        data={
            "day_of_year": doy,
            "deity": deity,
            "dob": str(profile.dob),
            # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
            "scholarship_fidelity": "CLASSICAL",
            "scholarship_note": "Co-occurrence of tradition-local protector signatures on the same day is pattern, not historical alignment.",
        },
        interpretation=None, constants_version=constants["version"],
        references=["Egyptian decan-deity calendar (reconstructed from Cairo Calendar)"],
        question="Q1_IDENTITY"
    )
