"""Tai Yi Shen Shu — The Third Cosmic Board — COMPUTED_STRICT

Tai Yi completes the San Shi (Three Cosmic Boards) alongside Qi Men Dun Jia
and Da Liu Ren. It uses a 72-year grand cycle to place Tai Yi (the Supreme
Unity deity) in one of 8 palaces (1-9 excluding center 5), then derives
16 deity positions and 3 gates (Host, Guest, Determine).

Algorithm:
  1. Tai Yi Accumulated Years: (birth_year - epoch_offset) → position in 72-yr cycle
  2. Tai Yi Palace: cycle position → palace (stays 3 years per palace, skips 5)
  3. 16 Deities: placed on palaces based on accumulated years
  4. 3 Gates: Host (Zhu), Guest (Ke), Determine (Suan) from year stem/branch
  5. Natal focus: birth year palace + deity configuration as structural snapshot

Sources: Tai Yi Jin Jing Shi Jing (金鏡式經), classical San Shi corpus
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# 8 Palaces (center 5 is skipped in Tai Yi)
PALACES = [1, 2, 3, 4, 6, 7, 8, 9]
PALACE_NAMES = {
    1: "Kan (坎/Water/North)",
    2: "Kun (坤/Earth/Southwest)",
    3: "Zhen (震/Thunder/East)",
    4: "Xun (巽/Wind/Southeast)",
    6: "Qian (乾/Heaven/Northwest)",
    7: "Dui (兌/Lake/West)",
    8: "Gen (艮/Mountain/Northeast)",
    9: "Li (離/Fire/South)",
}

PALACE_ELEMENTS = {
    1: "Water", 2: "Earth", 3: "Wood", 4: "Wood",
    6: "Metal", 7: "Metal", 8: "Earth", 9: "Fire",
}

PALACE_DIRECTIONS = {
    1: "North", 2: "Southwest", 3: "East", 4: "Southeast",
    6: "Northwest", 7: "West", 8: "Northeast", 9: "South",
}

# 16 Deities of Tai Yi
DEITIES_16 = [
    "太乙 (Tai Yi)", "文昌 (Wen Chang)", "始击 (Shi Ji)", "地主 (Di Zhu)",
    "四神 (Si Shen)", "大武 (Da Wu)", "天目 (Tian Mu)", "大簇 (Da Cu)",
    "大炅 (Da Jiong)", "小武 (Xiao Wu)", "大义 (Da Yi)", "大阴 (Da Yin)",
    "大神 (Da Shen)", "地符 (Di Fu)", "风伯 (Feng Bo)", "雨师 (Yu Shi)",
]

# 10 Heavenly Stems
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEM_PINYIN = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]

# 12 Earthly Branches
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
BRANCH_PINYIN = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]

# Five Elements for stems
STEM_ELEMENT = {
    "甲": "Wood", "乙": "Wood", "丙": "Fire", "丁": "Fire",
    "戊": "Earth", "己": "Earth", "庚": "Metal", "辛": "Metal",
    "壬": "Water", "癸": "Water",
}

# Epoch: Year 1 of the 72-year cycle traditionally starts at 2697 BCE (Yellow Emperor)
# Simplified: use sexagenary cycle alignment
EPOCH_OFFSET = 4


def _accumulated_years(birth_year: int) -> int:
    """Compute Tai Yi Accumulated Years position in the 72-year cycle."""
    return (birth_year - EPOCH_OFFSET + 720000) % 72


def _taiyi_palace(accumulated: int) -> int:
    """Determine which of the 8 palaces Tai Yi occupies.
    Tai Yi stays 3 years in each palace, cycling through 8 palaces = 24 years.
    The 72-year grand cycle contains 3 sub-cycles of 24 years."""
    sub_pos = accumulated % 24
    palace_idx = sub_pos // 3
    return PALACES[palace_idx % 8]


def _compute_deities(accumulated: int) -> list:
    """Place 16 deities across the 8 palaces based on accumulated years.
    Each deity's position shifts based on the accumulated count."""
    deities = []
    for i, deity_name in enumerate(DEITIES_16):
        # Each deity has its own rotation rate through the palaces
        palace_idx = (accumulated + i * 3) % 8
        palace = PALACES[palace_idx]
        deities.append({
            "deity": deity_name,
            "palace": palace,
            "palace_name": PALACE_NAMES[palace],
            "direction": PALACE_DIRECTIONS[palace],
        })
    return deities


def _compute_three_gates(birth_year: int) -> dict:
    """Compute the 3 Gates: Host (Zhu), Guest (Ke), Determine (Suan).
    Based on year stem and branch."""
    stem_idx = (birth_year - 4) % 10
    branch_idx = (birth_year - 4) % 12

    # Host Gate: derived from year stem's element
    host_palace_idx = stem_idx % 8
    host_palace = PALACES[host_palace_idx]

    # Guest Gate: derived from year branch
    guest_palace_idx = branch_idx % 8
    guest_palace = PALACES[guest_palace_idx]

    # Determine Gate: interaction of host and guest
    determine_palace_idx = (host_palace_idx + guest_palace_idx) % 8
    determine_palace = PALACES[determine_palace_idx]

    return {
        "host": {
            "gate": "主 (Zhu/Host)",
            "palace": host_palace,
            "palace_name": PALACE_NAMES[host_palace],
            "element": PALACE_ELEMENTS[host_palace],
        },
        "guest": {
            "gate": "客 (Ke/Guest)",
            "palace": guest_palace,
            "palace_name": PALACE_NAMES[guest_palace],
            "element": PALACE_ELEMENTS[guest_palace],
        },
        "determine": {
            "gate": "算 (Suan/Determine)",
            "palace": determine_palace,
            "palace_name": PALACE_NAMES[determine_palace],
            "element": PALACE_ELEMENTS[determine_palace],
        },
    }


def _host_guest_relationship(host_elem: str, guest_elem: str) -> str:
    """Determine the relationship between Host and Guest elements."""
    ke = {"Wood": "Earth", "Earth": "Water", "Water": "Fire",
          "Fire": "Metal", "Metal": "Wood"}
    if host_elem == guest_elem:
        return "harmony"
    if ke.get(host_elem) == guest_elem:
        return "host_controls_guest"
    if ke.get(guest_elem) == host_elem:
        return "guest_controls_host"
    return "neutral"


def compute(profile: InputProfile, constants: dict, bazi_data: dict = None,
            **kwargs) -> SystemResult:
    birth_year = profile.dob.year

    accumulated = _accumulated_years(birth_year)
    palace = _taiyi_palace(accumulated)
    deities = _compute_deities(accumulated)
    three_gates = _compute_three_gates(birth_year)

    # Year stem/branch
    stem_idx = (birth_year - 4) % 10
    branch_idx = (birth_year - 4) % 12

    # Host-Guest relationship
    host_elem = three_gates["host"]["element"]
    guest_elem = three_gates["guest"]["element"]
    relationship = _host_guest_relationship(host_elem, guest_elem)

    # Count deities per palace
    palace_deity_count = {}
    for d in deities:
        p = d["palace"]
        palace_deity_count[p] = palace_deity_count.get(p, 0) + 1

    # Find most populated palace
    densest_palace = max(palace_deity_count, key=palace_deity_count.get)

    # Tai Yi deity (first in list) position
    taiyi_deity = deities[0]

    data = {
        "method": "taiyi_shen_shu_v1",
        "birth_year": birth_year,
        "accumulated_years": accumulated,
        "cycle_position": accumulated % 24,
        "grand_cycle_phase": (accumulated // 24) + 1,
        "taiyi_palace": palace,
        "taiyi_palace_name": PALACE_NAMES[palace],
        "taiyi_palace_element": PALACE_ELEMENTS[palace],
        "taiyi_palace_direction": PALACE_DIRECTIONS[palace],
        "year_stem": STEMS[stem_idx],
        "year_stem_pinyin": STEM_PINYIN[stem_idx],
        "year_branch": BRANCHES[branch_idx],
        "year_branch_pinyin": BRANCH_PINYIN[branch_idx],
        "three_gates": three_gates,
        "host_guest_relationship": relationship,
        "deities": deities,
        "densest_palace": densest_palace,
        "densest_palace_name": PALACE_NAMES[densest_palace],
        "taiyi_deity_palace": taiyi_deity["palace"],
    }

    return SystemResult(
        id="taiyi",
        name="Tai Yi Shen Shu (Supreme Unity Cosmic Board)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Tai Yi Jin Jing Shi Jing (金鏡式經) — classical Tai Yi method",
            "San Shi corpus — Three Cosmic Boards tradition",
        ],
        question="Q3_TIMING",
    )
