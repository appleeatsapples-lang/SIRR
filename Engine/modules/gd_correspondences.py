"""Golden Dawn Correspondences — COMPUTED_STRICT
Cross-reference engine mapping numbers and letters to the GD 777 table:
Planet, Element, Tarot, Hebrew letter, Color, Incense, etc.
Takes Life Path + Expression + Abjad root as input keys.
Source: Aleister Crowley, Liber 777; Israel Regardie, The Golden Dawn
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

TABLE_777 = {
    1: {"planet":"Neptune/Kether","element":"Spirit","tarot":"The Magician","hebrew":"Aleph","color":"White brilliance","path":11},
    2: {"planet":"Uranus/Chokmah","element":"Air","tarot":"The High Priestess","hebrew":"Beth","color":"Grey","path":12},
    3: {"planet":"Saturn/Binah","element":"Water","tarot":"The Empress","hebrew":"Gimel","color":"Black","path":13},
    4: {"planet":"Jupiter/Chesed","element":"Fire","tarot":"The Emperor","hebrew":"Daleth","color":"Blue","path":14},
    5: {"planet":"Mars/Geburah","element":"Fire","tarot":"The Hierophant","hebrew":"He","color":"Red","path":15},
    6: {"planet":"Sun/Tiphareth","element":"Air","tarot":"The Lovers","hebrew":"Vav","color":"Gold","path":16},
    7: {"planet":"Venus/Netzach","element":"Water","tarot":"The Chariot","hebrew":"Zayin","color":"Green","path":17},
    8: {"planet":"Mercury/Hod","element":"Earth","tarot":"Strength","hebrew":"Cheth","color":"Orange","path":18},
    9: {"planet":"Moon/Yesod","element":"Water","tarot":"The Hermit","hebrew":"Teth","color":"Violet","path":19},
    11:{"planet":"Uranus","element":"Air","tarot":"Justice","hebrew":"Lamed","color":"Blue-violet","path":22},
    22:{"planet":"Saturn","element":"Earth","tarot":"The Fool","hebrew":"Shin","color":"Crimson","path":31},
    33:{"planet":"Neptune","element":"Water","tarot":"The World","hebrew":"Tav","color":"Indigo","path":32},
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    lp = profile.life_path or 3
    expr = profile.expression or 11
    # Abjad root
    abjad = constants["arabic_letters"]["abjad_kabir"]
    ar_name = profile.arabic.replace(" ","")
    ar_total = sum(abjad.get(ch,0) for ch in ar_name)
    ar_root = reduce_number(ar_total, keep_masters=())

    lp_corr = TABLE_777.get(lp, TABLE_777.get(reduce_number(lp, keep_masters=()), {}))
    expr_corr = TABLE_777.get(expr, TABLE_777.get(reduce_number(expr, keep_masters=()), {}))
    ar_corr = TABLE_777.get(ar_root, {})

    return SystemResult(
        id="gd_correspondences", name="Golden Dawn 777 Correspondences",
        certainty="COMPUTED_STRICT",
        data={
            "life_path": {"number": lp, **lp_corr},
            "expression": {"number": expr, **expr_corr},
            "abjad_root": {"number": ar_root, **ar_corr},
        },
        interpretation=None, constants_version=constants["version"],
        references=["Crowley Liber 777 / Regardie The Golden Dawn correspondence tables"],
        question="Q6_SYNTHESIS"
    )
