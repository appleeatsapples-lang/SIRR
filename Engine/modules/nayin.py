"""NaYin — Chinese Melodic Element — LOOKUP_FIXED
Uses the verified 60-Jiazi table from constants.json (Gemini extraction, cross-checked).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def _sexagenary_position(year: int) -> int:
    """Get 1-60 position in sexagenary cycle."""
    return ((year - 4) % 60) + 1


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    pos = _sexagenary_position(profile.dob.year)
    pos_str = str(pos)

    cycle = constants["nayin"]["cycle"]
    entry = cycle.get(pos_str)

    if entry:
        pillar_cn, pinyin, nayin_en, nayin_cn, element = entry
    else:
        pillar_cn, pinyin, nayin_en, nayin_cn, element = "?", "?", "Unknown", "?", "Unknown"

    # Find the pair partner
    if pos % 2 == 0:
        partner_pos = pos - 1
    else:
        partner_pos = pos + 1
    partner = cycle.get(str(partner_pos), ["?", "?", "?", "?", "?"])

    return SystemResult(
        id="nayin",
        name="NaYin (Chinese Melodic Element / 纳音)",
        certainty="LOOKUP_FIXED",
        data={
            "year": profile.dob.year,
            "sexagenary_position": pos,
            "pillar_chinese": pillar_cn,
            "pillar_pinyin": pinyin,
            "nayin_english": nayin_en,
            "nayin_chinese": nayin_cn,
            "element": element,
            "pair_partner": f"{partner[0]} ({partner[1]})",
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Standard 60 Jiazi NaYin table. Verified against 涧下水 fixture."],
        question="Q3_NATURE"
    )
