"""Aspects — Major Planetary Aspects
Given natal chart data (passed via kwargs), computes all major aspects
between planets with standard orbs.

Major aspects:
  Conjunction  0°   orb 8°
  Opposition 180°   orb 8°
  Trine      120°   orb 8°
  Square      90°   orb 8°
  Sextile     60°   orb 6°

Each aspect is classified as applying (planets moving closer) or separating.
Since we compute from a single birth moment, applying/separating is determined
by comparing faster vs slower planet speeds. Without speed data available from
the natal chart snapshot, we use the natural mean daily motion order.

COMPUTED_STRICT when natal_chart_data is present, NEEDS_INPUT when missing.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

ASPECTS = [
    {"name": "conjunction", "angle": 0, "orb": 8, "symbol": "\u260c"},
    {"name": "opposition", "angle": 180, "orb": 8, "symbol": "\u260d"},
    {"name": "trine", "angle": 120, "orb": 8, "symbol": "\u25b3"},
    {"name": "square", "angle": 90, "orb": 8, "symbol": "\u25a1"},
    {"name": "sextile", "angle": 60, "orb": 6, "symbol": "\u2731"},
]

# Mean daily motion (degrees/day) — used to determine applying vs separating
# Faster planet "applies" to slower planet when angular distance is decreasing
MEAN_DAILY_MOTION = {
    "Moon": 13.176,
    "Mercury": 1.383,
    "Venus": 1.200,
    "Sun": 0.986,
    "Mars": 0.524,
    "Jupiter": 0.083,
    "Saturn": 0.034,
    "Uranus": 0.012,
    "Neptune": 0.006,
    "Pluto": 0.004,
    "North Node": 0.053,
}

# Planet pairs to check (all unique pairs, excluding Node-Node)
PLANET_NAMES = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
                "North Node"]


def _angle_diff(lon1: float, lon2: float) -> float:
    """Smallest angular separation between two longitudes (0-180)."""
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="aspects",
            name="Aspects (Major)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q3_NATURE",
        )

    planets = natal_chart_data.get("planets", {})

    aspect_list = []

    for i in range(len(PLANET_NAMES)):
        for j in range(i + 1, len(PLANET_NAMES)):
            p1_name = PLANET_NAMES[i]
            p2_name = PLANET_NAMES[j]

            if p1_name not in planets or p2_name not in planets:
                continue

            lon1 = planets[p1_name]["longitude"]
            lon2 = planets[p2_name]["longitude"]
            separation = _angle_diff(lon1, lon2)

            for asp in ASPECTS:
                orb_actual = abs(separation - asp["angle"])
                if orb_actual <= asp["orb"]:
                    # Determine applying vs separating
                    # Faster planet applies to slower when moving toward exact aspect
                    speed1 = MEAN_DAILY_MOTION.get(p1_name, 0)
                    speed2 = MEAN_DAILY_MOTION.get(p2_name, 0)
                    if speed1 >= speed2:
                        faster, slower = p1_name, p2_name
                    else:
                        faster, slower = p2_name, p1_name

                    # If orb is very tight (<0.5°), call it exact
                    if orb_actual < 0.5:
                        phase = "exact"
                    else:
                        # Simplified: use orb direction as heuristic
                        # Applying = faster planet hasn't yet reached exact aspect
                        # We approximate: if faster planet's longitude puts it
                        # "before" the exact aspect point, it's applying
                        phase = "applying" if separation < asp["angle"] or (asp["angle"] == 0 and separation > 0) else "separating"
                        if asp["angle"] == 0:
                            # Conjunction: always separating if orb > 0
                            phase = "separating" if orb_actual > 0.5 else "exact"

                    aspect_list.append({
                        "planet_1": p1_name,
                        "planet_2": p2_name,
                        "aspect": asp["name"],
                        "angle": asp["angle"],
                        "orb": round(orb_actual, 2),
                        "phase": phase,
                    })
                    break  # One aspect per pair

    # Sort by tightest orb first
    aspect_list.sort(key=lambda a: a["orb"])

    # Summary counts
    counts = {}
    for a in aspect_list:
        counts[a["aspect"]] = counts.get(a["aspect"], 0) + 1

    data = {
        "aspect_count": len(aspect_list),
        "aspects": aspect_list,
        "summary": counts,
    }

    return SystemResult(
        id="aspects",
        name="Aspects (Major)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Standard Western orbs: conjunction/opposition/trine/square 8\u00b0, sextile 6\u00b0",
            "Ptolemy, Tetrabiblos — five major aspects",
        ],
        question="Q3_NATURE",
    )
