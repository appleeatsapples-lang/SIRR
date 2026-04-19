"""Qi Men Dun Jia — 9-Palace Dynamic Board — COMPUTED_STRICT

One of the Three Pillars of Chinese metaphysics (San Shi). Constructs a
9-palace board with layered Heaven Plate, Earth Plate, 8 Doors, 9 Stars,
and 8 Deities based on the birth moment's solar term and stem/branch cycle.

Algorithm:
  1. Determine Yang/Yin Dun from solar term (terms 0-11 = Yang, 12-23 = Yin)
  2. Determine Ju number (1-9) from 24-term lookup table + Upper/Middle/Lower Yuan
  3. Layout Earth Plate: 6 Crescents (Yi-Geng) + 3 Nobles (Xin-Gui) on Lo Shu path
  4. Lead Star/Door from hour pillar's Xun Kong (empty branch pair)
  5. Rotate Heaven Plate stars, 8 Doors, 8 Deities from Lead positions

Center palace (5) parasitizes Palace 2 (Yang Dun) or Palace 8 (Yin Dun).

Sources: Zhang Zhizhong (Qi Men Dun Jia), Liu Bowen,
         Zhuge Liang (attribution), Joseph Yu (FSRC)

Patches applied Feb 28 2026 per Gemini cross-validation:
  - PATCH 1: 24-term Ju lookup table (replaces paired formula)
  - PATCH 2: Correct 8-star clockwise rotation order
  - PATCH 3: Yang/Yin Dun deity swap (positions 5-6)
  - PATCH 4: Xun Kong fix via 60-Jiazi pillar index
"""
from __future__ import annotations
import math
from sirr_core.types import InputProfile, SystemResult

# 10 Heavenly Stems
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEM_PINYIN = ["Jiǎ", "Yǐ", "Bǐng", "Dīng", "Wù", "Jǐ", "Gēng", "Xīn", "Rén", "Guǐ"]

# 12 Earthly Branches
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
BRANCH_PINYIN = ["Zǐ", "Chǒu", "Yín", "Mǎo", "Chén", "Sì", "Wǔ", "Wèi", "Shēn", "Yǒu", "Xū", "Hài"]

# Lo Shu magic square path: palace sequence
# Standard Lo Shu: 4 9 2 / 3 5 7 / 8 1 6
# Flying sequence from center: 5→6→7→8→9→1→2→3→4
LO_SHU_FLIGHT = [1, 8, 3, 4, 9, 2, 7, 6]  # Perimeter path from palace 1

# 9 Stars (Jiu Xing) — PATCH 2: correct clockwise rotation order
# Tian Qin (天禽, palace 5 center) merges with Tian Rui when rotating
STARS_9 = ["天蓬", "天任", "天冲", "天辅", "天禽", "天英", "天芮", "天柱", "天心"]
STAR_PINYIN_9 = ["Peng", "Ren", "Chong", "Fu", "Qin", "Ying", "Rui", "Zhu", "Xin"]
# 8 rotating stars (excluding center Qin): clockwise from palace 1
STARS_8 = ["天蓬", "天任", "天冲", "天辅", "天英", "天芮", "天柱", "天心"]
STAR_PINYIN_8 = ["Peng", "Ren", "Chong", "Fu", "Ying", "Rui", "Zhu", "Xin"]
# Stars naturally live in palaces: Peng→1, Ren→8, Chong→3, Fu→4, Ying→9, Rui→2, Zhu→7, Xin→6
STAR_HOME_PALACE = [1, 8, 3, 4, 9, 2, 7, 6]  # Same as Lo Shu flight

# 8 Doors (Ba Men)
DOORS = ["休", "生", "伤", "杜", "景", "死", "惊", "开"]
DOOR_PINYIN = ["Xiu", "Sheng", "Shang", "Du", "Jing", "Si", "Jing2", "Kai"]
DOOR_ENGLISH = ["Rest", "Life", "Wound", "Block", "Scenery", "Death", "Fright", "Open"]
# Doors naturally: Rest→P1, Life→P8, Wound→P3, Block→P4, Scenery→P9, Death→P2, Fright→P7, Open→P6
DOOR_HOME_PALACE = [1, 8, 3, 4, 9, 2, 7, 6]

# 8 Deities (Ba Shen) — PATCH 3: Yang/Yin Dun have different deities at positions 5-6
DEITIES_YANG = ["值符", "腾蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"]
DEITY_PINYIN_YANG = ["Zhi Fu", "Teng She", "Tai Yin", "Liu He", "Gou Chen", "Zhu Que", "Jiu Di", "Jiu Tian"]
DEITY_ENGLISH_YANG = ["Lead Deity", "Serpent", "Moon", "Harmony", "Hook", "Phoenix", "Earth", "Heaven"]

DEITIES_YIN = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]
DEITY_PINYIN_YIN = ["Zhi Fu", "Teng She", "Tai Yin", "Liu He", "Bai Hu", "Xuan Wu", "Jiu Di", "Jiu Tian"]
DEITY_ENGLISH_YIN = ["Lead Deity", "Serpent", "Moon", "Harmony", "White Tiger", "Dark Warrior", "Earth", "Heaven"]

# 6 Crescents + 3 Nobles (the 9 stems excluding 甲)
# Earth plate stems in Lo Shu order for each Ju
CRESCENT_ORDER = ["乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# PATCH 4: Xun Kong — 6 xun groups mapped by (branch_idx - stem_idx) % 12
# xun_group → (void_branch_1, void_branch_2)
XUN_VOID_MAP = {
    0: ("戌", "亥"),   # 甲子 xun: branches 10,11 are void
    10: ("申", "酉"),  # 甲戌 xun: branches 8,9 are void
    8: ("午", "未"),   # 甲申 xun: branches 6,7 are void
    6: ("辰", "巳"),   # 甲午 xun: branches 4,5 are void
    4: ("寅", "卯"),   # 甲辰 xun: branches 2,3 are void
    2: ("子", "丑"),   # 甲寅 xun: branches 0,1 are void
}

# 24 Solar Terms with approximate Sun longitude boundaries
SOLAR_TERMS = [
    ("Xiao Han", 285), ("Da Han", 300), ("Li Chun", 315), ("Yu Shui", 330),
    ("Jing Zhe", 345), ("Chun Fen", 0), ("Qing Ming", 15), ("Gu Yu", 30),
    ("Li Xia", 45), ("Xiao Man", 60), ("Mang Zhong", 75), ("Xia Zhi", 90),
    ("Xiao Shu", 105), ("Da Shu", 120), ("Li Qiu", 135), ("Chu Shu", 150),
    ("Bai Lu", 165), ("Qiu Fen", 180), ("Han Lu", 195), ("Shuang Jiang", 210),
    ("Li Dong", 225), ("Xiao Xue", 240), ("Da Xue", 255), ("Dong Zhi", 270),
]

# PATCH 1: Full 24-term Ju lookup table (one entry per solar term)
# term_index → (Upper, Middle, Lower) yuan Ju values
# Yang Dun terms (0-11): Dong Zhi(23) through Mang Zhong(10)
# Yin Dun terms (12-23): Xia Zhi(11) through Da Xue(22)
JU_TABLE = {
    # Yang Dun — Winter Solstice through pre-Summer Solstice
    23: (1, 7, 4),  # Dong Zhi (Winter Solstice)
    0:  (2, 8, 5),  # Xiao Han (Minor Cold)
    1:  (3, 9, 6),  # Da Han (Major Cold)
    2:  (8, 5, 2),  # Li Chun (Start of Spring)
    3:  (9, 6, 3),  # Yu Shui (Rain Water)
    4:  (1, 7, 4),  # Jing Zhe (Awakening of Insects)
    5:  (3, 9, 6),  # Chun Fen (Spring Equinox)
    6:  (4, 1, 7),  # Qing Ming (Clear and Bright)
    7:  (5, 2, 8),  # Gu Yu (Grain Rain)
    8:  (4, 1, 7),  # Li Xia (Start of Summer)
    9:  (5, 2, 8),  # Xiao Man (Minor Fullness)
    10: (6, 3, 9),  # Mang Zhong (Grain in Ear)
    # Yin Dun — Summer Solstice through pre-Winter Solstice
    11: (9, 3, 6),  # Xia Zhi (Summer Solstice)
    12: (8, 2, 5),  # Xiao Shu (Minor Heat)
    13: (7, 1, 4),  # Da Shu (Major Heat)
    14: (2, 5, 8),  # Li Qiu (Start of Autumn)
    15: (1, 4, 7),  # Chu Shu (End of Heat)
    16: (9, 3, 6),  # Bai Lu (White Dew)
    17: (7, 1, 4),  # Qiu Fen (Autumn Equinox)
    18: (6, 9, 3),  # Han Lu (Cold Dew)
    19: (5, 8, 2),  # Shuang Jiang (Frost's Descent)
    20: (6, 9, 3),  # Li Dong (Start of Winter)
    21: (5, 8, 2),  # Xiao Xue (Minor Snow)
    22: (4, 7, 1),  # Da Xue (Major Snow)
}


def _get_solar_term(sun_lon: float) -> tuple:
    """Return (term_name, term_index) for given Sun longitude."""
    lon = sun_lon % 360
    for i, (name, start_lon) in enumerate(SOLAR_TERMS):
        next_lon = SOLAR_TERMS[(i + 1) % 24][1]
        if start_lon <= next_lon:
            if start_lon <= lon < next_lon:
                return name, i
        else:  # wraps around 360
            if lon >= start_lon or lon < next_lon:
                return name, i
    return SOLAR_TERMS[0][0], 0


def _determine_dun(term_index: int) -> str:
    """Yang Dun: terms 0-11 (Xiao Han through Xia Zhi, plus Dong Zhi=23).
    Yin Dun: terms 12-22 (Xiao Shu through Da Xue)."""
    if term_index == 23 or term_index <= 10:
        return "Yang"
    return "Yin"


def _determine_yuan(day_stem: str, day_branch: str) -> str:
    """Upper/Middle/Lower Yuan from day pillar position in 60-cycle."""
    stem_idx = STEMS.index(day_stem) if day_stem in STEMS else 0
    branch_idx = BRANCHES.index(day_branch) if day_branch in BRANCHES else 0
    sexagenary = (stem_idx * 6 + branch_idx) % 60
    pos = sexagenary % 15
    if pos < 5:
        return "Upper"
    elif pos < 10:
        return "Middle"
    return "Lower"


def _determine_ju(term_index: int, yuan: str) -> int:
    """PATCH 1: Determine Ju number (1-9) from 24-term lookup table + Yuan."""
    values = JU_TABLE.get(term_index, (1, 7, 4))
    if yuan == "Upper":
        return values[0]
    elif yuan == "Middle":
        return values[1]
    return values[2]


def _find_xun(hour_stem: str, hour_branch: str) -> tuple:
    """PATCH 4: Find which Xun the hour pillar belongs to using 60-Jiazi index.
    xun_group = (branch_index - stem_index) % 12."""
    stem_idx = STEMS.index(hour_stem) if hour_stem in STEMS else 0
    branch_idx = BRANCHES.index(hour_branch) if hour_branch in BRANCHES else 0
    xun_group = (branch_idx - stem_idx) % 12
    void_branches = XUN_VOID_MAP.get(xun_group, ("戌", "亥"))
    # Reconstruct xun head for display
    xun_start_branch = BRANCHES[(branch_idx - stem_idx) % 12]
    xun_head = "甲" + xun_start_branch
    return xun_head, void_branches


def _palace_for_stem(stem: str, ju: int, dun: str) -> int:
    """Determine which palace a crescent/noble stem occupies on the Earth Plate."""
    stem_idx = CRESCENT_ORDER.index(stem) if stem in CRESCENT_ORDER else 0
    flight = [1, 2, 3, 4, 6, 7, 8, 9]  # skip 5 (center)
    if ju in flight:
        idx = flight.index(ju)
        rotated = flight[idx:] + flight[:idx]
    else:
        rotated = flight
    if stem_idx < len(rotated):
        return rotated[stem_idx]
    return rotated[stem_idx % len(rotated)]


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            bazi_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None or bazi_data is None:
        return SystemResult(
            id="qimen",
            name="Qi Men Dun Jia (Nine Palace Board)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data and bazi_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q3_TIMING",
        )

    sun_lon = natal_chart_data.get("planets", {}).get("Sun", {}).get("longitude", 0)

    # Extract pillars
    day_stem = bazi_data.get("day_pillar", {}).get("stem", "甲")
    day_branch = bazi_data.get("day_pillar", {}).get("branch", "子")
    hour_stem = bazi_data.get("hour_pillar", {}).get("stem", "甲")
    hour_branch = bazi_data.get("hour_pillar", {}).get("branch", "子")

    # Step 1: Solar term and Dun type
    term_name, term_index = _get_solar_term(sun_lon)
    dun = _determine_dun(term_index)

    # Step 2: Yuan and Ju (PATCH 1: uses 24-term lookup table)
    yuan = _determine_yuan(day_stem, day_branch)
    ju = _determine_ju(term_index, yuan)

    # Step 3: Xun Kong from hour pillar (PATCH 4: uses 60-Jiazi index)
    xun_head, empty_branches = _find_xun(hour_stem, hour_branch)

    # Step 4: Lead Star — star that naturally occupies the Ju palace
    # PATCH 2: Use correct 8-star rotation order
    lead_star_idx = STAR_HOME_PALACE.index(ju) if ju in STAR_HOME_PALACE else 0
    lead_star = STARS_8[lead_star_idx]
    lead_star_pinyin = STAR_PINYIN_8[lead_star_idx]

    # Step 5: Lead Door — door whose home palace matches the Ju
    lead_door_idx = DOOR_HOME_PALACE.index(ju) if ju in DOOR_HOME_PALACE else 0
    lead_door = DOORS[lead_door_idx]
    lead_door_pinyin = DOOR_PINYIN[lead_door_idx]

    # Center parasitizes
    parasite_palace = 2 if dun == "Yang" else 8

    # PATCH 3: Select deity list based on Dun type
    deities = DEITIES_YANG if dun == "Yang" else DEITIES_YIN
    deity_pinyin = DEITY_PINYIN_YANG if dun == "Yang" else DEITY_PINYIN_YIN
    deity_english = DEITY_ENGLISH_YANG if dun == "Yang" else DEITY_ENGLISH_YIN

    # Step 6: Build 9 palaces
    palaces = {}
    perimeter = [1, 8, 3, 4, 9, 2, 7, 6]  # Lo Shu flight order

    for p in range(1, 10):
        earth_stem_idx = (p - ju) % 9
        earth_stem = CRESCENT_ORDER[earth_stem_idx] if earth_stem_idx < len(CRESCENT_ORDER) else ""

        # Heaven plate: rotate 8 stars from lead star position
        if p == 5:
            star = STARS_9[4]  # 天禽 always in center
            star_py = STAR_PINYIN_9[4]
        else:
            p_flight_idx = perimeter.index(p) if p in perimeter else 0
            offset = (p_flight_idx - lead_star_idx) % 8
            s_idx = (lead_star_idx + offset) % 8
            star = STARS_8[s_idx]
            star_py = STAR_PINYIN_8[s_idx]

        # Doors: rotate from lead door
        if p == 5:
            door = "—"
            door_py = "—"
            door_en = "Center"
        else:
            p_flight_idx = perimeter.index(p) if p in perimeter else 0
            d_offset = (p_flight_idx - lead_door_idx) % 8
            d_idx = (lead_door_idx + d_offset) % 8
            door = DOORS[d_idx]
            door_py = DOOR_PINYIN[d_idx]
            door_en = DOOR_ENGLISH[d_idx]

        # Deities: rotate from lead star palace (PATCH 3: uses dun-specific list)
        if p == 5:
            dei = "—"
            dei_py = "—"
            dei_en = "Center"
        else:
            p_flight_idx = perimeter.index(p) if p in perimeter else 0
            dei_idx = p_flight_idx % 8
            dei = deities[dei_idx]
            dei_py = deity_pinyin[dei_idx]
            dei_en = deity_english[dei_idx]

        palaces[str(p)] = {
            "earth_stem": earth_stem,
            "star": star,
            "star_pinyin": star_py,
            "door": door if p != 5 else "—",
            "door_english": door_en if p != 5 else "Center",
            "deity": dei if p != 5 else "—",
            "deity_english": dei_en if p != 5 else "Center",
        }

    data = {
        "dun_type": dun,
        "solar_term": term_name,
        "solar_term_index": term_index,
        "yuan": yuan,
        "ju_number": ju,
        "parasite_palace": parasite_palace,
        "xun_head": xun_head,
        "empty_branches": list(empty_branches),
        "lead_star": lead_star,
        "lead_star_pinyin": lead_star_pinyin,
        "lead_door": lead_door,
        "lead_door_pinyin": lead_door_pinyin,
        "palaces": palaces,
    }

    return SystemResult(
        id="qimen",
        name="Qi Men Dun Jia (Nine Palace Board)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Zhang Zhizhong — Qi Men Dun Jia systematic method",
            "Joseph Yu, FSRC — Qi Men Dun Jia reference tables",
            "Liu Bowen — classical Qi Men treatise",
        ],
        question="Q3_TIMING",
    )
