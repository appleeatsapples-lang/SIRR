"""Ifá / Ifa — COMPUTED_STRICT
Yoruba binary divination system — 256 odu (8-bit combinations)
Completely independent mathematical framework from Western/Arabic/Chinese systems.

Computation:
  - 16 principal odu (4-bit right leg) × 16 (4-bit left leg) = 256 total
  - Birth odu derived from date components mapped to binary via modular arithmetic
  - Each leg is a 4-position binary column (open=0, closed=1)

This is the first African tradition in SIRR.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# 16 principal odu names (Meji forms) in traditional ranking order
# Each corresponds to a 4-bit binary pattern
ODU_NAMES = {
    0b1111: ("Ogbe", "Open Road"),
    0b0000: ("Oyeku", "Completion/Darkness"),
    0b1100: ("Iwori", "Inner Vision"),
    0b0011: ("Odi", "Closure/Feminine"),
    0b1010: ("Irosun", "Ancestry/Blood"),
    0b0101: ("Owonrin", "Chaos/Transformation"),
    0b1001: ("Obara", "Strength Through Humility"),
    0b0110: ("Okanran", "Reversal/Fire"),
    0b1110: ("Ogunda", "Clearing The Path"),
    0b0001: ("Osa", "Spiritual Journey"),
    0b1011: ("Ika", "Power/Aggression"),
    0b0100: ("Oturupon", "Disease/Medicine"),
    0b1101: ("Otura", "Spiritual Wisdom"),
    0b0010: ("Irete", "Pressing Forward"),
    0b1000: ("Ose", "Sweetness/Abundance"),
    0b0111: ("Ofun", "Creation/Origin"),
}

# All 256 odu as (right_leg, left_leg) combinations
# Right leg = first odu cast, Left leg = second
# Combined name = "Right-Left" (e.g., "Ogbe-Oyeku")


def _date_to_binary_leg(value: int) -> int:
    """Map a numeric value to a 4-bit binary pattern (0-15).
    Uses modular arithmetic to distribute across all 16 patterns."""
    return value % 16


def _odu_name(binary_4bit: int) -> str:
    """Get odu name from 4-bit pattern."""
    entry = ODU_NAMES.get(binary_4bit)
    return entry[0] if entry else f"Odu-{binary_4bit:04b}"


def _odu_meaning(binary_4bit: int) -> str:
    """Get odu meaning from 4-bit pattern."""
    entry = ODU_NAMES.get(binary_4bit)
    return entry[1] if entry else "Unknown"


def _binary_string(val: int) -> str:
    """Convert to 4-position binary display (traditional: | or || marks)."""
    bits = f"{val:04b}"
    return bits


def _rank_odu(binary_4bit: int) -> int:
    """Get traditional ranking (1=Ogbe highest, 16=Ofun)."""
    ranking = list(ODU_NAMES.keys())
    try:
        return ranking.index(binary_4bit) + 1
    except ValueError:
        return 17


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    dob = profile.dob

    # Derive two legs from birth date components
    # Right leg (destiny): day + month
    # Left leg (path): year digits sum + day
    right_seed = dob.day + dob.month
    left_seed = sum(int(d) for d in str(dob.year)) + dob.day

    right_leg = _date_to_binary_leg(right_seed)
    left_leg = _date_to_binary_leg(left_seed)

    # Combined 8-bit odu (256 possibilities)
    combined = (right_leg << 4) | left_leg
    odu_index = combined  # 0-255

    right_name = _odu_name(right_leg)
    left_name = _odu_name(left_leg)
    right_meaning = _odu_meaning(right_leg)
    left_meaning = _odu_meaning(left_leg)

    # Meji check: both legs identical = doubled power
    is_meji = right_leg == left_leg

    # Combined name
    if is_meji:
        combined_name = f"{right_name} Meji"
    else:
        combined_name = f"{right_name}-{left_name}"

    # Traditional element mapping
    element_map = {
        0b1111: "Air", 0b0000: "Earth", 0b1100: "Fire", 0b0011: "Water",
        0b1010: "Earth", 0b0101: "Air", 0b1001: "Fire", 0b0110: "Fire",
        0b1110: "Metal", 0b0001: "Air", 0b1011: "Earth", 0b0100: "Water",
        0b1101: "Air", 0b0010: "Earth", 0b1000: "Water", 0b0111: "Fire",
    }
    right_element = element_map.get(right_leg, "Unknown")
    left_element = element_map.get(left_leg, "Unknown")

    # Root number (total binary positions that are "closed"/1)
    ones_count = bin(combined).count('1')

    return SystemResult(
        id="ifa",
        name="Ifá (Yoruba Binary Odu)",
        certainty="COMPUTED_STRICT",
        data={
            "combined_odu": combined_name,
            "odu_index": odu_index,
            "right_leg": {
                "name": right_name,
                "meaning": right_meaning,
                "binary": _binary_string(right_leg),
                "rank": _rank_odu(right_leg),
                "element": right_element,
            },
            "left_leg": {
                "name": left_name,
                "meaning": left_meaning,
                "binary": _binary_string(left_leg),
                "rank": _rank_odu(left_leg),
                "element": left_element,
            },
            "is_meji": is_meji,
            "closed_marks": ones_count,
            "open_marks": 8 - ones_count,
            "seed_right": right_seed,
            "seed_left": left_seed,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Ifá: Yoruba divination system, 256 odu from 16×16 binary combinations",
            "Birth odu derived from date components via mod-16 mapping",
            "Traditional ranking: Ogbe (highest) through Ofun",
            "First African tradition in SIRR — completely independent mathematical axis",
            "SOURCE_TIER:A/B — Ifa Odu corpus (Yoruba oral tradition). INVESTIGATE: verify specific lookup table attribution to documented scholarly edition.",
        ],
        question="Q1_IDENTITY"
    )
