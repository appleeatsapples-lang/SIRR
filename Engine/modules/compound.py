"""Compound Number Meanings — LOOKUP_FIXED"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    meanings = constants["compound"]["meanings"]

    # Compute compounds from profile's pre-computed core numbers
    compounds = {}
    lp_compound = None
    bd_compound = profile.dob.day

    # Life Path compound: month+day+year digit-by-digit
    m, d, y = profile.dob.month, profile.dob.day, profile.dob.year
    lp_compound = reduce_number(m) + reduce_number(d) + reduce_number(y)
    # Actually: standard method sums reduced components
    m_r = reduce_number(m)
    d_r = reduce_number(d)
    y_r = reduce_number(y)
    lp_compound = m_r + d_r + y_r  # = 9 + 5 + 7 = 21

    compounds["life_path"] = {
        "compound": lp_compound,
        "reduced": reduce_number(lp_compound),
        "name": meanings.get(str(lp_compound), ["Unknown", ""])[0],
        "meaning": meanings.get(str(lp_compound), ["", "Unknown"])[1]
    }
    compounds["birthday"] = {
        "compound": bd_compound,
        "reduced": reduce_number(bd_compound),
        "name": meanings.get(str(bd_compound), ["Unknown", ""])[0],
        "meaning": meanings.get(str(bd_compound), ["", "Unknown"])[1]
    }

    birth_year_compound = reduce_number(y, keep_masters=())  # reduce fully first pass
    # Actually: 1+9+9+6 = 25
    birth_year_compound = sum(int(x) for x in str(y))
    compounds["birth_year"] = {
        "compound": birth_year_compound,
        "reduced": reduce_number(birth_year_compound),
        "name": meanings.get(str(birth_year_compound), ["Unknown", ""])[0],
        "meaning": meanings.get(str(birth_year_compound), ["", "Unknown"])[1]
    }

    # Personal year compound
    py = reduce_number(m) + reduce_number(d) + reduce_number(profile.today.year)
    compounds["personal_year"] = {
        "compound": py,
        "reduced": reduce_number(py),
        "name": meanings.get(str(py), ["Unknown", ""])[0],
        "meaning": meanings.get(str(py), ["", "Unknown"])[1]
    }

    # From pre-computed if available
    if profile.expression:
        compounds["expression"] = {
            "compound": profile.expression if profile.expression > 9 else profile.expression,
            "name": meanings.get(str(profile.expression), ["Unknown", ""])[0]
        }
    if profile.personality:
        compounds["personality"] = {
            "compound": profile.personality if profile.personality > 9 else profile.personality,
            "name": meanings.get(str(profile.personality), ["Unknown", ""])[0]
        }
    if profile.abjad_first:
        compounds["abjad_first_name"] = {
            "compound": profile.abjad_first,
            "name": meanings.get(str(profile.abjad_first), ["Unknown", ""])[0]
        }

    return SystemResult(
        id="compound",
        name="Compound Number Meanings (Chaldean)",
        certainty="LOOKUP_FIXED",
        data=compounds,
        interpretation="Compound meanings from Cheiro/Goodman tradition. Fixed lookup per compound value.",
        constants_version=constants["version"],
        references=[constants["compound"]["source"],
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q1_IDENTITY"
    )
