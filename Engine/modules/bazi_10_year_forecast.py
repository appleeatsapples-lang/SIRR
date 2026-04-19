"""
BaZi 10-Year Luck Pillar Forecast (大运十年预测)
──────────────────────────────────────────────────
Extends bazi_luck_pillars with element interaction analysis for each
10-year period against the Day Master.

Algorithm (from chinese_african_lookups.json):
  1. Determine yang/yin year stem → forward/backward progression
  2. Find solar term boundary → onset age
  3. Each 10-year pillar: stem+branch → element interaction with Day Master
  4. Score each period: productive/draining/neutral/conflicting

Source: Zi Ping Zhen Quan; San Ming Tong Hui
SOURCE_TIER: A (classical BaZi text)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


STEMS = ["jia", "yi", "bing", "ding", "wu", "ji", "geng", "xin", "ren", "gui"]
BRANCHES = ["zi", "chou", "yin", "mao", "chen", "si",
            "wu_br", "wei", "shen", "you", "xu", "hai"]

STEM_ELEMENT = {
    "jia": "Wood", "yi": "Wood", "bing": "Fire", "ding": "Fire",
    "wu": "Earth", "ji": "Earth", "geng": "Metal", "xin": "Metal",
    "ren": "Water", "gui": "Water",
}

# Pinyin with tone marks → plain pinyin
_TONE_STRIP = {
    "jiǎ": "jia", "yǐ": "yi", "bǐng": "bing", "dīng": "ding",
    "wù": "wu", "jǐ": "ji", "gēng": "geng", "xīn": "xin",
    "rén": "ren", "guǐ": "gui",
    "zǐ": "zi", "chǒu": "chou", "yín": "yin", "mǎo": "mao",
    "chén": "chen", "sì": "si", "wǔ": "wu_br", "wèi": "wei",
    "shēn": "shen", "yǒu": "you", "xū": "xu", "hài": "hai",
}


def _normalize_pinyin(s: str) -> str:
    """Strip tone marks from pinyin and lowercase."""
    lower = s.strip().lower()
    return _TONE_STRIP.get(lower, lower)

BRANCH_ELEMENT = {
    "zi": "Water", "chou": "Earth", "yin": "Wood", "mao": "Wood",
    "chen": "Earth", "si": "Fire", "wu_br": "Fire", "wei": "Earth",
    "shen": "Metal", "you": "Metal", "xu": "Earth", "hai": "Water",
}

STEM_POLARITY = {s: "Yang" if i % 2 == 0 else "Yin" for i, s in enumerate(STEMS)}

# Five element interactions relative to Day Master
PRODUCTION = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CONTROL = {"Wood": "Earth", "Fire": "Metal", "Earth": "Water", "Metal": "Wood", "Water": "Fire"}


def _interaction(dm_element: str, period_element: str) -> str:
    """Determine how period element relates to Day Master."""
    if period_element == dm_element:
        return "companion"
    if PRODUCTION.get(period_element) == dm_element:
        return "resource"  # period produces DM
    if PRODUCTION.get(dm_element) == period_element:
        return "output"  # DM produces period (draining)
    if CONTROL.get(dm_element) == period_element:
        return "wealth"  # DM controls period
    if CONTROL.get(period_element) == dm_element:
        return "authority"  # period controls DM
    return "neutral"


def _score_interaction(interaction: str) -> int:
    """Score: positive = supportive, negative = challenging."""
    return {"companion": 1, "resource": 2, "output": -1, "wealth": 0, "authority": -2, "neutral": 0}.get(interaction, 0)


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    bazi = kwargs.get("bazi_data")
    if not bazi:
        return SystemResult(
            id="bazi_10_year_forecast",
            name="BaZi 10-Year Forecast",
            certainty="NEEDS_INPUT",
            data={"periods": None, "reason": "No BaZi pillar data"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["Zi Ping Zhen Quan"],
            question="Q4_TIMING",
        )

    # Extract Day Master
    day_pillar = bazi.get("day_pillar", {})
    dm_stem = _normalize_pinyin(day_pillar.get("stem_pinyin", ""))
    dm_element = STEM_ELEMENT.get(dm_stem)
    if not dm_element:
        return SystemResult(
            id="bazi_10_year_forecast",
            name="BaZi 10-Year Forecast",
            certainty="NEEDS_INPUT",
            data={"periods": None, "reason": "Cannot determine Day Master element"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["Zi Ping Zhen Quan"],
            question="Q4_TIMING",
        )

    # Year stem polarity + gender → direction
    year_pillar = bazi.get("year_pillar", {})
    year_stem = _normalize_pinyin(year_pillar.get("stem_pinyin", ""))
    year_polarity = STEM_POLARITY.get(year_stem, "Yang")
    gender = profile.gender or "male"
    forward = (year_polarity == "Yang" and gender == "male") or \
              (year_polarity == "Yin" and gender == "female")

    # Month pillar as starting point
    month_pillar = bazi.get("month_pillar", {})
    month_stem = _normalize_pinyin(month_pillar.get("stem_pinyin", ""))
    month_branch = _normalize_pinyin(month_pillar.get("branch_pinyin", ""))

    stem_idx = STEMS.index(month_stem) if month_stem in STEMS else 0
    branch_idx = BRANCHES.index(month_branch) if month_branch in BRANCHES else 0

    # Onset age approximation: count days to next solar term / 3
    # Simplified: use birth day within month as proxy
    onset_age = max(1, (30 - profile.dob.day) // 3) if forward else max(1, profile.dob.day // 3)

    # Generate 8 luck pillars
    periods = []
    for i in range(1, 9):
        if forward:
            s_idx = (stem_idx + i) % 10
            b_idx = (branch_idx + i) % 12
        else:
            s_idx = (stem_idx - i) % 10
            b_idx = (branch_idx - i) % 12

        p_stem = STEMS[s_idx]
        p_branch = BRANCHES[b_idx]
        stem_el = STEM_ELEMENT[p_stem]
        branch_el = BRANCH_ELEMENT[p_branch]

        stem_int = _interaction(dm_element, stem_el)
        branch_int = _interaction(dm_element, branch_el)
        score = _score_interaction(stem_int) + _score_interaction(branch_int)

        start_age = onset_age + (i - 1) * 10
        end_age = start_age + 9

        quality = "supportive" if score > 0 else "challenging" if score < 0 else "neutral"

        periods.append({
            "pillar_number": i,
            "stem": p_stem,
            "branch": p_branch,
            "stem_element": stem_el,
            "branch_element": branch_el,
            "age_range": f"{start_age}-{end_age}",
            "start_age": start_age,
            "stem_interaction": stem_int,
            "branch_interaction": branch_int,
            "score": score,
            "quality": quality,
        })

    # Current period
    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1
    current = None
    for p in periods:
        if p["start_age"] <= age <= p["start_age"] + 9:
            current = p
            break

    return SystemResult(
        id="bazi_10_year_forecast",
        name="BaZi 10-Year Forecast",
        certainty="COMPUTED_STRICT",
        data={
            "day_master": dm_stem,
            "day_master_element": dm_element,
            "direction": "forward" if forward else "backward",
            "onset_age": onset_age,
            "periods": periods,
            "current_period": current,
            "current_age": age,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Zi Ping Zhen Quan", "San Ming Tong Hui", "chinese_african_lookups.json"],
        question="Q4_TIMING",
    )
