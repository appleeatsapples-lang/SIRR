"""Chinese Zodiac (Full) — COMPUTED_STRICT
Computes Heavenly Stem + Earthly Branch + Animal + Element + Yin/Yang.
Uses solar calendar approximation (Lichun ≈ Feb 4).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def _effective_year(profile: InputProfile) -> int:
    """Chinese year starts at Lichun (~Feb 4). Before that, use previous year."""
    y, m, d = profile.dob.year, profile.dob.month, profile.dob.day
    if m < 2 or (m == 2 and d < 4):
        return y - 1
    return y


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    cfg = constants["chinese_zodiac"]
    stems = cfg["heavenly_stems"]
    branches = cfg["earthly_branches"]

    year = _effective_year(profile)
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12

    stem = stems[stem_idx]
    branch = branches[branch_idx]

    pillar_cn = f"{stem['chinese']}{branch['chinese']}"
    pillar_pinyin = f"{stem['pinyin']} {branch['pinyin']}"

    # Zodiac compatibility groups
    trine_group = branch_idx % 4  # 0=Rat/Dragon/Monkey, etc.
    trine_names = {
        0: "Rat, Dragon, Monkey (Doers)",
        1: "Ox, Snake, Rooster (Thinkers)",
        2: "Tiger, Horse, Dog (Protectors)",
        3: "Rabbit, Goat, Pig (Peacemakers)",
    }

    return SystemResult(
        id="chinese_zodiac",
        name="Chinese Zodiac (Full Stem-Branch)",
        certainty="COMPUTED_STRICT",
        data={
            "effective_year": year,
            "heavenly_stem": stem["chinese"],
            "stem_pinyin": stem["pinyin"],
            "stem_element": stem["element"],
            "stem_polarity": stem["polarity"],
            "earthly_branch": branch["chinese"],
            "branch_pinyin": branch["pinyin"],
            "animal": branch["animal"],
            "branch_element": branch["element"],
            "pillar_chinese": pillar_cn,
            "pillar_pinyin": pillar_pinyin,
            "sexagenary_position": ((year - 4) % 60) + 1,
            "trine_group": trine_names.get(trine_group % 4, "Unknown"),
            "note": "Year element from Heavenly Stem. Animal from Earthly Branch. Lichun boundary applied."
        },
        interpretation=f"{year}: {stem['polarity']} {stem['element']} {branch['animal']} ({pillar_cn}). Trine: {trine_names.get(trine_group % 4, '?')}.",
        constants_version=constants["version"],
        references=["Standard Chinese sexagenary cycle", "Heavenly Stems and Earthly Branches"],
        question="Q1_IDENTITY"
    )