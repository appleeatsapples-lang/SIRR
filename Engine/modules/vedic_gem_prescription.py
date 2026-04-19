"""
Vedic Gem Prescription (नवरत्न — Navaratna)
──────────────────────────────────────────────
Maps natal planetary strengths to traditional Navaratna gem recommendations.

Algorithm:
  1. Identify Ascendant lord (strongest functional benefic)
  2. Map each planet → gem/metal/day from vedic_lookups.json
  3. Primary gem = Ascendant lord's gem (strengthens the chart ruler)
  4. Secondary gem = Moon lord's gem (strengthens emotional constitution)
  5. Caution gem = planet ruling 6th/8th/12th house (dusthana lords)

Source: BPHS; Garuda Purana; Ratna Pariksha
SOURCE_TIER: B (respected secondary — gem therapy is classical but interpretive)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


PLANET_GEM = {
    "Sun": {"gem": "Ruby", "metal": "Gold", "day": "Sunday"},
    "Moon": {"gem": "Pearl", "metal": "Silver", "day": "Monday"},
    "Mars": {"gem": "Red Coral", "metal": "Copper", "day": "Tuesday"},
    "Mercury": {"gem": "Emerald", "metal": "Gold", "day": "Wednesday"},
    "Jupiter": {"gem": "Yellow Sapphire", "metal": "Gold", "day": "Thursday"},
    "Venus": {"gem": "Diamond", "metal": "Silver", "day": "Friday"},
    "Saturn": {"gem": "Blue Sapphire", "metal": "Iron/Lead", "day": "Saturday"},
    "Rahu": {"gem": "Hessonite Garnet", "metal": "Mixed metals", "day": None},
    "Ketu": {"gem": "Cat's Eye Chrysoberyl", "metal": "Mixed metals", "day": None},
}

SIGN_RULER = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

# Dusthana houses (6th, 8th, 12th — counted from 0)
DUSTHANA_HOUSES = {5, 7, 11}  # 0-indexed: house 6=idx 5, house 8=idx 7, house 12=idx 11


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal = kwargs.get("natal_chart_data")
    if not natal or "planets" not in natal:
        return SystemResult(
            id="vedic_gem_prescription",
            name="Vedic Gem Prescription (Navaratna)",
            certainty="NEEDS_EPHEMERIS",
            data={"primary_gem": None, "reason": "No natal chart data"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["BPHS", "Garuda Purana"],
            question="Q3_GUIDANCE",
        )

    planets = natal["planets"]

    # Ascendant lord
    asc_raw = natal.get("ascendant")
    asc = asc_raw.get("longitude") if isinstance(asc_raw, dict) else asc_raw
    asc_sign_idx = int(float(asc) / 30.0) % 12 if asc is not None else None
    asc_lord = SIGN_RULER.get(asc_sign_idx) if asc_sign_idx is not None else None

    # Moon lord
    moon_info = planets.get("Moon")
    moon_sign_idx = None
    if moon_info is not None:
        moon_lon = moon_info if isinstance(moon_info, (int, float)) else moon_info.get("longitude", moon_info.get("lon", 0))
        moon_sign_idx = int(float(moon_lon) / 30.0) % 12
    moon_lord = SIGN_RULER.get(moon_sign_idx) if moon_sign_idx is not None else None

    # Primary gem (Ascendant lord)
    primary = PLANET_GEM.get(asc_lord, {}) if asc_lord else {}
    # Secondary gem (Moon lord)
    secondary = PLANET_GEM.get(moon_lord, {}) if moon_lord else {}

    # Dusthana lords (6th, 8th, 12th from Ascendant)
    caution_gems = []
    if asc_sign_idx is not None:
        for offset in DUSTHANA_HOUSES:
            dusthana_sign = (asc_sign_idx + offset) % 12
            dusthana_lord = SIGN_RULER.get(dusthana_sign)
            if dusthana_lord and dusthana_lord != asc_lord:
                gem_info = PLANET_GEM.get(dusthana_lord, {})
                caution_gems.append({
                    "house": offset + 1,
                    "lord": dusthana_lord,
                    "gem": gem_info.get("gem"),
                    "reason": f"Rules house {offset + 1} (dusthana)",
                })

    # Full prescription table
    all_gems = {}
    for planet, info in PLANET_GEM.items():
        all_gems[planet] = info.copy()

    return SystemResult(
        id="vedic_gem_prescription",
        name="Vedic Gem Prescription (Navaratna)",
        certainty="COMPUTED_STRICT",
        data={
            "ascendant_lord": asc_lord,
            "ascendant_sign_index": asc_sign_idx,
            "primary_gem": primary.get("gem"),
            "primary_metal": primary.get("metal"),
            "primary_day": primary.get("day"),
            "moon_lord": moon_lord,
            "secondary_gem": secondary.get("gem"),
            "secondary_metal": secondary.get("metal"),
            "caution_gems": caution_gems,
            "navaratna_table": all_gems,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["BPHS", "Garuda Purana", "Ratna Pariksha", "vedic_lookups.json"],
        question="Q3_GUIDANCE",
    )
