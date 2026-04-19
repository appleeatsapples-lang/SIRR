"""Hebrew Albam Cipher — COMPUTED_STRICT"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    albam_cfg = constants["albam"]
    cipher = albam_cfg["map"]
    values = constants["atbash"]["values"]  # reuse value table

    hebrew_letters = [("mem", 40), ("vav", 6), ("he", 5), ("bet", 2)]
    original_sum = sum(v for _, v in hebrew_letters)
    transformed = [(cipher[name], values[cipher[name]]) for name, _ in hebrew_letters]
    albam_sum = sum(v for _, v in transformed)
    albam_root = reduce_number(albam_sum, keep_masters=())

    return SystemResult(
        id="albam",
        name="Hebrew Albam (Split-Alphabet Cipher)",
        certainty="COMPUTED_STRICT",
        data={
            "original_sum": original_sum,
            "transformed_letters": [(n, v) for n, v in transformed],
            "albam_sum": albam_sum,
            "albam_root": albam_root
        },
        interpretation="Deterministic cipher. Second Kabbalistic transformation method.",
        constants_version=constants["version"],
        references=["Standard Hebrew Albam table"],
        question="Q1_IDENTITY"
    )
