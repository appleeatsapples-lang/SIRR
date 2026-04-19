"""Draconic Chart — Soul's Pre-Incarnation Blueprint — COMPUTED_STRICT

The Draconic chart rotates the entire natal chart so that the North Node
sits at 0° Aries. This reveals the soul's essential pattern before this
life's conditioning — the karmic template carried from previous cycles.

Computation:
  draconic_longitude = (natal_longitude - north_node_longitude) % 360

Comparing draconic to natal positions reveals where soul-level patterns
directly activate the personality. Conjunctions within 2° orb are the
most significant draconic-natal contacts.

Sources:
  - Pamela Crane — The Draconic Chart (Astrology Quarterly, 1987)
  - Dennis Elwell — Cosmic Loom (draconic theory)
  - Zipporah Dobyns — Node-based chart systems
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Planets to compute draconic positions for
PLANET_NAMES = [
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "North Node",
]

CONJUNCTION_ORB = 2.0  # degrees


def _format_position(longitude: float) -> dict:
    """Convert longitude to sign, degree, formatted string."""
    lon = longitude % 360
    sign_idx = int(lon / 30) % 12
    deg_in_sign = lon % 30
    degree = int(deg_in_sign)
    minute = int((deg_in_sign - degree) * 60)
    return {
        "longitude": round(lon, 4),
        "sign": SIGNS[sign_idx],
        "degree": degree,
        "minute": minute,
        "formatted": f"{degree}\u00b0{minute:02d}' {SIGNS[sign_idx]}",
    }


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes (0-180)."""
    diff = abs((lon1 - lon2) % 360)
    if diff > 180:
        diff = 360 - diff
    return diff


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="draconic_chart",
            name="Draconic Chart (Soul Blueprint)",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "Requires natal_chart_data"},
            interpretation=None,
            constants_version=constants.get("version", "unknown"),
            references=[],
        )

    planets_data = natal_chart_data.get("planets", {})

    # Get North Node longitude
    nn_data = planets_data.get("North Node")
    if nn_data is None:
        return SystemResult(
            id="draconic_chart",
            name="Draconic Chart (Soul Blueprint)",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "North Node not found in natal_chart_data"},
            interpretation=None,
            constants_version=constants.get("version", "unknown"),
            references=[],
        )

    nn_lon = nn_data.get("longitude", 0)
    node_type = "mean_node"  # natal_chart uses swe.MEAN_NODE (id 10)

    # Compute draconic positions for planets
    draconic_positions = {}
    natal_longitudes = {}  # for conjunction check

    for pname in PLANET_NAMES:
        pdata = planets_data.get(pname)
        if pdata is None:
            continue
        natal_lon = pdata.get("longitude", 0)
        natal_longitudes[pname] = natal_lon
        drac_lon = (natal_lon - nn_lon) % 360
        draconic_positions[pname] = _format_position(drac_lon)

    # Ascendant
    asc_data = natal_chart_data.get("ascendant", {})
    asc_lon = asc_data.get("longitude", 0)
    natal_longitudes["Ascendant"] = asc_lon
    drac_asc_lon = (asc_lon - nn_lon) % 360
    draconic_positions["Ascendant"] = _format_position(drac_asc_lon)

    # MC (midheaven)
    mc_data = natal_chart_data.get("midheaven", {})
    mc_lon = mc_data.get("longitude", 0)
    if mc_lon:
        natal_longitudes["MC"] = mc_lon
        drac_mc_lon = (mc_lon - nn_lon) % 360
        draconic_positions["MC"] = _format_position(drac_mc_lon)

    # Extract key signs
    draconic_sun_sign = draconic_positions.get("Sun", {}).get("sign", "unknown")
    draconic_moon_sign = draconic_positions.get("Moon", {}).get("sign", "unknown")
    draconic_asc_sign = draconic_positions.get("Ascendant", {}).get("sign", "unknown")

    natal_sun_sign = natal_chart_data.get("sun_sign", SIGNS[int(planets_data.get("Sun", {}).get("longitude", 0) / 30) % 12])
    natal_moon_sign = natal_chart_data.get("moon_sign", SIGNS[int(planets_data.get("Moon", {}).get("longitude", 0) / 30) % 12])

    sun_sign_shift = f"{natal_sun_sign} \u2192 {draconic_sun_sign} (draconic)"
    moon_sign_shift = f"{natal_moon_sign} \u2192 {draconic_moon_sign} (draconic)"

    # Draconic-to-natal conjunctions (2° orb)
    conjunctions = []
    drac_planet_names = [p for p in PLANET_NAMES if p in draconic_positions]
    drac_planet_names.append("Ascendant")
    if "MC" in draconic_positions:
        drac_planet_names.append("MC")

    natal_planet_names = list(PLANET_NAMES) + ["Ascendant"]
    if "MC" in natal_longitudes:
        natal_planet_names.append("MC")

    for dp in drac_planet_names:
        drac_lon = draconic_positions[dp]["longitude"]
        for np_name in natal_planet_names:
            if np_name not in natal_longitudes:
                continue
            nat_lon = natal_longitudes[np_name]
            orb = _angular_distance(drac_lon, nat_lon)
            if orb <= CONJUNCTION_ORB:
                # Skip trivial self-conjunction of North Node (draconic NN is always 0° Aries)
                if dp == "North Node" and np_name == "North Node":
                    continue
                conjunctions.append({
                    "draconic_planet": dp,
                    "natal_planet": np_name,
                    "orb": round(orb, 2),
                    "description": f"Draconic {dp} conjunct Natal {np_name} \u2014 {orb:.2f}\u00b0",
                })

    conjunctions.sort(key=lambda x: x["orb"])

    # Interpretation
    interp_parts = [
        f"Draconic Sun in {draconic_sun_sign} \u2014 the soul's essential solar drive "
        f"before this life's conditioning ({sun_sign_shift}). ",
        f"Draconic Moon in {draconic_moon_sign} \u2014 the soul's emotional template ({moon_sign_shift}). ",
        f"Draconic Ascendant in {draconic_asc_sign}. ",
    ]

    if conjunctions:
        interp_parts.append(
            f"{len(conjunctions)} draconic-to-natal conjunction(s) found within {CONJUNCTION_ORB}\u00b0, "
            f"indicating direct soul-blueprint activations: "
        )
        for c in conjunctions[:3]:
            interp_parts.append(f"{c['description']}. ")
    else:
        interp_parts.append("No tight draconic-to-natal conjunctions within 2\u00b0. ")

    data = {
        "north_node_used": round(nn_lon, 4),
        "node_type": node_type,
        "draconic_positions": draconic_positions,
        "draconic_sun_sign": draconic_sun_sign,
        "draconic_moon_sign": draconic_moon_sign,
        "draconic_asc_sign": draconic_asc_sign,
        "draconic_natal_conjunctions": conjunctions,
        "sun_sign_shift": sun_sign_shift,
        "moon_sign_shift": moon_sign_shift,
    }

    return SystemResult(
        id="draconic_chart",
        name="Draconic Chart (Soul Blueprint)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation="".join(interp_parts),
        constants_version=constants.get("version", "unknown"),
        references=[
            "Pamela Crane \u2014 The Draconic Chart (Astrology Quarterly, 1987)",
            "Dennis Elwell \u2014 Cosmic Loom (draconic theory)",
            "Zipporah Dobyns \u2014 Node-based chart systems",
        ],
    )
