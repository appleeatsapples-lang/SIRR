"""Onmyōdō (陰陽道) — Japanese Yin-Yang Five-Element System — COMPUTED_STRICT

The Way of Yin and Yang: Japan's syncretic cosmological system combining
Chinese Wu Xing (Five Elements), Yin-Yang classification, directional
deities (12 Heavenly Generals), and calendrical day-quality assessment.

Algorithm:
  1. Classify birth year, month, day via Yin-Yang polarity (stem/branch)
  2. Determine birth element from Heavenly Stem (Jikkan)
  3. Map birth to one of 12 Directional Deities (Jūni Shō)
  4. Compute Roku-Yō (六曜) — six-day fortune cycle
  5. Determine Eto (干支) — Japanese sexagenary cycle animal + element
  6. Assess directional quality (Kippō/Kata-imi)

Sources: Seimei-reki (晴明暦), Onmyō-ryō historical records,
         Abe no Seimei tradition
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Jikkan (十干) — 10 Heavenly Stems with Japanese readings
JIKKAN = [
    ("甲", "Kinoe", "Wood+"),
    ("乙", "Kinoto", "Wood-"),
    ("丙", "Hinoe", "Fire+"),
    ("丁", "Hinoto", "Fire-"),
    ("戊", "Tsuchinoe", "Earth+"),
    ("己", "Tsuchinoto", "Earth-"),
    ("庚", "Kanoe", "Metal+"),
    ("辛", "Kanoto", "Metal-"),
    ("壬", "Mizunoe", "Water+"),
    ("癸", "Mizunoto", "Water-"),
]

# Jūnishi (十二支) — 12 Earthly Branches with Japanese readings
JUNISHI = [
    ("子", "Ne", "Rat"),
    ("丑", "Ushi", "Ox"),
    ("寅", "Tora", "Tiger"),
    ("卯", "U", "Rabbit"),
    ("辰", "Tatsu", "Dragon"),
    ("巳", "Mi", "Snake"),
    ("午", "Uma", "Horse"),
    ("未", "Hitsuji", "Sheep"),
    ("申", "Saru", "Monkey"),
    ("酉", "Tori", "Rooster"),
    ("戌", "Inu", "Dog"),
    ("亥", "I", "Boar"),
]

# Roku-Yō (六曜) — Six-day fortune cycle
ROKUYO = [
    ("先勝", "Sensho", "Good morning, bad afternoon"),
    ("友引", "Tomobiki", "Draw-friend: avoid funerals"),
    ("先負", "Senbu", "Bad morning, good afternoon"),
    ("仏滅", "Butsumetsu", "Buddha's death: unlucky all day"),
    ("大安", "Taian", "Great peace: lucky all day"),
    ("赤口", "Shakko", "Red mouth: only midday is good"),
]

# Jūni Shō (十二直) — 12 Day Qualities
JUNI_SHO = [
    ("建", "Tatsu", "Establish", "good"),
    ("除", "Nozoku", "Remove", "good"),
    ("満", "Mitsu", "Full", "good"),
    ("平", "Taira", "Balance", "good"),
    ("定", "Sadamu", "Settle", "good"),
    ("執", "Toru", "Grasp", "mixed"),
    ("破", "Yaburu", "Break", "bad"),
    ("危", "Ayabu", "Danger", "bad"),
    ("成", "Naru", "Accomplish", "good"),
    ("納", "Osamu", "Receive", "good"),
    ("開", "Hiraku", "Open", "good"),
    ("閉", "Tozu", "Close", "bad"),
]

# Five Elements (Gogyō) with production/destruction cycles
GOGYO_PRODUCTION = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal",
                     "Metal": "Water", "Water": "Wood"}
GOGYO_DESTRUCTION = {"Wood": "Earth", "Earth": "Water", "Water": "Fire",
                      "Fire": "Metal", "Metal": "Wood"}

# 12 Directional Deities (Jūni Shinsho / 十二神将)
# Associated with Abe no Seimei's Onmyōdō tradition
DIRECTIONAL_DEITIES = [
    ("天一", "Ten'ichi", "North", "Water"),
    ("騰蛇", "Tōda", "North-Northeast", "Fire"),
    ("朱雀", "Suzaku", "South", "Fire"),
    ("六合", "Rikugō", "East", "Wood"),
    ("勾陳", "Kōchin", "Center-Earth", "Earth"),
    ("青龍", "Seiryū", "East", "Wood"),
    ("天空", "Tenkū", "Center", "Earth"),
    ("白虎", "Byakko", "West", "Metal"),
    ("太常", "Taijō", "Southwest", "Earth"),
    ("玄武", "Genbu", "North", "Water"),
    ("太陰", "Taiin", "West-Northwest", "Metal"),
    ("天后", "Tenkō", "North-Northwest", "Water"),
]

# Kippō (吉方) — Lucky directions based on year element
KIPPO = {
    "Wood": ["South", "East"],
    "Fire": ["East", "South"],
    "Earth": ["South", "Southwest"],
    "Metal": ["North", "West"],
    "Water": ["North", "East"],
}

# Kata-imi (方忌) — Directions to avoid based on year element
KATA_IMI = {
    "Wood": ["West", "Northwest"],
    "Fire": ["North", "Northwest"],
    "Earth": ["East", "Northeast"],
    "Metal": ["South", "Southeast"],
    "Water": ["South", "Southwest"],
}


def _stem_branch_indices(year: int) -> tuple:
    """Compute Heavenly Stem and Earthly Branch indices for a year."""
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return stem_idx, branch_idx


def _rokuyo_index(month: int, day: int) -> int:
    """Compute Roku-Yō index from lunar-approximated month and day.
    Traditional formula: (month + day) % 6"""
    return (month + day) % 6


def _juni_sho_index(month: int, day: int) -> int:
    """Compute Jūni Shō (12 Day Qualities) index.
    Rotates based on month and day of month."""
    return (month + day - 1) % 12


def _directional_deity(branch_idx: int) -> dict:
    """Map birth Earthly Branch to its Directional Deity."""
    deity = DIRECTIONAL_DEITIES[branch_idx % 12]
    return {
        "kanji": deity[0],
        "reading": deity[1],
        "direction": deity[2],
        "element": deity[3],
    }


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    birth_year = profile.dob.year
    birth_month = profile.dob.month
    birth_day = profile.dob.day

    # Step 1: Year Stem and Branch (Eto)
    stem_idx, branch_idx = _stem_branch_indices(birth_year)
    jikkan = JIKKAN[stem_idx]
    junishi = JUNISHI[branch_idx]

    # Extract element and polarity
    birth_element = jikkan[2].replace("+", "").replace("-", "")
    yin_yang = "Yang" if "+" in jikkan[2] else "Yin"

    # Step 2: Eto (干支) combination
    eto = {
        "stem_kanji": jikkan[0],
        "stem_reading": jikkan[1],
        "stem_nature": jikkan[2],
        "branch_kanji": junishi[0],
        "branch_reading": junishi[1],
        "branch_animal": junishi[2],
        "eto_name": f"{jikkan[1]}-{junishi[1]}",
        "sexagenary_position": (stem_idx * 6 + branch_idx) % 60 + 1,
    }

    # Step 3: Roku-Yō (six-day fortune)
    rokuyo_idx = _rokuyo_index(birth_month, birth_day)
    rokuyo = ROKUYO[rokuyo_idx]

    # Step 4: Jūni Shō (12 day qualities)
    juni_sho_idx = _juni_sho_index(birth_month, birth_day)
    juni_sho = JUNI_SHO[juni_sho_idx]

    # Step 5: Directional Deity
    deity = _directional_deity(branch_idx)

    # Step 6: Lucky/unlucky directions
    lucky_dirs = KIPPO.get(birth_element, [])
    avoid_dirs = KATA_IMI.get(birth_element, [])

    # Step 7: Production/destruction cycle relationships
    produces = GOGYO_PRODUCTION.get(birth_element, "")
    destroys = GOGYO_DESTRUCTION.get(birth_element, "")

    # Day stem/branch for birth day
    day_stem_idx, day_branch_idx = _stem_branch_indices(birth_year)
    # Approximate day pillar from JDN offset
    from datetime import date
    jdn_offset = (profile.dob - date(1900, 1, 1)).days
    day_stem_idx = (jdn_offset + 9) % 10
    day_branch_idx = (jdn_offset + 1) % 12
    day_yin_yang = "Yang" if JIKKAN[day_stem_idx][2].endswith("+") else "Yin"

    data = {
        "method": "onmyodo_core_v1",
        "yin_yang": yin_yang,
        "birth_element": birth_element,
        "eto": eto,
        "rokuyo": {
            "kanji": rokuyo[0],
            "reading": rokuyo[1],
            "meaning": rokuyo[2],
        },
        "juni_sho": {
            "kanji": juni_sho[0],
            "reading": juni_sho[1],
            "meaning": juni_sho[2],
            "quality": juni_sho[3],
        },
        "directional_deity": deity,
        "lucky_directions": lucky_dirs,
        "avoid_directions": avoid_dirs,
        "element_produces": produces,
        "element_destroys": destroys,
        "day_yin_yang": day_yin_yang,
    }

    return SystemResult(
        id="onmyodo",
        name="Onmyōdō (Way of Yin-Yang)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Seimei-reki (晴明暦) — Abe no Seimei calendar tradition",
            "Onmyō-ryō historical records — Japanese Imperial Bureau of Divination",
        ],
        question="Q1_IDENTITY",
    )
