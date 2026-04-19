"""Ogham Letter System — COMPUTED_STRICT
Maps name letters to Ogham fid (letter-trees) and their kennings.
Each of the 20 Ogham letters (feda) corresponds to a tree and meaning.
Source: Auraicept na n-Éces, Book of Ballymote
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Latin → Ogham fid mapping (B-L-F-S-N / H-D-T-C-Q / M-G-NG-Z-R / A-O-U-E-I)
OGHAM = {
    'B': ("Beith", "Birch", "New beginnings"),
    'L': ("Luis", "Rowan", "Protection, insight"),
    'F': ("Fearn", "Alder", "Foundation, oracle"),
    'S': ("Saille", "Willow", "Intuition, cycles"),
    'N': ("Nion", "Ash", "Connection, rebirth"),
    'H': ("Huath", "Hawthorn", "Purification, patience"),
    'D': ("Duir", "Oak", "Strength, endurance"),
    'T': ("Tinne", "Holly", "Challenge, balance"),
    'C': ("Coll", "Hazel", "Wisdom, creativity"),
    'Q': ("Quert", "Apple", "Beauty, choice"),
    'M': ("Muin", "Vine", "Harvest, prophecy"),
    'G': ("Gort", "Ivy", "Persistence, growth"),
    'Z': ("Straif", "Blackthorn", "Discipline, fate"),
    'R': ("Ruis", "Elder", "Transformation, endings"),
    'A': ("Ailm", "Pine/Fir", "Clarity, vision"),
    'O': ("Onn", "Gorse", "Gathering, vitality"),
    'U': ("Ur", "Heather", "Healing, generosity"),
    'E': ("Eadha", "Aspen", "Endurance, courage"),
    'I': ("Ioho", "Yew", "Rebirth, legacy"),
    'K': ("Coll", "Hazel", "Wisdom, creativity"),  # K→C
    'V': ("Fearn", "Alder", "Foundation, oracle"),  # V→F
    'W': ("Saille", "Willow", "Intuition, cycles"),  # W→double-U
    'X': ("Straif", "Blackthorn", "Discipline, fate"),  # X→Z variant
    'Y': ("Ioho", "Yew", "Rebirth, legacy"),  # Y→I
    'J': ("Ioho", "Yew", "Rebirth, legacy"),  # J→I
    'P': ("Beith", "Birch", "New beginnings"),  # P→B labial
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [ch for ch in name if ch.isalpha()]
    feda = [(ch, OGHAM.get(ch, ("?","?","?"))) for ch in letters]

    # Count tree frequencies
    tree_freq = {}
    for _, (fid, tree, _) in feda:
        tree_freq[tree] = tree_freq.get(tree, 0) + 1
    dominant_tree = max(tree_freq, key=tree_freq.get) if tree_freq else "?"

    # First letter = primary ogham
    primary = OGHAM.get(letters[0], ("?","?","?")) if letters else ("?","?","?")

    return SystemResult(
        id="ogham", name="Ogham Letter System",
        certainty="COMPUTED_STRICT",
        data={
            "name": profile.subject,
            "primary_fid": primary[0], "primary_tree": primary[1],
            "primary_meaning": primary[2],
            "dominant_tree": dominant_tree,
            "tree_frequencies": tree_freq,
            "letter_count": len(letters),
        },
        interpretation=None, constants_version=constants["version"],
        references=["Ogham alphabet: 20 feda mapped to trees, from Auraicept na n-Éces"],
        question="Q1_IDENTITY"
    )
