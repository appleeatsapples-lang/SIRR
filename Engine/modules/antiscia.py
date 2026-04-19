"""Antiscia — Shadow Degrees (Solstice Axis Reflection)
Each planet's longitude reflected across the 0° Cancer/0° Capricorn axis,
producing a "hidden" mirror position. When a planet's antiscion falls on
another planet's natal position (within orb), it indicates a concealed connection.

Formula:
  antiscia(lon) = (180 - lon) % 360
  contra_antiscia(lon) = (antiscia + 180) % 360

Requires natal_chart_data (passed via kwargs from runner.py).

COMPUTED_STRICT when natal_chart_data is present, NEEDS_INPUT when missing.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PLANET_NAMES = [
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
    "North Node",
]

ORB = 2.0


def _sign_of(lon: float) -> str:
    """Return zodiac sign for a given longitude."""
    return SIGNS[int(lon % 360) // 30]


def _angle_diff(lon1: float, lon2: float) -> float:
    """Smallest angular separation (0-180)."""
    diff = abs(lon1 - lon2) % 360
    return diff if diff <= 180 else 360 - diff


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="antiscia",
            name="Antiscia (Shadow Degrees)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    planets_data = natal_chart_data.get("planets", {})

    # Compute antiscia and contra-antiscia for each body
    planets = {}
    for name in PLANET_NAMES:
        if name not in planets_data:
            continue
        lon = planets_data[name]["longitude"]
        anti = (180 - lon) % 360
        contra = (anti + 180) % 360
        planets[name] = {
            "natal_longitude": round(lon, 4),
            "antiscia": round(anti, 4),
            "contra_antiscia": round(contra, 4),
            "antiscia_sign": _sign_of(anti),
            "contra_antiscia_sign": _sign_of(contra),
        }

    # Detect conjunctions: each planet's antiscia/contra vs all other planets' natal
    # Only check i < j to avoid duplicate pairs (A→B and B→A)
    conjunctions = []
    planet_list = list(planets.keys())
    seen_pairs = set()
    for i, p1 in enumerate(planet_list):
        for shadow_type, shadow_key in [("antiscia", "antiscia"), ("contra_antiscia", "contra_antiscia")]:
            shadow_lon = planets[p1][shadow_key]
            for j, p2 in enumerate(planet_list):
                if i == j:
                    continue
                # Deduplicate: normalize pair so (A,B) == (B,A)
                pair_key = tuple(sorted([p1, p2])) + (shadow_type,)
                if pair_key in seen_pairs:
                    continue
                natal_lon = planets[p2]["natal_longitude"]
                orb_actual = _angle_diff(shadow_lon, natal_lon)
                if orb_actual <= ORB:
                    seen_pairs.add(pair_key)
                    conjunctions.append({
                        "planet1": p1,
                        "type": shadow_type,
                        "planet2": p2,
                        "planet1_shadow": shadow_lon,
                        "planet2_natal": natal_lon,
                        "orb": round(orb_actual, 2),
                    })

    conjunctions.sort(key=lambda c: c["orb"])

    # Detect notable shadow-shadow pairs (antiscia/contra of different planets near each other)
    notable_shadow_pairs = []
    for i in range(len(planet_list)):
        for j in range(i + 1, len(planet_list)):
            p1, p2 = planet_list[i], planet_list[j]
            # Check all shadow-shadow combinations
            for label1, key1 in [("antiscia", "antiscia"), ("contra-antiscia", "contra_antiscia")]:
                for label2, key2 in [("antiscia", "antiscia"), ("contra-antiscia", "contra_antiscia")]:
                    lon1 = planets[p1][key1]
                    lon2 = planets[p2][key2]
                    orb_actual = _angle_diff(lon1, lon2)
                    if orb_actual <= ORB:
                        notable_shadow_pairs.append({
                            "shadow1": f"{p1} {label1}",
                            "shadow2": f"{p2} {label2}",
                            "longitude1": lon1,
                            "longitude2": lon2,
                            "orb": round(orb_actual, 2),
                        })

    notable_shadow_pairs.sort(key=lambda s: s["orb"])

    data = {
        "planets": planets,
        "conjunctions": conjunctions,
        "conjunction_count": len(conjunctions),
        "notable_shadow_pairs": notable_shadow_pairs,
        "orb_used": ORB,
    }

    return SystemResult(
        id="antiscia",
        name="Antiscia (Shadow Degrees)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Ptolemy, Tetrabiblos — antiscia as 'commanding/obeying' signs",
            "Lilly, William. Christian Astrology (1647) — shadow degree conjunctions",
        ],
        question="Q4_TIMING",
    )
