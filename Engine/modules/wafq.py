"""Personal Wafq (Magic Square) — LOOKUP_FIXED"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

def compute(profile: InputProfile, constants: dict, base_number: int) -> SystemResult:
    base = constants["wafq"]["loshu_base"]
    offset = (base_number // 3) - 5
    sq = [[cell + offset for cell in row] for row in base]
    return SystemResult(
        id="wafq",
        name="Personal Wafq (Lo Shu offset)",
        certainty="LOOKUP_FIXED",
        data={"base_number": base_number, "offset": offset,
              "square": sq, "row_sum": sum(sq[0]), "center": sq[1][1]},
        interpretation="Lo Shu offset square. Deterministic given base_number.",
        constants_version=constants["version"],
        references=["Lo Shu base from constants.json"],
        question="Q1_IDENTITY"
    )
