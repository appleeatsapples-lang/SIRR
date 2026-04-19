"""I Ching Plum Blossom — LOOKUP_FIXED"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

TRIGRAMS = {1:"Qian/Heaven",2:"Dui/Lake",3:"Li/Fire",4:"Zhen/Thunder",
            5:"Xun/Wind",6:"Kan/Water",7:"Gen/Mountain",8:"Kun/Earth"}

HEX_TABLE = {
    (1,1):1,(1,2):10,(1,3):13,(1,4):25,(1,5):44,(1,6):6,(1,7):33,(1,8):12,
    (2,1):43,(2,2):58,(2,3):49,(2,4):17,(2,5):28,(2,6):47,(2,7):31,(2,8):45,
    (3,1):14,(3,2):38,(3,3):30,(3,4):21,(3,5):50,(3,6):64,(3,7):56,(3,8):35,
    (4,1):34,(4,2):54,(4,3):55,(4,4):51,(4,5):32,(4,6):40,(4,7):62,(4,8):16,
    (5,1):9,(5,2):61,(5,3):37,(5,4):42,(5,5):57,(5,6):59,(5,7):53,(5,8):20,
    (6,1):5,(6,2):60,(6,3):63,(6,4):3,(6,5):48,(6,6):29,(6,7):39,(6,8):8,
    (7,1):26,(7,2):41,(7,3):22,(7,4):27,(7,5):18,(7,6):4,(7,7):52,(7,8):23,
    (8,1):11,(8,2):19,(8,3):36,(8,4):24,(8,5):46,(8,6):7,(8,7):15,(8,8):2,
}

HEX_NAMES = {
    1:"The Creative",2:"The Receptive",3:"Difficulty at Beginning",4:"Youthful Folly",
    5:"Waiting",6:"Conflict",7:"The Army",8:"Holding Together",9:"Small Taming",
    10:"Treading",11:"Peace",12:"Standstill",13:"Fellowship",14:"Great Possession",
    15:"Modesty",16:"Enthusiasm",17:"Following",18:"Work on Decayed",19:"Approach",
    20:"Contemplation",21:"Biting Through",22:"Grace",23:"Splitting Apart",24:"Return",
    25:"Innocence",26:"Great Taming",27:"Nourishment",28:"Great Excess",
    29:"The Abysmal",30:"The Clinging",31:"Influence",32:"Duration",33:"Retreat",
    34:"Great Power",35:"Progress",36:"Darkening of Light",37:"The Family",
    38:"Opposition",39:"Obstruction",40:"Deliverance",41:"Decrease",42:"Increase",
    43:"Breakthrough",44:"Coming to Meet",45:"Gathering",46:"Pushing Upward",
    47:"Oppression",48:"The Well",49:"Revolution",50:"The Cauldron",51:"Arousing",
    52:"Keeping Still",53:"Development",54:"Marrying Maiden",55:"Abundance",
    56:"The Wanderer",57:"The Gentle",58:"The Joyous",59:"Dispersion",
    60:"Limitation",61:"Inner Truth",62:"Small Excess",63:"After Completion",
    64:"Before Completion"
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    ic = constants["iching"]["plum_blossom"]
    yr = int(ic["earthly_branch_year_rat"])
    hr = int(ic["hour_branch_si"])
    s = yr + profile.dob.month + profile.dob.day

    upper = s % 8
    if upper == 0: upper = 8
    lower = (s + hr) % 8
    if lower == 0: lower = 8

    hx = HEX_TABLE.get((upper, lower), 0)
    name = HEX_NAMES.get(hx, f"#{hx}")

    return SystemResult(
        id="iching",
        name="I Ching (Plum Blossom)",
        certainty="LOOKUP_FIXED",
        data={
            "upper_trigram": TRIGRAMS.get(upper, str(upper)),
            "lower_trigram": TRIGRAMS.get(lower, str(lower)),
            "hexagram_number": hx,
            "hexagram_name": name
        },
        interpretation="Method-locked Mei Hua mapping with fixed hour branch placeholder.",
        constants_version=constants["version"],
        references=["King Wen matrix + user Plum Blossom method"],
        question="Q1_IDENTITY"
    )
