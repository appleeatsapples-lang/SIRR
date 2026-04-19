"""Essential Dignities — COMPUTED_STRICT
For each planet in the natal chart, evaluates its five essential dignities:
1. Domicile (rulership) — planet in its own sign
2. Exaltation — planet in its exaltation sign
3. Triplicity — planet ruling the element of its sign (Dorothean day/night)
4. Bound/Term — planet ruling its degree range (Egyptian bounds)
5. Face/Decan — planet ruling its 10° decan (Chaldean order)

Also flags detriment (opposite of domicile) and fall (opposite of exaltation).

Each dignity has a traditional point score:
  Domicile +5, Exaltation +4, Triplicity +3, Bound +2, Face +1
  Detriment -5, Fall -4
A planet with no dignity is "peregrine" (score 0).

Sources: Ptolemy (Tetrabiblos), Lilly (Christian Astrology), Al-Biruni
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_ELEMENTS = {
    "Aries": "Fire", "Taurus": "Earth", "Gemini": "Air", "Cancer": "Water",
    "Leo": "Fire", "Virgo": "Earth", "Libra": "Air", "Scorpio": "Water",
    "Sagittarius": "Fire", "Capricorn": "Earth", "Aquarius": "Air", "Pisces": "Water",
}

# Traditional domicile rulerships
DOMICILE = {
    "Sun": ["Leo"], "Moon": ["Cancer"],
    "Mercury": ["Gemini", "Virgo"], "Venus": ["Taurus", "Libra"],
    "Mars": ["Aries", "Scorpio"], "Jupiter": ["Sagittarius", "Pisces"],
    "Saturn": ["Capricorn", "Aquarius"],
}

# Detriment = opposite of domicile signs
DETRIMENT = {
    "Sun": ["Aquarius"], "Moon": ["Capricorn"],
    "Mercury": ["Sagittarius", "Pisces"], "Venus": ["Aries", "Scorpio"],
    "Mars": ["Taurus", "Libra"], "Jupiter": ["Gemini", "Virgo"],
    "Saturn": ["Cancer", "Leo"],
}

# Classical exaltation signs
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo",
    "Venus": "Pisces", "Mars": "Capricorn", "Jupiter": "Cancer",
    "Saturn": "Libra", "North Node": "Gemini",
}

# Fall = opposite of exaltation
FALL = {
    "Sun": "Libra", "Moon": "Scorpio", "Mercury": "Pisces",
    "Venus": "Virgo", "Mars": "Cancer", "Jupiter": "Capricorn",
    "Saturn": "Aries", "North Node": "Sagittarius",
}

# Dorothean triplicity rulers
# Element → {day_ruler, night_ruler, participating_ruler}
TRIPLICITY = {
    "Fire":  {"day": "Sun",    "night": "Jupiter", "participating": "Saturn"},
    "Earth": {"day": "Venus",  "night": "Moon",    "participating": "Mars"},
    "Air":   {"day": "Saturn", "night": "Mercury", "participating": "Jupiter"},
    "Water": {"day": "Venus",  "night": "Mars",    "participating": "Moon"},
}

# Egyptian bounds (terms) — for each sign, list of (ruler, end_degree) tuples
# Degrees are cumulative within the sign (0-30)
EGYPTIAN_BOUNDS = {
    "Aries":       [("Jupiter", 6), ("Venus", 12), ("Mercury", 20), ("Mars", 25), ("Saturn", 30)],
    "Taurus":      [("Venus", 8), ("Mercury", 14), ("Jupiter", 22), ("Saturn", 27), ("Mars", 30)],
    "Gemini":      [("Mercury", 6), ("Jupiter", 12), ("Venus", 17), ("Mars", 24), ("Saturn", 30)],
    "Cancer":      [("Mars", 7), ("Venus", 13), ("Mercury", 19), ("Jupiter", 26), ("Saturn", 30)],
    "Leo":         [("Jupiter", 6), ("Venus", 11), ("Saturn", 18), ("Mercury", 24), ("Mars", 30)],
    "Virgo":       [("Mercury", 7), ("Venus", 17), ("Jupiter", 21), ("Mars", 28), ("Saturn", 30)],
    "Libra":       [("Saturn", 6), ("Mercury", 14), ("Jupiter", 21), ("Venus", 28), ("Mars", 30)],
    "Scorpio":     [("Mars", 7), ("Venus", 11), ("Mercury", 19), ("Jupiter", 24), ("Saturn", 30)],
    "Sagittarius": [("Jupiter", 12), ("Venus", 17), ("Mercury", 21), ("Saturn", 26), ("Mars", 30)],
    "Capricorn":   [("Mercury", 7), ("Jupiter", 14), ("Venus", 22), ("Saturn", 26), ("Mars", 30)],
    "Aquarius":    [("Mercury", 7), ("Venus", 13), ("Jupiter", 20), ("Mars", 25), ("Saturn", 30)],
    "Pisces":      [("Venus", 12), ("Jupiter", 16), ("Mercury", 19), ("Mars", 28), ("Saturn", 30)],
}

# Chaldean decan (face) rulers — repeating sequence through all 36 decans
# Starting from 0° Aries: Mars, Sun, Venus, Mercury, Moon, Saturn, Jupiter, ...
CHALDEAN_SEQUENCE = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]


def _get_bound_ruler(sign: str, degree: float) -> str:
    """Return the Egyptian bound ruler for a given sign and degree."""
    bounds = EGYPTIAN_BOUNDS.get(sign, [])
    for ruler, end_deg in bounds:
        if degree < end_deg:
            return ruler
    return bounds[-1][0] if bounds else "?"


def _get_face_ruler(longitude: float) -> str:
    """Return the Chaldean face/decan ruler for a given ecliptic longitude."""
    # 36 decans total, each 10°, cycling through CHALDEAN_SEQUENCE
    decan_index = int(longitude / 10) % 36
    return CHALDEAN_SEQUENCE[decan_index % 7]


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="essential_dignities",
            name="Essential Dignities",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q3_NATURE",
        )

    planets = natal_chart_data.get("planets", {})
    # Determine if day or night chart for triplicity
    sun_lon = planets["Sun"]["longitude"]
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    desc_lon = (asc_lon + 180) % 360
    is_diurnal = ((sun_lon - desc_lon) % 360) < 180

    dignities = {}
    total_score = 0
    dignified_count = 0
    debilitated_count = 0

    for planet_name, planet_data in planets.items():
        sign = planet_data["sign"]
        degree_in_sign = planet_data["degree"] + planet_data["minute"] / 60.0
        longitude = planet_data["longitude"]

        conditions = []
        score = 0

        # 1. Domicile (+5)
        if sign in DOMICILE.get(planet_name, []):
            conditions.append("domicile")
            score += 5

        # 2. Exaltation (+4)
        if EXALTATION.get(planet_name) == sign:
            conditions.append("exaltation")
            score += 4

        # 3. Triplicity (+3)
        element = SIGN_ELEMENTS[sign]
        trip = TRIPLICITY[element]
        trip_ruler = trip["day"] if is_diurnal else trip["night"]
        if planet_name == trip_ruler:
            conditions.append("triplicity")
            score += 3
        elif planet_name == trip["participating"]:
            conditions.append("participating_triplicity")
            score += 1

        # 4. Bound/Term (+2)
        bound_ruler = _get_bound_ruler(sign, degree_in_sign)
        if planet_name == bound_ruler:
            conditions.append("bound")
            score += 2

        # 5. Face/Decan (+1)
        face_ruler = _get_face_ruler(longitude)
        if planet_name == face_ruler:
            conditions.append("face")
            score += 1

        # Debilities
        if sign in DETRIMENT.get(planet_name, []):
            conditions.append("detriment")
            score -= 5

        if FALL.get(planet_name) == sign:
            conditions.append("fall")
            score -= 4

        if not conditions:
            conditions.append("peregrine")

        if score > 0:
            dignified_count += 1
        elif score < 0:
            debilitated_count += 1

        total_score += score

        dignities[planet_name] = {
            "sign": sign,
            "conditions": conditions,
            "score": score,
            "bound_ruler": bound_ruler,
            "face_ruler": face_ruler,
        }

    data = {
        "is_diurnal": is_diurnal,
        "dignities": dignities,
        "total_score": total_score,
        "dignified_count": dignified_count,
        "debilitated_count": debilitated_count,
    }

    return SystemResult(
        id="essential_dignities",
        name="Essential Dignities",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Ptolemy, Tetrabiblos — domicile, exaltation, triplicity, bound, face",
            "Dorothean triplicity rulers (day/night)",
            "Egyptian bounds (Ptolemaic terms)",
        ],
        question="Q3_NATURE",
    )
