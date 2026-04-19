"""Birth Rune — COMPUTED_STRICT
Maps DOB to one of the 24 Elder Futhark runes via half-month periods.
Source: Ralph Blum, Edred Thorsson / Germanic tradition
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

RUNES = [
    ((6,29),(7,13), "Fehu", "ᚠ", "Wealth, abundance"),
    ((7,14),(7,28), "Uruz", "ᚢ", "Strength, vitality"),
    ((7,29),(8,12), "Thurisaz", "ᚦ", "Defense, conflict"),
    ((8,13),(8,28), "Ansuz", "ᚨ", "Communication, wisdom"),
    ((8,29),(9,12), "Raidho", "ᚱ", "Journey, movement"),
    ((9,13),(9,27), "Kenaz", "ᚲ", "Knowledge, creativity"),
    ((9,28),(10,12), "Gebo", "ᚷ", "Gift, partnership"),
    ((10,13),(10,27), "Wunjo", "ᚹ", "Joy, harmony"),
    ((10,28),(11,12), "Hagalaz", "ᚺ", "Disruption, change"),
    ((11,13),(11,27), "Nauthiz", "ᚾ", "Need, constraint"),
    ((11,28),(12,12), "Isa", "ᛁ", "Ice, stillness"),
    ((12,13),(12,27), "Jera", "ᛃ", "Harvest, cycles"),
    ((12,28),(1,12), "Eihwaz", "ᛇ", "Endurance, death/rebirth"),
    ((1,13),(1,27), "Perthro", "ᛈ", "Mystery, fate"),
    ((1,28),(2,11), "Algiz", "ᛉ", "Protection, awakening"),
    ((2,12),(2,26), "Sowilo", "ᛊ", "Sun, victory"),
    ((2,27),(3,13), "Tiwaz", "ᛏ", "Justice, sacrifice"),
    ((3,14),(3,29), "Berkano", "ᛒ", "Birth, renewal"),
    ((3,30),(4,13), "Ehwaz", "ᛖ", "Horse, trust"),
    ((4,14),(4,28), "Mannaz", "ᛗ", "Humanity, self"),
    ((4,29),(5,13), "Laguz", "ᛚ", "Water, intuition"),
    ((5,14),(5,28), "Ingwaz", "ᛝ", "Fertility, completion"),
    ((5,29),(6,13), "Dagaz", "ᛞ", "Day, breakthrough"),
    ((6,14),(6,28), "Othala", "ᛟ", "Heritage, home"),
]

def _in_range(dob, start, end):
    m, d = dob.month, dob.day
    sm, sd = start
    em, ed = end
    if sm > em:
        return (m == sm and d >= sd) or (m == em and d <= ed) or m > sm or m < em
    return (m == sm and d >= sd) or (m == em and d <= ed) or (sm < m < em)

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    rune_name, rune_char, rune_meaning = "Unknown", "?", ""
    for start, end, name, char, meaning in RUNES:
        if _in_range(profile.dob, start, end):
            rune_name, rune_char, rune_meaning = name, char, meaning
            break
    return SystemResult(
        id="birth_rune", name="Birth Rune (Elder Futhark)",
        certainty="COMPUTED_STRICT",
        data={"rune": rune_name, "rune_character": rune_char,
              "meaning": rune_meaning, "dob": str(profile.dob)},
        interpretation=None, constants_version=constants["version"],
        references=["24 Elder Futhark runes mapped to half-month periods"],
        question="Q1_IDENTITY"
    )
