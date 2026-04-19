"""Da Liu Ren — 12-Branch Rotating Plate System — COMPUTED_STRICT

One of the Three Pillars of Chinese metaphysics. Constructs a Heaven Plate
from the Monthly General (Yue Jiang, derived from Sun longitude) placed on
the hour branch, then derives Four Lessons (Si Ke) from day stem/branch
overlays and Three Transmissions (San Chuan) from conflict rules.

Algorithm:
  1. Monthly General: Sun longitude → Earthly Branch
  2. Heaven Plate: place General on hour branch, rotate all 12 branches
  3. Four Lessons: day stem's parasitic branch → what's above on Heaven Plate
  4. Three Transmissions: Ze Ke (conflict selection) → 3-step derivation

Sources: Da Liu Ren Shen Jiang Zhi Nan, Shao Weihua,
         Classical Chinese Divination (Ho Peng Yoke)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# 12 Earthly Branches
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
BRANCH_PINYIN = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]

# 10 Heavenly Stems
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEM_PINYIN = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]

# Day Stem → Parasitic Branch (寄宫)
STEM_PARASITIC = {
    "甲": "寅", "乙": "辰", "丙": "巳", "丁": "未",
    "戊": "巳", "己": "未", "庚": "申", "辛": "戌",
    "壬": "亥", "癸": "丑",
}

# PATCH 5: Monthly General (月将 Yue Jiang): tropical Sun longitude → Earthly Branch
# Corrected mapping per Gemini cross-validation (Feb 28 2026)
# Each 30° sector of tropical Sun longitude maps to a specific branch
MONTHLY_GENERALS = [
    (0, 30, "戌"),      # Aries → Xu
    (30, 60, "酉"),     # Taurus → You
    (60, 90, "申"),     # Gemini → Shen
    (90, 120, "未"),    # Cancer → Wei
    (120, 150, "午"),   # Leo → Wu
    (150, 180, "巳"),   # Virgo → Si
    (180, 210, "辰"),   # Libra → Chen
    (210, 240, "卯"),   # Scorpio → Mao
    (240, 270, "寅"),   # Sagittarius → Yin
    (270, 300, "丑"),   # Capricorn → Chou
    (300, 330, "子"),   # Aquarius → Zi
    (330, 360, "亥"),   # Pisces → Hai
]

# Wu Xing (Five Elements) for branches
BRANCH_ELEMENT = {
    "子": "Water", "丑": "Earth", "寅": "Wood", "卯": "Wood",
    "辰": "Earth", "巳": "Fire", "午": "Fire", "未": "Earth",
    "申": "Metal", "酉": "Metal", "戌": "Earth", "亥": "Water",
}

# Ke (control/克) relationships: controller → controlled
KE_PAIRS = {
    "Wood": "Earth", "Earth": "Water", "Water": "Fire",
    "Fire": "Metal", "Metal": "Wood",
}


def _get_monthly_general(sun_lon: float) -> str:
    """Map Sun longitude to Monthly General branch."""
    lon = sun_lon % 360
    for start, end, branch in MONTHLY_GENERALS:
        if start <= end:
            if start <= lon < end:
                return branch
        else:  # wraps 360
            if lon >= start or lon < end:
                return branch
    return "戌"  # default


def _build_heaven_plate(general: str, hour_branch: str) -> dict:
    """Place Monthly General on hour branch, rotate all 12 branches accordingly.
    Returns mapping: earth_position (branch) → heaven_branch above it."""
    general_idx = BRANCHES.index(general)
    hour_idx = BRANCHES.index(hour_branch)
    offset = general_idx - hour_idx  # How much to shift

    plate = {}
    for i, earth_branch in enumerate(BRANCHES):
        heaven_idx = (i + offset) % 12
        plate[earth_branch] = BRANCHES[heaven_idx]
    return plate


def _heaven_above(plate: dict, earth_branch: str) -> str:
    """What branch is above the given earth branch on the heaven plate."""
    return plate.get(earth_branch, earth_branch)


def _has_ke(upper_elem: str, lower_elem: str) -> bool:
    """Check if upper element controls (ke) lower element."""
    return KE_PAIRS.get(upper_elem) == lower_elem


def _derive_four_lessons(day_stem: str, day_branch: str, plate: dict) -> list:
    """Derive the 4 lessons (Si Ke) from day stem parasitic branch and heaven plate."""
    parasitic = STEM_PARASITIC.get(day_stem, "子")

    lessons = []

    # Lesson 1: What's above the day stem's parasitic branch
    above_1 = _heaven_above(plate, parasitic)
    lessons.append({
        "lesson": 1,
        "lower": parasitic,
        "lower_pinyin": BRANCH_PINYIN[BRANCHES.index(parasitic)],
        "upper": above_1,
        "upper_pinyin": BRANCH_PINYIN[BRANCHES.index(above_1)],
        "lower_element": BRANCH_ELEMENT[parasitic],
        "upper_element": BRANCH_ELEMENT[above_1],
    })

    # Lesson 2: What's above lesson 1's result
    above_2 = _heaven_above(plate, above_1)
    lessons.append({
        "lesson": 2,
        "lower": above_1,
        "lower_pinyin": BRANCH_PINYIN[BRANCHES.index(above_1)],
        "upper": above_2,
        "upper_pinyin": BRANCH_PINYIN[BRANCHES.index(above_2)],
        "lower_element": BRANCH_ELEMENT[above_1],
        "upper_element": BRANCH_ELEMENT[above_2],
    })

    # Lesson 3: What's above the day branch
    above_3 = _heaven_above(plate, day_branch)
    lessons.append({
        "lesson": 3,
        "lower": day_branch,
        "lower_pinyin": BRANCH_PINYIN[BRANCHES.index(day_branch)],
        "upper": above_3,
        "upper_pinyin": BRANCH_PINYIN[BRANCHES.index(above_3)],
        "lower_element": BRANCH_ELEMENT[day_branch],
        "upper_element": BRANCH_ELEMENT[above_3],
    })

    # Lesson 4: What's above lesson 3's result
    above_4 = _heaven_above(plate, above_3)
    lessons.append({
        "lesson": 4,
        "lower": above_3,
        "lower_pinyin": BRANCH_PINYIN[BRANCHES.index(above_3)],
        "upper": above_4,
        "upper_pinyin": BRANCH_PINYIN[BRANCHES.index(above_4)],
        "lower_element": BRANCH_ELEMENT[above_3],
        "upper_element": BRANCH_ELEMENT[above_4],
    })

    return lessons


def _derive_three_transmissions(lessons: list, plate: dict) -> list:
    """Derive the 3 transmissions (San Chuan) using Ze Ke priority.

    Ze Ke: select the lesson where upper controls (ke) lower.
    If multiple ke: prefer lessons 3-4 (branch-based) over 1-2 (stem-based).
    If no ke: use lesson 4's upper as initial transmission (She method).
    """
    # Find lessons with ke relationship
    ke_lessons = []
    for lesson in lessons:
        if _has_ke(lesson["upper_element"], lesson["lower_element"]):
            ke_lessons.append(lesson)

    if ke_lessons:
        # Prefer later lessons (branch-based)
        selected = ke_lessons[-1]
    else:
        # She method: use lesson 4
        selected = lessons[3]

    # Initial transmission: upper of selected lesson
    initial = selected["upper"]
    initial_idx = BRANCHES.index(initial)

    # Middle transmission: what's above the initial on the heaven plate
    middle = _heaven_above(plate, initial)

    # Final transmission: what's above the middle on the heaven plate
    final = _heaven_above(plate, middle)

    transmissions = [
        {
            "position": "initial",
            "branch": initial,
            "branch_pinyin": BRANCH_PINYIN[BRANCHES.index(initial)],
            "element": BRANCH_ELEMENT[initial],
            "source": f"Lesson {selected['lesson']} upper",
        },
        {
            "position": "middle",
            "branch": middle,
            "branch_pinyin": BRANCH_PINYIN[BRANCHES.index(middle)],
            "element": BRANCH_ELEMENT[middle],
        },
        {
            "position": "final",
            "branch": final,
            "branch_pinyin": BRANCH_PINYIN[BRANCHES.index(final)],
            "element": BRANCH_ELEMENT[final],
        },
    ]
    return transmissions


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            bazi_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None or bazi_data is None:
        return SystemResult(
            id="liu_ren",
            name="Da Liu Ren (12-Branch Rotating Plate)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data and bazi_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q3_TIMING",
        )

    sun_lon = natal_chart_data.get("planets", {}).get("Sun", {}).get("longitude", 0)

    # Extract day and hour pillar data
    day_stem = bazi_data.get("day_pillar", {}).get("stem", "甲")
    day_branch = bazi_data.get("day_pillar", {}).get("branch", "子")
    hour_branch = bazi_data.get("hour_pillar", {}).get("branch", "子")

    # Step 1: Monthly General
    general = _get_monthly_general(sun_lon)
    general_idx = BRANCHES.index(general)

    # Step 2: Build Heaven Plate
    plate = _build_heaven_plate(general, hour_branch)

    # Format plate for output: earth → heaven mapping
    heaven_plate = {}
    for eb in BRANCHES:
        hb = plate[eb]
        eb_idx = BRANCHES.index(eb)
        hb_idx = BRANCHES.index(hb)
        heaven_plate[eb] = {
            "heaven_branch": hb,
            "heaven_pinyin": BRANCH_PINYIN[hb_idx],
            "earth_pinyin": BRANCH_PINYIN[eb_idx],
        }

    # Step 3: Four Lessons
    four_lessons = _derive_four_lessons(day_stem, day_branch, plate)

    # Step 4: Three Transmissions
    three_transmissions = _derive_three_transmissions(four_lessons, plate)

    # Summary: dominant element in transmissions
    trans_elements = [t["element"] for t in three_transmissions]
    element_counts = {}
    for e in trans_elements:
        element_counts[e] = element_counts.get(e, 0) + 1
    dominant = max(element_counts, key=element_counts.get)

    data = {
        "monthly_general": general,
        "monthly_general_pinyin": BRANCH_PINYIN[general_idx],
        "day_stem": day_stem,
        "day_stem_pinyin": STEM_PINYIN[STEMS.index(day_stem)] if day_stem in STEMS else "",
        "day_branch": day_branch,
        "hour_branch": hour_branch,
        "heaven_plate": heaven_plate,
        "four_lessons": four_lessons,
        "three_transmissions": three_transmissions,
        "transmission_elements": trans_elements,
        "dominant_element": dominant,
    }

    return SystemResult(
        id="liu_ren",
        name="Da Liu Ren (12-Branch Rotating Plate)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Da Liu Ren Shen Jiang Zhi Nan — classical method",
            "Shao Weihua — Liu Ren systematic reference",
            "Ho Peng Yoke, Chinese Mathematical Astrology — Liu Ren analysis",
        ],
        question="Q3_TIMING",
    )
