"""Midpoints — Ebertin Cosmobiology — COMPUTED_STRICT
Computes midpoints between all pairs of planets + ASC + MC and identifies
which natal bodies are conjunct a midpoint (within orb), revealing hidden
connections between planetary pairs.

The 90° sort (Ebertin dial) reduces all positions to a 0-90° range,
making squares and oppositions equivalent to conjunctions.

For each activated midpoint, the interpretation follows:
  Planet = Midpoint(A/B) means "Planet integrates the A/B principle"

Sources: Reinhold Ebertin (The Combination of Stellar Influences),
         Noel Tyl (Solar Arcs)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

MIDPOINT_ORB = 1.5  # degrees on the 360° wheel


def _shorter_midpoint(lon_a: float, lon_b: float) -> float:
    """Compute the nearer midpoint of two longitudes."""
    diff = (lon_b - lon_a) % 360
    if diff <= 180:
        return (lon_a + diff / 2) % 360
    else:
        return (lon_a + (diff + 360) / 2) % 360


def _angular_diff(a: float, b: float) -> float:
    """Shortest angular difference."""
    d = abs(a - b) % 360
    return min(d, 360 - d)


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="midpoints", name="Midpoints (Ebertin Cosmobiology)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    planets = natal_chart_data.get("planets", {})
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    mc_lon = natal_chart_data["midheaven"]["longitude"]

    # Build point list
    points = {}
    for name, pdata in planets.items():
        points[name] = pdata["longitude"]
    points["ASC"] = asc_lon
    points["MC"] = mc_lon

    point_names = list(points.keys())
    point_lons = list(points.values())

    # Compute all midpoints
    midpoints_list = []
    for i in range(len(point_names)):
        for j in range(i + 1, len(point_names)):
            mp = _shorter_midpoint(point_lons[i], point_lons[j])
            midpoints_list.append((point_names[i], point_names[j], mp))

    # Check which natal points activate a midpoint
    activations = []
    for body_name, body_lon in points.items():
        for pa, pb, mp_lon in midpoints_list:
            if body_name in (pa, pb):
                continue
            orb = _angular_diff(body_lon, mp_lon)
            if orb <= MIDPOINT_ORB:
                activations.append({
                    "planet": body_name,
                    "midpoint": f"{pa}/{pb}",
                    "midpoint_longitude": round(mp_lon, 2),
                    "orb": round(orb, 4),
                })
            # Also check opposition to midpoint
            opp = (mp_lon + 180) % 360
            orb_opp = _angular_diff(body_lon, opp)
            if orb_opp <= MIDPOINT_ORB:
                activations.append({
                    "planet": body_name,
                    "midpoint": f"{pa}/{pb}",
                    "midpoint_longitude": round(mp_lon, 2),
                    "orb": round(orb_opp, 4),
                    "type": "opposition",
                })

    # Sort by tightest orb
    activations.sort(key=lambda x: x["orb"])

    # Unique activated midpoints
    unique_midpoints = set()
    for a in activations:
        unique_midpoints.add(a["midpoint"])

    data = {
        "total_midpoints": len(midpoints_list),
        "activation_count": len(activations),
        "unique_midpoint_count": len(unique_midpoints),
        "activations": activations[:30],  # Top 30 tightest
    }

    return SystemResult(
        id="midpoints",
        name="Midpoints (Ebertin Cosmobiology)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Reinhold Ebertin, The Combination of Stellar Influences",
            "Noel Tyl, Solar Arcs — midpoint analysis",
        ],
        question="Q3_NATURE",
    )
