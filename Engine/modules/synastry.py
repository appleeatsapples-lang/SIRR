"""Synastry — Cross-Chart Relationship Analysis — COMPUTED_STRICT
Compares two natal charts to compute cross-chart aspects, composite
midpoints, and SIRR numerological compatibility metrics.

Sources: Liz Greene (Relating), Robert Hand (Planets in Composite),
         Stephen Arroyo (Chart Interpretation Handbook)
"""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# Aspect definitions: (name, exact_angle, orb, nature)
ASPECTS = [
    ("conjunction", 0, 8, "neutral"),
    ("sextile", 60, 4, "harmonious"),
    ("square", 90, 6, "challenging"),
    ("trine", 120, 6, "harmonious"),
    ("opposition", 180, 8, "challenging"),
]

# Conjunction nature depends on planets involved
CONJUNCTION_NATURE = {
    ("Sun", "Moon"): "harmonious",
    ("Venus", "Mars"): "harmonious",
    ("Venus", "Jupiter"): "harmonious",
    ("Sun", "Venus"): "harmonious",
    ("Moon", "Venus"): "harmonious",
    ("Sun", "Jupiter"): "harmonious",
    ("Saturn", "Sun"): "challenging",
    ("Saturn", "Moon"): "challenging",
    ("Mars", "Saturn"): "challenging",
}

# Significance weighting for aspect pairs
SIGNIFICANCE = {
    ("Sun", "Moon"): 10,
    ("Moon", "Moon"): 9,
    ("Venus", "Mars"): 9,
    ("Sun", "Sun"): 8,
    ("Moon", "Venus"): 8,
    ("Sun", "Venus"): 7,
    ("Venus", "Venus"): 7,
    ("Mars", "Mars"): 6,
    ("Saturn", "Sun"): 6,
    ("Saturn", "Moon"): 6,
    ("Jupiter", "Venus"): 5,
}

# Life Path compatibility table (classic numerology)
LP_COMPAT = {
    (1, 1): "dynamic", (1, 2): "complementary", (1, 3): "highly compatible",
    (1, 4): "challenging", (1, 5): "highly compatible", (1, 6): "compatible",
    (1, 7): "compatible", (1, 8): "dynamic", (1, 9): "highly compatible",
    (2, 2): "compatible", (2, 3): "compatible", (2, 4): "highly compatible",
    (2, 5): "challenging", (2, 6): "highly compatible", (2, 7): "compatible",
    (2, 8): "compatible", (2, 9): "compatible",
    (3, 3): "dynamic", (3, 4): "challenging", (3, 5): "highly compatible",
    (3, 6): "highly compatible", (3, 7): "challenging", (3, 8): "compatible",
    (3, 9): "highly compatible",
    (4, 4): "compatible", (4, 5): "challenging", (4, 6): "compatible",
    (4, 7): "compatible", (4, 8): "highly compatible", (4, 9): "challenging",
    (5, 5): "dynamic", (5, 6): "challenging", (5, 7): "highly compatible",
    (5, 8): "compatible", (5, 9): "compatible",
    (6, 6): "highly compatible", (6, 7): "challenging", (6, 8): "compatible",
    (6, 9): "highly compatible",
    (7, 7): "compatible", (7, 8): "challenging", (7, 9): "compatible",
    (8, 8): "dynamic", (8, 9): "compatible",
    (9, 9): "compatible",
}

# Aspect brief descriptions
ASPECT_DESCRIPTIONS = {
    ("Sun", "Moon", "conjunction"): "Core identity fuses with emotional nature — deep instinctive bond",
    ("Sun", "Moon", "opposition"): "Identity-emotion polarity creates attraction through difference",
    ("Sun", "Moon", "trine"): "Natural flow between identity and emotional needs",
    ("Sun", "Moon", "square"): "Tension between will and emotional needs drives growth",
    ("Sun", "Moon", "sextile"): "Gentle harmony between purpose and feelings",
    ("Venus", "Mars", "conjunction"): "Strong physical and romantic attraction",
    ("Venus", "Mars", "opposition"): "Magnetic attraction through polarity",
    ("Venus", "Mars", "trine"): "Easy-flowing romantic and creative chemistry",
    ("Venus", "Mars", "square"): "Passionate tension — attraction with friction",
    ("Venus", "Mars", "sextile"): "Gentle attraction and creative compatibility",
    ("Moon", "Moon", "conjunction"): "Deep emotional resonance — feel at home together",
    ("Moon", "Moon", "opposition"): "Complementary emotional styles",
    ("Moon", "Moon", "trine"): "Natural emotional understanding",
    ("Moon", "Moon", "square"): "Emotional friction requiring adjustment",
    ("Saturn", "Sun", "conjunction"): "Commitment and structure around identity",
    ("Saturn", "Moon", "conjunction"): "Emotional discipline — serious bond",
    ("Sun", "Sun", "conjunction"): "Shared identity and purpose",
    ("Sun", "Sun", "trine"): "Harmonious goals and self-expression",
}


def _angular_distance(lon1: float, lon2: float) -> float:
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def _sign_of(lon: float) -> str:
    return SIGNS[int(lon // 30) % 12]


def _midpoint(lon1: float, lon2: float) -> float:
    """Compute shorter-arc midpoint of two longitudes."""
    diff = (lon2 - lon1) % 360
    if diff <= 180:
        return (lon1 + diff / 2) % 360
    else:
        return (lon1 + (diff - 360) / 2) % 360


def _reduce(n: int) -> int:
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n


def _get_conjunction_nature(p_a: str, p_b: str) -> str:
    """Determine nature of a conjunction based on planets involved."""
    pair = (p_a, p_b)
    rev = (p_b, p_a)
    if pair in CONJUNCTION_NATURE:
        return CONJUNCTION_NATURE[pair]
    if rev in CONJUNCTION_NATURE:
        return CONJUNCTION_NATURE[rev]
    return "neutral"


def _get_description(p_a: str, p_b: str, aspect_name: str) -> str:
    """Get description for an aspect, checking both orderings."""
    key = (p_a, p_b, aspect_name)
    rev = (p_b, p_a, aspect_name)
    if key in ASPECT_DESCRIPTIONS:
        return ASPECT_DESCRIPTIONS[key]
    if rev in ASPECT_DESCRIPTIONS:
        return ASPECT_DESCRIPTIONS[rev]
    return f"{p_a}-{p_b} {aspect_name}: cross-chart activation"


def _get_significance(p_a: str, p_b: str) -> int:
    pair = (p_a, p_b)
    rev = (p_b, p_a)
    return SIGNIFICANCE.get(pair, SIGNIFICANCE.get(rev, 3))


def _compute_cross_aspects(planets_a: dict, planets_b: dict,
                            asc_a: dict = None, asc_b: dict = None) -> list:
    """Compute all cross-chart aspects between two sets of planets."""
    aspects = []

    bodies_a = {name: planets_a[name]["longitude"] for name in PLANETS
                if name in planets_a}
    bodies_b = {name: planets_b[name]["longitude"] for name in PLANETS
                if name in planets_b}

    # Add ASC if available
    if asc_a:
        bodies_a["Ascendant"] = asc_a["longitude"]
    if asc_b:
        bodies_b["Ascendant"] = asc_b["longitude"]

    for name_a, lon_a in bodies_a.items():
        for name_b, lon_b in bodies_b.items():
            dist = _angular_distance(lon_a, lon_b)
            for asp_name, asp_angle, asp_orb, asp_nature in ASPECTS:
                if abs(dist - asp_angle) <= asp_orb:
                    orb = round(abs(dist - asp_angle), 2)
                    nature = asp_nature
                    if asp_name == "conjunction":
                        nature = _get_conjunction_nature(name_a, name_b)

                    significance = _get_significance(name_a, name_b)
                    desc = _get_description(name_a, name_b, asp_name)

                    aspects.append({
                        "planet_a": name_a,
                        "planet_b": name_b,
                        "aspect": asp_name,
                        "orb": orb,
                        "nature": nature,
                        "significance": significance,
                        "description": desc,
                    })
                    break  # only one aspect per pair

    return aspects


def _compute_composite(planets_a: dict, planets_b: dict,
                        asc_a: dict = None, asc_b: dict = None) -> dict:
    """Compute composite (midpoint) chart positions."""
    composite = {}
    for name in PLANETS:
        if name in planets_a and name in planets_b:
            mid = _midpoint(planets_a[name]["longitude"],
                            planets_b[name]["longitude"])
            composite[name] = {
                "longitude": round(mid, 4),
                "sign": _sign_of(mid),
            }

    if asc_a and asc_b:
        mid = _midpoint(asc_a["longitude"], asc_b["longitude"])
        composite["Ascendant"] = {
            "longitude": round(mid, 4),
            "sign": _sign_of(mid),
        }

    return composite


def _lp_compatibility(lp_a: int, lp_b: int) -> str:
    """Look up Life Path compatibility."""
    # Reduce master numbers for lookup
    a = lp_a if lp_a <= 9 else _reduce(lp_a)
    b = lp_b if lp_b <= 9 else _reduce(lp_b)
    lo, hi = min(a, b), max(a, b)
    return LP_COMPAT.get((lo, hi), "neutral")


def _compute_abjad_roots(profile_a: InputProfile,
                          profile_b: InputProfile) -> list:
    """Find shared abjad root numbers between two profiles."""
    shared = []
    # Life path roots
    lp_a = _reduce(profile_a.life_path)
    lp_b = _reduce(profile_b.life_path)
    if lp_a == lp_b:
        shared.append({"value": lp_a, "source": "life_path"})

    # Birthday number
    bd_a = profile_a.birthday_number
    bd_b = profile_b.birthday_number
    if bd_a and bd_b and bd_a == bd_b:
        shared.append({"value": bd_a, "source": "birthday_number"})

    # Expression
    expr_a = _reduce(profile_a.expression) if profile_a.expression else None
    expr_b = _reduce(profile_b.expression) if profile_b.expression else None
    if expr_a and expr_b and expr_a == expr_b:
        shared.append({"value": expr_a, "source": "expression"})

    # Abjad first name
    abjad_a = profile_a.abjad_first
    abjad_b = profile_b.abjad_first
    if abjad_a and abjad_b:
        root_a = _reduce(abjad_a)
        root_b = _reduce(abjad_b)
        if root_a == root_b:
            shared.append({"value": root_a, "source": "abjad_first_root"})

    return shared


def _determine_connection_type(harmony: float, challenge: float,
                                shared_roots: list) -> str:
    """Determine the connection archetype."""
    if len(shared_roots) >= 2:
        return "mirror"
    if harmony > 0.6 and challenge < 0.3:
        return "complementary"
    if harmony > 0.3 and challenge > 0.3:
        return "dynamic"
    return "complex"


def _compute_noon_chart(profile: InputProfile) -> dict:
    """Compute a solar-noon chart for DOB-only profiles (no birth time).

    Returns planet positions computed at noon local time on DOB.
    ASC/MC are NOT reliable without birth time, so excluded.
    """
    import swisseph as swe
    swe.set_ephe_path(None)

    tz_offset = 3.0  # default
    try:
        from modules.natal_chart import TZ_OFFSETS
        if profile.timezone:
            tz_offset = TZ_OFFSETS.get(profile.timezone, 3.0)
    except ImportError:
        pass

    jd = swe.julday(profile.dob.year, profile.dob.month,
                     profile.dob.day, 12.0 - tz_offset)

    planet_ids = [
        ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
        ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
        ("Saturn", swe.SATURN),
    ]

    planets = {}
    for name, pid in planet_ids:
        r = swe.calc_ut(jd, pid)
        lon = r[0][0]
        planets[name] = {
            "longitude": round(lon, 4),
            "sign": _sign_of(lon),
        }

    return {"planets": planets}


def _load_second_profile(path: str) -> tuple:
    """Load second profile and compute natal chart."""
    from runner import load_profile, load_constants
    from modules.natal_chart import compute as compute_natal

    profile_b = load_profile(path)
    constants = load_constants()
    natal_b = compute_natal(profile_b, constants)
    if natal_b.certainty == "COMPUTED_STRICT":
        natal_data_b = natal_b.data
    else:
        # Fall back to noon chart for DOB-only profiles
        natal_data_b = _compute_noon_chart(profile_b)
    return profile_b, natal_data_b, constants


def compute(profile: InputProfile, constants: dict,
            natal_chart_data: dict = None, **kwargs) -> SystemResult:
    second_profile_path = kwargs.get("second_profile_path")
    second_natal_data = kwargs.get("second_natal_data")
    second_profile = kwargs.get("second_profile")

    if not second_profile_path and not second_natal_data:
        return SystemResult(
            id="synastry",
            name="Synastry",
            certainty="NEEDS_INPUT",
            data={
                "status": "no second profile provided",
                "usage": "add second_profile_path to profile fixture",
            },
            interpretation="Synastry requires a second person's profile.",
            constants_version=constants["version"],
            references=[],
            question="Q5_RELATIONSHIP",
        )

    # Load second profile if needed
    profile_b = second_profile
    natal_data_b = second_natal_data

    if second_profile_path and (profile_b is None or natal_data_b is None):
        profile_b, natal_data_b, _ = _load_second_profile(second_profile_path)

    # Use noon charts as fallback for DOB-only profiles
    chart_a = natal_chart_data
    chart_b = natal_data_b
    has_full_chart = True

    if chart_a is None:
        chart_a = _compute_noon_chart(profile)
        has_full_chart = False
    if chart_b is None:
        chart_b = _compute_noon_chart(profile_b)
        has_full_chart = False

    if chart_a is None or chart_b is None:
        certainty = "APPROX"
        cross_aspects = []
        composite = {}
        key_aspects = []
    else:
        certainty = "COMPUTED_STRICT" if has_full_chart else "APPROX"
        planets_a = chart_a["planets"]
        planets_b = chart_b["planets"]
        asc_a = chart_a.get("ascendant")
        asc_b = chart_b.get("ascendant")

        # 1. Cross-chart aspects
        cross_aspects = _compute_cross_aspects(
            planets_a, planets_b, asc_a, asc_b)

        # 2. Composite midpoints
        composite = _compute_composite(planets_a, planets_b, asc_a, asc_b)

        # Key aspects (top 5 by significance, then tightest orb)
        key_aspects = sorted(cross_aspects,
                              key=lambda a: (-a["significance"], a["orb"]))[:5]

    # 3. SIRR cross-profile metrics
    combined_lp = _reduce(profile.life_path + profile_b.life_path)
    lp_compat = _lp_compatibility(profile.life_path, profile_b.life_path)
    shared_roots = _compute_abjad_roots(profile, profile_b)

    sirr_metrics = {
        "combined_life_path": combined_lp,
        "lp_compatibility": lp_compat,
        "shared_abjad_roots": shared_roots,
        "shared_meta_patterns": [],  # populated if synthesis data available
    }

    # 4. Summary scores
    total = len(cross_aspects)
    harmonious = sum(1 for a in cross_aspects if a["nature"] == "harmonious")
    challenging = sum(1 for a in cross_aspects if a["nature"] == "challenging")

    harmony_score = round(harmonious / total, 3) if total > 0 else 0.0
    challenge_score = round(challenging / total, 3) if total > 0 else 0.0
    connection_type = _determine_connection_type(
        harmony_score, challenge_score, shared_roots)

    # Composite signs
    comp_sun_sign = composite.get("Sun", {}).get("sign", "unknown")
    comp_moon_sign = composite.get("Moon", {}).get("sign", "unknown")

    # Build interpretation
    interp_parts = [
        f"Synastry: {profile.subject} × {profile_b.subject}",
        f"Total cross-aspects: {total} ({harmonious} harmonious, "
        f"{challenging} challenging)",
        f"Connection type: {connection_type}",
        f"Harmony: {harmony_score:.1%}, Challenge: {challenge_score:.1%}",
        f"Combined Life Path: {combined_lp} ({lp_compat})",
        f"Composite Sun: {comp_sun_sign}, Composite Moon: {comp_moon_sign}",
    ]
    if key_aspects:
        interp_parts.append("Key aspects:")
        for ka in key_aspects:
            interp_parts.append(
                f"  {ka['planet_a']}-{ka['planet_b']} {ka['aspect']} "
                f"({ka['orb']}°): {ka['description']}")
    if shared_roots:
        roots_str = ", ".join(
            f"{r['source']}={r['value']}" for r in shared_roots)
        interp_parts.append(f"Shared roots: {roots_str}")
    interpretation = "\n".join(interp_parts)

    data = {
        "person_a": {
            "name": profile.subject,
            "dob": profile.dob.isoformat(),
            "life_path": profile.life_path,
        },
        "person_b": {
            "name": profile_b.subject,
            "dob": profile_b.dob.isoformat(),
            "life_path": profile_b.life_path,
        },
        "cross_aspects": cross_aspects,
        "key_aspects": key_aspects,
        "composite_sun_sign": comp_sun_sign,
        "composite_moon_sign": comp_moon_sign,
        "sirr_metrics": sirr_metrics,
        "harmony_score": harmony_score,
        "challenge_score": challenge_score,
        "connection_type": connection_type,
        "total_aspects_found": total,
        "interpretation": interpretation,
    }

    return SystemResult(
        id="synastry",
        name="Synastry",
        certainty=certainty,
        data=data,
        interpretation=interpretation,
        constants_version=constants["version"],
        references=[
            "Liz Greene, Relating: An Astrological Guide to Living with Others",
            "Robert Hand, Planets in Composite",
            "Stephen Arroyo, Chart Interpretation Handbook",
        ],
        question="Q5_RELATIONSHIP",
    )
