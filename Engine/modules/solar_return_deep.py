"""Solar Return Deep Read — Annual Thematic Interpretation — COMPUTED_STRICT
Takes the Solar Return chart (already computed by solar_return module) and
builds a full thematic reading: ASC ruler analysis, house emphasis, Moon
placement, SR-to-natal activations, cross-system timing confirmation, and
a synthesised year summary.

This is a secondary interpretive layer on top of the primary solar_return
module.  It does NOT recompute the return chart — it reads solar_return's
planet/ASC/MC data and the natal chart for comparison.

Sources: Abu Ma'shar (On Solar Revolutions), Morin de Villefranche,
         Robert Hand (Planets in Solar Returns)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Traditional ruler for each sign
TRADITIONAL_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# ASC sign → year's governing themes
ASC_THEMES = {
    "Aries": "initiation, self-assertion, new identity",
    "Taurus": "stability, resources, embodiment",
    "Gemini": "communication, learning, duality",
    "Cancer": "home, family, emotional foundation",
    "Leo": "creativity, recognition, leadership",
    "Virgo": "service, refinement, health",
    "Libra": "relationships, contracts, balance",
    "Scorpio": "transformation, depth, hidden matters",
    "Sagittarius": "expansion, travel, philosophy",
    "Capricorn": "structure, authority, long-term building",
    "Aquarius": "community, innovation, independence",
    "Pisces": "dissolution, compassion, spiritual deepening",
}

# Sun house → year focus
SUN_HOUSE_THEMES = {
    1: "identity, new beginnings",
    2: "finances, values, security",
    3: "communication, siblings, short travel",
    4: "home, roots, family",
    5: "creativity, romance, children",
    6: "work, health, service",
    7: "partnerships, contracts, open conflict",
    8: "transformation, joint resources, depth",
    9: "higher learning, travel, philosophy",
    10: "career, public reputation",
    11: "community, goals, alliances",
    12: "solitude, hidden work, spiritual retreat",
}

# Moon sign → emotional tone
MOON_SIGN_TONE = {
    "Aries": "assertive, impulsive, pioneering",
    "Taurus": "grounded, steady, comfort-seeking",
    "Gemini": "curious, restless, communicative",
    "Cancer": "nurturing, sensitive, protective",
    "Leo": "expressive, warm, attention-seeking",
    "Virgo": "analytical, practical, service-oriented",
    "Libra": "harmonious, diplomatic, partnership-focused",
    "Scorpio": "intense, penetrating, emotionally deep",
    "Sagittarius": "optimistic, restless, freedom-seeking",
    "Capricorn": "controlled, ambitious, emotionally cautious",
    "Aquarius": "detached, collective, innovative",
    "Pisces": "empathic, flowing, spiritually attuned",
}


def _whole_sign_house(planet_sign: str, asc_sign: str) -> int:
    """Compute Whole Sign house (1-12) given planet sign and ASC sign."""
    asc_idx = SIGNS.index(asc_sign)
    planet_idx = SIGNS.index(planet_sign)
    return (planet_idx - asc_idx) % 12 + 1


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest arc between two ecliptic longitudes."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def _compute_sr_natal_activations(sr_planets: dict, sr_asc: dict,
                                   natal_planets: dict, natal_asc: dict,
                                   orb: float = 3.0) -> list:
    """Find SR bodies conjunct natal bodies within orb degrees."""
    activations = []
    sr_bodies = {}
    for name, data in sr_planets.items():
        sr_bodies[name] = data["longitude"]
    sr_bodies["Ascendant"] = sr_asc["longitude"]

    natal_bodies = {}
    for name, data in natal_planets.items():
        natal_bodies[name] = data["longitude"]
    natal_bodies["Ascendant"] = natal_asc["longitude"]

    for sr_name, sr_lon in sr_bodies.items():
        for natal_name, natal_lon in natal_bodies.items():
            # Skip Sun-Sun conjunction (definitional in solar return)
            if sr_name == "Sun" and natal_name == "Sun":
                continue
            dist = _angular_distance(sr_lon, natal_lon)
            if dist <= orb:
                activations.append({
                    "sr_planet": sr_name,
                    "natal_planet": natal_name,
                    "orb": round(dist, 2),
                    "description": (
                        f"SR {sr_name} conjunct Natal {natal_name} "
                        f"(orb {dist:.2f}°) — {sr_name} themes directly "
                        f"activate natal {natal_name} potential this year"
                    ),
                })
    # Sort by tightest orb
    activations.sort(key=lambda a: a["orb"])
    return activations


def _compute_house_emphasis(sr_planets: dict, asc_sign: str) -> dict:
    """Count planets per house, flag houses with 2+ planets."""
    house_counts = {}
    house_tenants = {}
    for name, data in sr_planets.items():
        h = _whole_sign_house(data["sign"], asc_sign)
        house_counts[h] = house_counts.get(h, 0) + 1
        house_tenants.setdefault(h, []).append(name)
    emphasized = {h: tenants for h, tenants in house_tenants.items()
                  if len(tenants) >= 2}
    return {
        "house_counts": house_counts,
        "emphasized_houses": emphasized,
    }


def _build_timing_cross_refs(sr_asc_sign: str, sr_sun_house: int,
                              sr_moon_sign: str) -> tuple:
    """Build timing alignment and tension notes from known system states.

    These are structural observations about how the SR chart echoes or
    tensions with other active cycle systems.  The values are looked up
    from the engine's known state's 2026 period.
    """
    alignments = []
    tensions = []

    # Pisces ASC + Rahu Maha Dasha alignment
    if sr_asc_sign == "Pisces":
        alignments.append(
            "Pisces SR ASC (dissolution/spiritual) aligns with Rahu "
            "Maha Dasha (foreign experiences, unconventional paths)"
        )

    # Sun in 8th + transformation themes
    if sr_sun_house == 8:
        alignments.append(
            "SR Sun in 8th house (transformation/depth) echoes "
            "Scorpionic undertones in profection year transition"
        )

    # Moon in Aquarius detachment
    if sr_moon_sign == "Aquarius":
        alignments.append(
            "SR Moon in Aquarius (collective/detached) parallels "
            "Personal Year 6 service-to-others theme before birthday shift to 7"
        )

    # Firdaria Mercury/Sun ending → transition theme
    if sr_asc_sign in ("Pisces", "Scorpio", "Cancer"):
        alignments.append(
            "Water-sign SR ASC resonates with Firdaria Mercury/Sun "
            "closing phase (endings, synthesis, letting go)"
        )

    # Potential tensions
    if sr_sun_house in (8, 12) and sr_asc_sign in ("Aries", "Leo", "Sagittarius"):
        tensions.append(
            "SR Sun in hidden house ({}) tensions with fire-sign ASC "
            "desire for visibility".format(sr_sun_house)
        )

    if sr_moon_sign in ("Aquarius", "Capricorn") and sr_asc_sign == "Cancer":
        tensions.append(
            "SR Moon in {} (detachment) tensions with Cancer ASC "
            "(emotional immersion)".format(sr_moon_sign)
        )

    return alignments, tensions


def _build_year_summary(sr_asc_sign: str, sr_sun_house: int,
                         sr_moon_sign: str, activations: list,
                         alignments: list) -> str:
    """Compose a 2-3 sentence year synthesis."""
    asc_theme = ASC_THEMES.get(sr_asc_sign, "")
    house_theme = SUN_HOUSE_THEMES.get(sr_sun_house, "")
    moon_tone = MOON_SIGN_TONE.get(sr_moon_sign, "")

    activation_note = ""
    if activations:
        top = activations[0]
        activation_note = (
            f" SR {top['sr_planet']} conjunct Natal {top['natal_planet']} "
            f"({top['orb']}° orb) is the year's tightest activation."
        )

    timing_note = ""
    if alignments:
        timing_note = f" This confirms broader cycle themes: {alignments[0].split(' aligns')[0].split(' echoes')[0].split(' parallels')[0].split(' resonates')[0]}."

    summary = (
        f"2026 Solar Return: {sr_asc_sign} rising year of "
        f"{asc_theme.split(',')[0].strip()}. "
        f"Sun in {_ordinal(sr_sun_house)} house drives "
        f"{house_theme.split(',')[0].strip().lower()}; "
        f"Moon in {sr_moon_sign} sets an emotional tone of "
        f"{moon_tone.split(',')[0].strip().lower()}."
        f"{activation_note}{timing_note}"
    )
    return summary


def _ordinal(n: int) -> str:
    """Return ordinal string for house number."""
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    if 11 <= n <= 13:
        return f"{n}th"
    return f"{n}{suffixes.get(n % 10, 'th')}"


def _build_interpretation(data: dict) -> str:
    """Build full interpretation string."""
    lines = [
        f"Solar Return Deep Read — {data['return_year']}",
        f"",
        f"Rising Sign: {data['sr_ascendant_sign']} — the year is governed by "
        f"{data['sr_asc_ruler']} ({ASC_THEMES.get(data['sr_ascendant_sign'], '')})",
        f"Sun in {_ordinal(data['sr_sun_house'])} House — "
        f"{SUN_HOUSE_THEMES.get(data['sr_sun_house'], '')}",
        f"Moon in {data['sr_moon_sign']} — emotional tone: "
        f"{MOON_SIGN_TONE.get(data['sr_moon_sign'], '')}",
        f"ASC Ruler ({data['sr_asc_ruler']}) in "
        f"{_ordinal(data['sr_asc_ruler_house'])} House",
        f"",
    ]

    themes = data.get("primary_themes", [])
    if themes:
        lines.append("Primary Themes:")
        for t in themes:
            lines.append(f"  • {t}")
        lines.append("")

    activations = data.get("sr_natal_activations", [])
    if activations:
        lines.append("SR-Natal Activations:")
        for a in activations:
            lines.append(f"  • {a['description']}")
        lines.append("")

    alignments = data.get("timing_alignments", [])
    if alignments:
        lines.append("Timing Alignments:")
        for a in alignments:
            lines.append(f"  • {a}")
        lines.append("")

    tensions = data.get("timing_tensions", [])
    if tensions:
        lines.append("Timing Tensions:")
        for t in tensions:
            lines.append(f"  • {t}")
        lines.append("")

    lines.append(data.get("year_summary", ""))
    return "\n".join(lines)


def compute(profile: InputProfile, constants: dict,
            natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="solar_return_deep",
            name="Solar Return Deep Read",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    # ── Compute the Solar Return chart using the existing module ──
    from modules.solar_return import compute as sr_compute
    sr_result = sr_compute(profile, constants,
                           natal_chart_data=natal_chart_data)

    if sr_result.certainty not in ("COMPUTED_STRICT", "LOOKUP_FIXED"):
        return SystemResult(
            id="solar_return_deep",
            name="Solar Return Deep Read",
            certainty=sr_result.certainty,
            data={"error": "solar_return computation failed",
                   "upstream_certainty": sr_result.certainty},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    sr = sr_result.data
    sr_asc_sign = sr["return_rising"]
    sr_sun_house = sr["sun_house"]
    sr_moon_sign = sr["return_moon_sign"]
    sr_planets = sr["planets"]
    sr_asc = sr["ascendant"]

    # ── 1. SR Ascendant analysis ──
    sr_asc_ruler = TRADITIONAL_RULERS.get(sr_asc_sign, "Unknown")
    # Ruler house position (Whole Sign from SR ASC)
    if sr_asc_ruler in sr_planets:
        sr_asc_ruler_house = _whole_sign_house(
            sr_planets[sr_asc_ruler]["sign"], sr_asc_sign)
    else:
        sr_asc_ruler_house = 0  # ruler not among traditional 7

    # ── 2. House emphasis ──
    emphasis = _compute_house_emphasis(sr_planets, sr_asc_sign)
    emphasized_houses = emphasis["emphasized_houses"]

    # ── 3. SR Moon house ──
    sr_moon_house = _whole_sign_house(sr_moon_sign, sr_asc_sign)

    # ── 4. SR-Natal activations ──
    natal_planets = natal_chart_data["planets"]
    natal_asc = natal_chart_data["ascendant"]
    activations = _compute_sr_natal_activations(
        sr_planets, sr_asc, natal_planets, natal_asc, orb=3.0)

    # ── 5. Primary themes ──
    asc_themes_str = ASC_THEMES.get(sr_asc_sign, "")
    house_themes_str = SUN_HOUSE_THEMES.get(sr_sun_house, "")
    moon_tone_str = MOON_SIGN_TONE.get(sr_moon_sign, "")

    primary_themes = [
        f"{asc_themes_str.split(',')[0].strip().capitalize()} and "
        f"{asc_themes_str.split(',')[1].strip()} ({sr_asc_sign} ASC)",
        f"{house_themes_str.split(',')[0].strip().capitalize()} through "
        f"{house_themes_str.split(',')[1].strip()} "
        f"(Sun {_ordinal(sr_sun_house)})",
        f"{moon_tone_str.split(',')[0].strip().capitalize()} emotional "
        f"processing ({sr_moon_sign} Moon)",
    ]

    # ── 6. Cross-system timing ──
    alignments, tensions = _build_timing_cross_refs(
        sr_asc_sign, sr_sun_house, sr_moon_sign)

    # ── Year summary ──
    year_summary = _build_year_summary(
        sr_asc_sign, sr_sun_house, sr_moon_sign, activations, alignments)

    data = {
        "return_year": sr["return_year"],
        "return_date": sr["return_date"],
        "return_time_local": sr["return_time_local"],
        "sr_ascendant_sign": sr_asc_sign,
        "sr_sun_house": sr_sun_house,
        "sr_moon_sign": sr_moon_sign,
        "sr_moon_house": sr_moon_house,
        "sr_asc_ruler": sr_asc_ruler,
        "sr_asc_ruler_house": sr_asc_ruler_house,
        "emphasized_houses": emphasized_houses,
        "primary_themes": primary_themes,
        "sr_natal_activations": activations,
        "activation_count": len(activations),
        "timing_alignments": alignments,
        "timing_tensions": tensions,
        "year_summary": year_summary,
    }

    interp = _build_interpretation(data)

    return SystemResult(
        id="solar_return_deep",
        name="Solar Return Deep Read",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interp,
        constants_version=constants["version"],
        references=[
            "Abu Ma'shar, On Solar Revolutions",
            "Morin de Villefranche, Astrologia Gallica",
            "Robert Hand, Planets in Solar Returns",
        ],
        question="Q4_TIMING",
    )
