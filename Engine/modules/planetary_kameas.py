"""Planetary Kameas (Magic Squares) — COMPUTED_STRICT
Seven planetary magic squares: Saturn(3×3) through Moon(9×9).
Maps name's Abjad/ordinal values onto the appropriate planetary grid.
Source: Agrippa De Occulta Philosophia, Shams al-Ma'arif (Al-Buni)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

KAMEAS = {
    "Saturn": {"order":3, "constant":15, "square":[
        [2,7,6],[9,5,1],[4,3,8]]},
    "Jupiter": {"order":4, "constant":34, "square":[
        [4,14,15,1],[9,7,6,12],[5,11,10,8],[16,2,3,13]]},
    "Mars": {"order":5, "constant":65, "square":[
        [11,24,7,20,3],[4,12,25,8,16],[17,5,13,21,9],[10,18,1,14,22],[23,6,19,2,15]]},
    "Sun": {"order":6, "constant":111, "square":[
        [6,32,3,34,35,1],[7,11,27,28,8,30],[19,14,16,15,23,24],
        [18,20,22,21,17,13],[25,29,10,9,26,12],[36,5,33,4,2,31]]},
    "Venus": {"order":7, "constant":175, "square":[
        [22,47,16,41,10,35,4],[5,23,48,17,42,11,29],[30,6,24,49,18,36,12],
        [13,31,7,25,43,19,37],[38,14,32,1,26,44,20],[21,39,8,33,2,27,45],
        [46,15,40,9,34,3,28]]},
    "Mercury": {"order":8, "constant":260},  # Too large to inline
    "Moon": {"order":9, "constant":369},      # Too large to inline
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    # Determine planetary affinity from Day Ruler
    weekday = profile.dob.weekday()
    day_planets = {0:"Moon",1:"Mars",2:"Mercury",3:"Jupiter",4:"Venus",5:"Saturn",6:"Sun"}
    planet = day_planets[weekday]

    kamea = KAMEAS[planet]
    order = kamea["order"]
    magic_constant = kamea["constant"]
    total = order * magic_constant  # Sum of all cells

    # Name ordinal mapped to kamea position
    name = profile.subject.upper()
    ordinal_vals = [ord(ch)-64 for ch in name if ch.isalpha()]
    name_sum = sum(ordinal_vals)
    kamea_position = name_sum % (order * order) + 1

    return SystemResult(
        id="planetary_kameas", name="Planetary Kameas (Magic Squares)",
        certainty="COMPUTED_STRICT",
        data={
            "planet": planet, "kamea_order": order,
            "magic_constant": magic_constant, "total_sum": total,
            "name_ordinal_sum": name_sum,
            "name_position_in_kamea": kamea_position,
            "square": kamea.get("square"),
        },
        interpretation=None, constants_version=constants["version"],
        references=["Agrippa planetary kameas + Al-Buni wafq tradition"],
        question="Q4_PROTECTION"
    )
