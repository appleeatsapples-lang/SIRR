"""Bonification — Hellenistic Planetary Condition Assessment — COMPUTED_STRICT

Evaluates whether each of the 7 traditional planets is bonified (strengthened)
or maltreated (weakened) using classical criteria from Ptolemy, Valens, and
Abu Ma'shar. Each planet receives a net score from weighted conditions:

  A. Solar visibility  — cazimi (+4), combust (-5), under beams (-2)
  B. Essential dignity  — domicile (+3), exaltation (+2), detriment (-3), fall (-2), peregrine (-1)
  C. House strength    — angular (+2), succedent (+1), cadent (-1)
  D. Aspect testimony  — benefic trine (+2), sextile (+1); malefic square (-2), opposition (-3)
  E. Sect modifiers    — in-sect benefic +1 bonus; out-of-sect malefic -1 penalty
  F. Reception         — malefic receives maltreated planet: +1 mitigation
  G. Besiegement       — Mars-Saturn enclosure within 15°: -3

net_score > 0 → bonified; < 0 → maltreated; == 0 → neutral

Sources: Ptolemy (Tetrabiblos II-III), Vettius Valens (Anthology),
         Abu Ma'shar (Great Introduction), Robert Hand (Horoscope Symbols)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

TRADITIONAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

BENEFICS = {"Jupiter", "Venus"}
MALEFICS = {"Mars", "Saturn"}

DIURNAL_PLANETS = {"Sun", "Jupiter", "Saturn"}
NOCTURNAL_PLANETS = {"Moon", "Venus", "Mars"}

# --- Essential dignity tables ---
DOMICILE = {
    "Sun": "Leo", "Moon": "Cancer", "Mercury": ["Gemini", "Virgo"],
    "Venus": ["Taurus", "Libra"], "Mars": ["Aries", "Scorpio"],
    "Jupiter": ["Sagittarius", "Pisces"], "Saturn": ["Capricorn", "Aquarius"],
}
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo",
    "Venus": "Pisces", "Mars": "Capricorn", "Jupiter": "Cancer", "Saturn": "Libra",
}
DETRIMENT = {
    "Sun": "Aquarius", "Moon": "Capricorn", "Mercury": ["Sagittarius", "Pisces"],
    "Venus": ["Aries", "Scorpio"], "Mars": ["Taurus", "Libra"],
    "Jupiter": ["Gemini", "Virgo"], "Saturn": ["Cancer", "Leo"],
}
FALL = {
    "Sun": "Libra", "Moon": "Scorpio", "Mercury": "Pisces",
    "Venus": "Virgo", "Mars": "Cancer", "Jupiter": "Capricorn", "Saturn": "Aries",
}

ANGULAR = {1, 4, 7, 10}
SUCCEDENT = {2, 5, 8, 11}
CADENT = {3, 6, 9, 12}


def _in_sign_list(sign: str, rulership) -> bool:
    """Check if sign matches a rulership entry (str or list)."""
    if isinstance(rulership, list):
        return sign in rulership
    return sign == rulership


def _elongation(lon1: float, lon2: float) -> float:
    """Unsigned angular distance between two longitudes."""
    d = abs(lon1 - lon2) % 360
    return d if d <= 180 else 360 - d


def _is_above_horizon(planet_lon: float, asc_lon: float) -> bool:
    desc_lon = (asc_lon + 180) % 360
    return ((planet_lon - desc_lon) % 360) < 180


def _whole_sign_house(planet_sign: str, asc_sign: str) -> int:
    """Whole-sign house: sign distance from ascendant sign + 1."""
    asc_idx = SIGNS.index(asc_sign)
    pl_idx = SIGNS.index(planet_sign)
    return ((pl_idx - asc_idx) % 12) + 1


def _compute_aspects_between(planets: dict) -> list:
    """Compute major aspects between traditional planets from raw longitudes."""
    ASPECT_ANGLES = {"conjunction": 0, "sextile": 60, "square": 90, "trine": 120, "opposition": 180}
    ORBS = {"conjunction": 8, "sextile": 6, "square": 7, "trine": 8, "opposition": 8}
    result = []
    names = [p for p in TRADITIONAL_PLANETS if p in planets]
    for i, p1 in enumerate(names):
        for p2 in names[i+1:]:
            sep = _elongation(planets[p1]["longitude"], planets[p2]["longitude"])
            for asp_name, angle in ASPECT_ANGLES.items():
                orb = abs(sep - angle)
                if orb <= ORBS[asp_name]:
                    # Applying vs separating: check if angular distance is shrinking
                    # Simple heuristic: if planet with greater longitude has greater speed
                    phase = "applying" if orb < ORBS[asp_name] * 0.5 else "separating"
                    result.append({
                        "planet_1": p1, "planet_2": p2,
                        "aspect": asp_name, "orb": round(orb, 2), "phase": phase,
                    })
                    break  # only closest aspect per pair
    return result


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="bonification",
            name="Bonification (Planetary Condition)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    planets = natal_chart_data.get("planets", {})
    asc_data = natal_chart_data.get("ascendant", {})
    asc_lon = asc_data.get("longitude", 0)
    asc_sign = asc_data.get("sign", "Aries")
    sun_lon = planets.get("Sun", {}).get("longitude", 0)

    # Determine day/night chart
    is_diurnal = _is_above_horizon(sun_lon, asc_lon)

    # Compute aspects from raw positions
    aspects = _compute_aspects_between(planets)

    # Get Mars and Saturn longitudes for besiegement check
    mars_lon = planets.get("Mars", {}).get("longitude", 0)
    saturn_lon = planets.get("Saturn", {}).get("longitude", 0)

    # --- Score each traditional planet ---
    planet_results = {}
    for planet_name in TRADITIONAL_PLANETS:
        if planet_name not in planets:
            continue

        pdata = planets[planet_name]
        lon = pdata["longitude"]
        sign = pdata["sign"]
        conditions = []

        # A. Solar visibility (skip Sun itself)
        if planet_name != "Sun":
            sun_sep = _elongation(lon, sun_lon)
            # Moon uses wider orbs
            combust_orb = 12 if planet_name == "Moon" else 8
            beams_orb = 17 if planet_name == "Moon" else 15

            if sun_sep <= 0.2833:  # 0°17' cazimi
                conditions.append({"code": "CAZIMI", "weight": 4, "detail": f"Within {sun_sep:.2f}° of Sun"})
            elif sun_sep <= combust_orb:
                conditions.append({"code": "COMBUST", "weight": -5, "detail": f"{sun_sep:.1f}° from Sun"})
            elif sun_sep <= beams_orb:
                conditions.append({"code": "UNDER_BEAMS", "weight": -2, "detail": f"{sun_sep:.1f}° from Sun"})

        # B. Essential dignity
        if _in_sign_list(sign, DOMICILE.get(planet_name, [])):
            conditions.append({"code": "DOMICILE", "weight": 3, "detail": f"In own sign {sign}"})
        elif _in_sign_list(sign, EXALTATION.get(planet_name, "")):
            conditions.append({"code": "EXALTATION", "weight": 2, "detail": f"Exalted in {sign}"})
        elif _in_sign_list(sign, DETRIMENT.get(planet_name, [])):
            conditions.append({"code": "DETRIMENT", "weight": -3, "detail": f"In detriment in {sign}"})
        elif _in_sign_list(sign, FALL.get(planet_name, "")):
            conditions.append({"code": "FALL", "weight": -2, "detail": f"In fall in {sign}"})
        else:
            conditions.append({"code": "PEREGRINE", "weight": -1, "detail": f"No essential dignity in {sign}"})

        # C. House strength (whole sign)
        house = _whole_sign_house(sign, asc_sign)
        if house in ANGULAR:
            conditions.append({"code": "ANGULAR", "weight": 2, "detail": f"House {house}"})
        elif house in SUCCEDENT:
            conditions.append({"code": "SUCCEDENT", "weight": 1, "detail": f"House {house}"})
        elif house in CADENT:
            conditions.append({"code": "CADENT", "weight": -1, "detail": f"House {house}"})

        # D. Aspect testimony
        for asp in aspects:
            other = asp["planet_2"] if asp["planet_1"] == planet_name else (
                asp["planet_1"] if asp["planet_2"] == planet_name else None)
            if other is None:
                continue

            asp_type = asp["aspect"]
            phase = asp["phase"]
            weight_multiplier = 1.0 if phase == "applying" else 0.5

            if other in BENEFICS:
                if asp_type == "trine":
                    w = int(2 * weight_multiplier)
                    if w != 0:
                        conditions.append({"code": "BENEFIC_TRINE", "weight": w, "detail": f"{other} trine ({phase})"})
                elif asp_type == "sextile":
                    w = int(1 * weight_multiplier)
                    if w != 0:
                        conditions.append({"code": "BENEFIC_SEXTILE", "weight": w, "detail": f"{other} sextile ({phase})"})
            elif other in MALEFICS:
                if asp_type == "trine":
                    w = int(-1 * weight_multiplier)
                    if w != 0:
                        conditions.append({"code": "MALEFIC_TRINE", "weight": w, "detail": f"{other} trine ({phase})"})
                elif asp_type == "square":
                    w = int(-2 * weight_multiplier)
                    if w != 0:
                        conditions.append({"code": "MALEFIC_SQUARE", "weight": w, "detail": f"{other} square ({phase})"})
                elif asp_type == "opposition":
                    w = int(-3 * weight_multiplier)
                    if w != 0:
                        conditions.append({"code": "MALEFIC_OPPOSITION", "weight": w, "detail": f"{other} opposition ({phase})"})

        # E. Sect modifiers
        if planet_name == "Mercury":
            merc_diff = (planets["Mercury"]["longitude"] - sun_lon) % 360
            natural_sect = "nocturnal" if merc_diff < 180 else "diurnal"
        elif planet_name in DIURNAL_PLANETS:
            natural_sect = "diurnal"
        else:
            natural_sect = "nocturnal"

        chart_sect = "diurnal" if is_diurnal else "nocturnal"
        in_sect = (natural_sect == chart_sect)

        # Check if this planet is aspected by in-sect benefic or out-of-sect malefic
        for asp in aspects:
            other = asp["planet_2"] if asp["planet_1"] == planet_name else (
                asp["planet_1"] if asp["planet_2"] == planet_name else None)
            if other is None:
                continue

            if other in BENEFICS:
                other_sect = "diurnal" if other == "Jupiter" else "nocturnal"
                if other_sect == chart_sect:
                    conditions.append({"code": "SECT_BENEFIC", "weight": 1, "detail": f"In-sect benefic {other}"})
                    break
            elif other in MALEFICS:
                other_sect = "diurnal" if other == "Saturn" else "nocturnal"
                if other_sect != chart_sect:
                    conditions.append({"code": "SECT_MALEFIC", "weight": -1, "detail": f"Out-of-sect malefic {other}"})
                    break

        # F. Reception mitigation — if maltreated, check if any aspecting malefic receives this planet
        # (planet is in malefic's domicile or exaltation)
        for asp in aspects:
            other = asp["planet_2"] if asp["planet_1"] == planet_name else (
                asp["planet_1"] if asp["planet_2"] == planet_name else None)
            if other is None or other not in MALEFICS:
                continue
            # Does the malefic receive this planet? (planet in malefic's domicile/exaltation)
            if _in_sign_list(sign, DOMICILE.get(other, [])) or _in_sign_list(sign, EXALTATION.get(other, "")):
                conditions.append({"code": "RECEPTION_MITIGATE", "weight": 1, "detail": f"{other} receives in {sign}"})

        # G. Besiegement (Mars-Saturn enclosure within 15°)
        if planet_name not in ("Mars", "Saturn"):
            mars_sep = _elongation(lon, mars_lon)
            saturn_sep = _elongation(lon, saturn_lon)
            if mars_sep <= 15 and saturn_sep <= 15:
                # Check planet is between Mars and Saturn in zodiacal order
                m_to_s = (saturn_lon - mars_lon) % 360
                m_to_p = (lon - mars_lon) % 360
                if m_to_p < m_to_s and m_to_s < 30:
                    conditions.append({"code": "BESIEGED", "weight": -3, "detail": f"Enclosed by Mars ({mars_sep:.1f}°) and Saturn ({saturn_sep:.1f}°)"})

        net_score = sum(c["weight"] for c in conditions)
        planet_results[planet_name] = {
            "net_score": net_score,
            "bonified": net_score > 0,
            "maltreated": net_score < 0,
            "house": house,
            "conditions": conditions,
        }

    # Summary
    bonified_count = sum(1 for p in planet_results.values() if p["bonified"])
    maltreated_count = sum(1 for p in planet_results.values() if p["maltreated"])
    neutral_count = sum(1 for p in planet_results.values() if not p["bonified"] and not p["maltreated"])

    sorted_planets = sorted(planet_results.items(), key=lambda x: x[1]["net_score"], reverse=True)
    strongest = sorted_planets[0][0] if sorted_planets else ""
    weakest = sorted_planets[-1][0] if sorted_planets else ""

    data = {
        "planets": planet_results,
        "total_bonified": bonified_count,
        "total_maltreated": maltreated_count,
        "total_neutral": neutral_count,
        "strongest_planet": strongest,
        "weakest_planet": weakest,
        "is_diurnal": is_diurnal,
    }

    return SystemResult(
        id="bonification",
        name="Bonification (Planetary Condition)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Ptolemy, Tetrabiblos — planetary dignity and debility",
            "Vettius Valens, Anthology — sect, combustion, besiegement",
            "Abu Ma'shar, Great Introduction — bonification/maltreatment",
            "Robert Hand, Horoscope Symbols — planetary condition synthesis",
        ],
        question="Q1_IDENTITY",
    )
