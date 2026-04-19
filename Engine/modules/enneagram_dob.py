"""Enneagram from DOB — COMPUTED_STRICT
Derives Enneagram type from date of birth using digital root method.
DOB digits summed and reduced to 1-9. Type 9 maps to the Peacemaker.
Note: This is a numerological derivation, not the psychological assessment.
Source: Various numerology-Enneagram crossover systems
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

TYPES = {
    1: ("Reformer", "Principled, purposeful, self-controlled, perfectionist"),
    2: ("Helper", "Generous, demonstrative, people-pleasing, possessive"),
    3: ("Achiever", "Adaptable, excelling, driven, image-conscious"),
    4: ("Individualist", "Expressive, dramatic, self-absorbed, temperamental"),
    5: ("Investigator", "Perceptive, innovative, secretive, isolated"),
    6: ("Loyalist", "Engaging, responsible, anxious, suspicious"),
    7: ("Enthusiast", "Spontaneous, versatile, acquisitive, scattered"),
    8: ("Challenger", "Self-confident, decisive, willful, confrontational"),
    9: ("Peacemaker", "Receptive, reassuring, complacent, resigned"),
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    d = profile.dob
    raw = sum(int(ch) for ch in f"{d.year}{d.month:02d}{d.day:02d}")
    reduced = reduce_number(raw, keep_masters=())  # 1-9 only for Enneagram

    etype, edesc = TYPES.get(reduced, ("Unknown", ""))

    return SystemResult(
        id="enneagram_dob",
        name="Enneagram from DOB",
        certainty="COMPUTED_STRICT",
        data={
            "raw_sum": raw,
            "enneagram_type": reduced,
            "type_name": etype,
            "type_description": edesc,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["DOB digital root → Enneagram type mapping",
                    "SOURCE_TIER:C — DOB-based type assignment is post-1980s community addition. No classical lineage."],
        question="Q1_IDENTITY"
    )
