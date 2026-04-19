"""Attitude Number — COMPUTED_STRICT"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    raw = profile.dob.month + profile.dob.day
    reduced = reduce_number(raw)

    meanings = {
        1: "The Leader - assertive first impression",
        2: "The Diplomat - gentle, cooperative energy",
        3: "The Communicator - social, expressive, charming",
        4: "The Builder - solid, reliable, methodical",
        5: "The Magnetic Adventurer - energetic, curious, restless",
        6: "The Nurturer - caring, responsible, harmonious",
        7: "The Mystic - reserved, analytical, deep",
        8: "The Executive - powerful, commanding, confident",
        9: "The Humanitarian - warm, generous, idealistic",
        11: "The Illuminator - intense, visionary, electric",
        22: "The Master Builder - ambitious, grounded vision",
    }

    return SystemResult(
        id="attitude",
        name="Attitude Number",
        certainty="COMPUTED_STRICT",
        data={
            "month": profile.dob.month, "day": profile.dob.day,
            "raw": raw, "reduced": reduced,
            "meaning": meanings.get(reduced, "")
        },
        interpretation="First-impression energy. What people sense immediately.",
        constants_version=constants["version"],
        references=["Attitude = Month + Day, reduced",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q2_MASK"
    )
