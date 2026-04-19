"""
Ayurvedic Astrological Dosha Profile (आयुर्वेद दोष)
──────────────────────────────────────────────────────
Computes astrological dosha dominance (NOT clinical prakriti — that requires
physiological observation per Gemini delivery note / Charaka Samhita exclusion).

Algorithm:
  1. Map each natal planet → dosha (Vata/Pitta/Kapha) from vedic_lookups.json
  2. Weight Ascendant lord and Moon lord equally (BPHS principle)
  3. Mercury classified as "mixed" (tridoshic) — distributes 0.33 to each
  4. Determine dominant dosha and constitution type

Source: BPHS Ch. 3 dosha mapping; Charaka Samhita (exclusion note)
SOURCE_TIER: B (Vedic astrological derivation, not clinical diagnosis)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Planet → Dosha (from vedic_lookups.json)
PLANET_DOSHA = {
    "Sun": "Pitta",
    "Moon": "Kapha",
    "Mars": "Pitta",
    "Mercury": "mixed",
    "Jupiter": "Kapha",
    "Venus": "Kapha",
    "Saturn": "Vata",
    "Rahu": "Vata",
    "Ketu": "Pitta",
}

SIGN_RULER = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

# Constitution types
CONSTITUTION_TYPES = {
    "Vata": "Vata-dominant: movement, creativity, change, irregularity",
    "Pitta": "Pitta-dominant: transformation, intensity, precision, drive",
    "Kapha": "Kapha-dominant: stability, endurance, nurturing, groundedness",
    "Vata-Pitta": "Vata-Pitta dual: dynamic intensity with creative variability",
    "Pitta-Kapha": "Pitta-Kapha dual: steady drive with transformative depth",
    "Vata-Kapha": "Vata-Kapha dual: grounded creativity with rhythmic cycles",
    "Tridoshic": "Tridoshic: balanced across all three doshas",
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal = kwargs.get("natal_chart_data")
    if not natal or "planets" not in natal:
        return SystemResult(
            id="ayurvedic_constitution",
            name="Ayurvedic Astrological Dosha",
            certainty="NEEDS_EPHEMERIS",
            data={"dominant_dosha": None, "reason": "No natal chart data"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["BPHS Ch. 3"],
            question="Q1_IDENTITY",
        )

    planets = natal["planets"]
    scores = {"Vata": 0.0, "Pitta": 0.0, "Kapha": 0.0}
    planet_doshas = {}

    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if name in planets:
            dosha = PLANET_DOSHA.get(name)
            if dosha == "mixed":
                scores["Vata"] += 0.33
                scores["Pitta"] += 0.33
                scores["Kapha"] += 0.33
                planet_doshas[name] = "Tridoshic"
            elif dosha:
                scores[dosha] += 1.0
                planet_doshas[name] = dosha

    # Ascendant lord extra weight
    asc_raw = natal.get("ascendant")
    asc = asc_raw.get("longitude") if isinstance(asc_raw, dict) else asc_raw
    if asc is not None:
        asc_lord = SIGN_RULER.get(int(float(asc) / 30.0) % 12)
        if asc_lord:
            dosha = PLANET_DOSHA.get(asc_lord)
            if dosha == "mixed":
                scores["Vata"] += 0.33
                scores["Pitta"] += 0.33
                scores["Kapha"] += 0.33
            elif dosha:
                scores[dosha] += 1.0

    # Moon lord extra weight
    moon_info = planets.get("Moon")
    if moon_info is not None:
        moon_lon = moon_info if isinstance(moon_info, (int, float)) else moon_info.get("longitude", moon_info.get("lon", 0))
        moon_lord = SIGN_RULER.get(int(float(moon_lon) / 30.0) % 12)
        if moon_lord:
            dosha = PLANET_DOSHA.get(moon_lord)
            if dosha == "mixed":
                scores["Vata"] += 0.33
                scores["Pitta"] += 0.33
                scores["Kapha"] += 0.33
            elif dosha:
                scores[dosha] += 1.0

    # Round scores
    scores = {k: round(v, 2) for k, v in scores.items()}
    total = sum(scores.values())

    # Determine constitution type
    sorted_doshas = sorted(scores.items(), key=lambda x: -x[1])
    dominant = sorted_doshas[0][0]
    second = sorted_doshas[1][0]

    # Check if tridoshic (all within 15% of each other)
    if total > 0:
        pcts = {k: v / total for k, v in scores.items()}
        spread = max(pcts.values()) - min(pcts.values())
        if spread < 0.15:
            constitution = "Tridoshic"
        elif sorted_doshas[0][1] - sorted_doshas[1][1] < 1.0:
            # Dual dosha
            pair = sorted([dominant, second])
            constitution = f"{pair[0]}-{pair[1]}" if pair[0] < pair[1] else f"{pair[1]}-{pair[0]}"
            # Normalize ordering
            if constitution not in CONSTITUTION_TYPES:
                constitution = f"{dominant}-{second}"
        else:
            constitution = dominant
    else:
        constitution = "Unknown"

    return SystemResult(
        id="ayurvedic_constitution",
        name="Ayurvedic Astrological Dosha",
        certainty="COMPUTED_STRICT",
        data={
            "scores": scores,
            "dominant_dosha": dominant,
            "constitution_type": constitution,
            "constitution_description": CONSTITUTION_TYPES.get(constitution, ""),
            "planet_doshas": planet_doshas,
            "total_votes": round(total, 2),
            "note": "Astrological dosha profile — not clinical prakriti diagnosis",
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["BPHS Ch. 3", "vedic_lookups.json", "Charaka Samhita (exclusion note)"],
        question="Q1_IDENTITY",
    )
