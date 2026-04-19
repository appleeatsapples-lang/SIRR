"""Almuten Figuris — Lord of the Geniture — COMPUTED_STRICT
For each of 5 key chart positions (Sun, Moon, ASC, MC, Lot of Fortune),
evaluate all 7 traditional planets' dignity scores. The planet with the
highest cumulative score is the Almuten — the single most powerful planet
in the nativity.

Scoring per position (Ptolemaic):
  Domicile +5, Exaltation +4, Triplicity +3, Bound +2, Face +1

Sources: Ibn Ezra (The Beginning of Wisdom), Bonatti (Liber Astronomiae),
Al-Biruni (The Book of Instruction)
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

DOMICILE = {
    "Sun": ["Leo"], "Moon": ["Cancer"],
    "Mercury": ["Gemini", "Virgo"], "Venus": ["Taurus", "Libra"],
    "Mars": ["Aries", "Scorpio"], "Jupiter": ["Sagittarius", "Pisces"],
    "Saturn": ["Capricorn", "Aquarius"],
}

EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo",
    "Venus": "Pisces", "Mars": "Capricorn", "Jupiter": "Cancer",
    "Saturn": "Libra",
}

TRIPLICITY = {
    "Fire":  {"day": "Sun",    "night": "Jupiter"},
    "Earth": {"day": "Venus",  "night": "Moon"},
    "Air":   {"day": "Saturn", "night": "Mercury"},
    "Water": {"day": "Venus",  "night": "Mars"},
}

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

CHALDEAN_SEQUENCE = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]
TRADITIONAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def _bound_ruler(sign: str, deg: float) -> str:
    for ruler, end in EGYPTIAN_BOUNDS.get(sign, []):
        if deg < end:
            return ruler
    return EGYPTIAN_BOUNDS.get(sign, [("?", 30)])[-1][0]


def _face_ruler(longitude: float) -> str:
    return CHALDEAN_SEQUENCE[int(longitude / 10) % 36 % 7]


def _score_position(longitude: float, is_diurnal: bool) -> dict:
    """Score all 7 traditional planets for a single chart position."""
    sign_idx = int(longitude // 30) % 12
    sign = SIGNS[sign_idx]
    deg_in_sign = longitude % 30
    element = SIGN_ELEMENTS[sign]
    scores = {}

    for planet in TRADITIONAL_PLANETS:
        s = 0
        if sign in DOMICILE.get(planet, []):
            s += 5
        if EXALTATION.get(planet) == sign:
            s += 4
        trip = TRIPLICITY[element]
        trip_ruler = trip["day"] if is_diurnal else trip["night"]
        if planet == trip_ruler:
            s += 3
        if planet == _bound_ruler(sign, deg_in_sign):
            s += 2
        if planet == _face_ruler(longitude):
            s += 1
        scores[planet] = s

    return scores


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="almuten", name="Almuten Figuris (Lord of the Geniture)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    planets = natal_chart_data.get("planets", {})
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    sun_lon = planets["Sun"]["longitude"]
    desc_lon = (asc_lon + 180) % 360
    is_diurnal = ((sun_lon - desc_lon) % 360) < 180

    # 5 hylegical positions: Sun, Moon, ASC, MC, Fortune
    # Fortune longitude from arabic_parts or compute here
    moon_lon = planets["Moon"]["longitude"]
    if is_diurnal:
        fortune_lon = (asc_lon + moon_lon - sun_lon) % 360
    else:
        fortune_lon = (asc_lon + sun_lon - moon_lon) % 360

    mc_lon = natal_chart_data["midheaven"]["longitude"]

    positions = {
        "Sun": sun_lon,
        "Moon": moon_lon,
        "Ascendant": asc_lon,
        "Midheaven": mc_lon,
        "Fortune": fortune_lon,
    }

    # Accumulate scores across all 5 positions
    totals = {p: 0 for p in TRADITIONAL_PLANETS}
    position_detail = {}

    for pos_name, lon in positions.items():
        scores = _score_position(lon, is_diurnal)
        position_detail[pos_name] = {
            "longitude": round(lon, 2),
            "sign": SIGNS[int(lon // 30) % 12],
            "top_scorer": max(scores, key=scores.get),
            "top_score": max(scores.values()),
        }
        for planet, score in scores.items():
            totals[planet] += score

    # Rank planets by total score
    ranked = sorted(totals.items(), key=lambda x: -x[1])
    almuten = ranked[0][0]
    almuten_score = ranked[0][1]

    data = {
        "almuten": almuten,
        "almuten_score": almuten_score,
        "planet_scores": dict(ranked),
        "position_detail": position_detail,
        "is_diurnal": is_diurnal,
    }

    return SystemResult(
        id="almuten",
        name="Almuten Figuris (Lord of the Geniture)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Ibn Ezra, The Beginning of Wisdom — almuten calculation",
            "Bonatti, Liber Astronomiae — Lord of the Geniture",
            "Al-Biruni, The Book of Instruction — dignity accumulation",
        ],
        question="Q3_NATURE",
    )
