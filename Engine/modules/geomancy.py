"""Geomancy (Ilm al-Raml) — COMPUTED_STRICT"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

FIGURES = [
    ("Via / al-Tariq", "Path, movement, transitions"),
    ("Conjunctio / al-Iqtiran", "Union, connection, partnership"),
    ("Congregatio / al-Jama'a", "Gathering, community, collective"),
    ("Rubeus / al-Humra", "Intensity, passion; powerful but risky"),
    ("Albus / al-Bayad", "Purity, wisdom, clarity, peace"),
    ("Fortuna Minor / al-Nusra", "Short-term gains through effort"),
    ("Fortuna Major / al-'Utba", "Lasting fortune, stable success"),
    ("Laetitia / al-Farah", "Joy, optimism, upward movement"),
    ("Tristitia / al-Huzn", "Retreat, descent, inward work"),
    ("Puella / al-Naqi", "Grace, receptivity, attraction"),
    ("Puer / Ahmad", "Action, conflict, courage"),
    ("Amissio / al-Inkisar", "Loss, release, making room"),
    ("Acquisitio / al-Qabid", "Gain, accumulation"),
    ("Carcer / al-Dakhil", "Restriction, endurance, binding"),
    ("Caput Draconis / al-Ra's", "New beginnings, ascending energy"),
    ("Cauda Draconis / al-Dhanab", "Endings, release of past")
]

def compute(profile: InputProfile, constants: dict, jdn: int) -> SystemResult:
    idx = jdn % 16
    name, meaning = FIGURES[idx]
    return SystemResult(
        id="geomancy",
        name="Ilm al-Raml (Geomancy)",
        certainty="COMPUTED_STRICT",
        data={"jdn": jdn, "index": idx, "figure": name, "meaning": meaning},
        interpretation="JDN mod 16 mapping. Deterministic.",
        constants_version=constants["version"],
        references=["JDN mod 16 index into 16 geomantic figures"],
        question="Q1_IDENTITY"
    )
