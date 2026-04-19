"""
Hermetic Element Balance (Four Classical Elements)
────────────────────────────────────────────────────
Aggregates element votes across Western astrological systems
(natal chart, temperament, decan, dwad) into a single Hermetic
four-element profile.

Algorithm:
  1. Collect element assignments from natal planets (sign → element)
  2. Add temperament primary/secondary elements
  3. Add decan and dwad element associations
  4. Compute Fire/Earth/Air/Water balance with standardized scoring
  5. Determine dominant, weakest, and missing elements

Source: Agrippa: Three Books of Occult Philosophy; Ptolemy: Tetrabiblos
SOURCE_TIER: B (classical Western esoteric framework)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


SIGN_ELEMENT = {
    0: "Fire", 1: "Earth", 2: "Air", 3: "Water",
    4: "Fire", 5: "Earth", 6: "Air", 7: "Water",
    8: "Fire", 9: "Earth", 10: "Air", 11: "Water",
}

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal = kwargs.get("natal_chart_data")
    all_results = kwargs.get("all_results", [])

    scores = {"Fire": 0.0, "Earth": 0.0, "Air": 0.0, "Water": 0.0}
    sources = []

    # 1. Natal planets → sign → element
    if natal and "planets" in natal:
        for name, info in natal["planets"].items():
            lon = info if isinstance(info, (int, float)) else info.get("longitude", info.get("lon"))
            if lon is None:
                continue
            sign_idx = int(float(lon) / 30.0) % 12
            el = SIGN_ELEMENT[sign_idx]
            # Sun/Moon/Ascendant get 2× weight
            weight = 2.0 if name in ("Sun", "Moon") else 1.0
            scores[el] += weight
            sources.append({"source": f"natal_{name}", "element": el, "weight": weight})

        # Ascendant
        asc_raw = natal.get("ascendant")
        asc = asc_raw.get("longitude") if isinstance(asc_raw, dict) else asc_raw
        if asc is not None:
            asc_sign = int(float(asc) / 30.0) % 12
            el = SIGN_ELEMENT[asc_sign]
            scores[el] += 2.0
            sources.append({"source": "natal_Ascendant", "element": el, "weight": 2.0})

    # 2. Temperament module
    for r in all_results:
        if r.id == "temperament" and r.data:
            pri = r.data.get("primary_element")
            sec = r.data.get("secondary_element")
            if pri and pri in scores:
                scores[pri] += 1.5
                sources.append({"source": "temperament_primary", "element": pri, "weight": 1.5})
            if sec and sec in scores:
                scores[sec] += 1.0
                sources.append({"source": "temperament_secondary", "element": sec, "weight": 1.0})
            break

    # 3. Decan element
    for r in all_results:
        if r.id == "decan" and r.data:
            decan_el = r.data.get("element")
            if decan_el and decan_el in scores:
                scores[decan_el] += 1.0
                sources.append({"source": "decan", "element": decan_el, "weight": 1.0})
            break

    # 4. Dwad element
    for r in all_results:
        if r.id == "dwad" and r.data:
            dwad_el = r.data.get("element")
            if dwad_el and dwad_el in scores:
                scores[dwad_el] += 0.5
                sources.append({"source": "dwad", "element": dwad_el, "weight": 0.5})
            break

    # Compute totals
    scores = {k: round(v, 2) for k, v in scores.items()}
    total = sum(scores.values())

    dominant = max(scores, key=scores.get) if total > 0 else None
    weakest = min(scores, key=scores.get) if total > 0 else None
    missing = [k for k, v in scores.items() if v == 0]

    if total > 0:
        pcts = {k: round(v / total * 100, 1) for k, v in scores.items()}
    else:
        pcts = {k: 0.0 for k in scores}

    # Modality check (Cardinal/Fixed/Mutable) from Sun sign
    modality = None
    if natal and "planets" in natal:
        sun = natal["planets"].get("Sun")
        if sun is not None:
            sun_lon = sun if isinstance(sun, (int, float)) else sun.get("longitude", sun.get("lon", 0))
            sun_sign = int(float(sun_lon) / 30.0) % 12
            modality = ["Cardinal", "Fixed", "Mutable"][sun_sign % 3]

    return SystemResult(
        id="hermetic_element_balance",
        name="Hermetic Element Balance",
        certainty="COMPUTED_STRICT",
        data={
            "scores": scores,
            "percentages": pcts,
            "dominant_element": dominant,
            "weakest_element": weakest,
            "missing_elements": missing,
            "total_weight": round(total, 2),
            "source_count": len(sources),
            "sun_modality": modality,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Agrippa: Three Books of Occult Philosophy", "Ptolemy: Tetrabiblos"],
        question="Q1_IDENTITY",
    )
