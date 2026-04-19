"""Sect — Diurnal/Nocturnal Chart Classification — COMPUTED_STRICT
Determines whether the chart is diurnal (day) or nocturnal (night) based on
the Sun's position relative to the horizon, then classifies each planet's
sect condition.

Sect is arguably the single most important Hellenistic distinction:
- Diurnal sect: Sun, Jupiter, Saturn
- Nocturnal sect: Moon, Venus, Mars
- Mercury: sect of the Sun (morning star = diurnal, evening star = nocturnal)

A planet "in sect" operates at its best; "contrary to sect" is challenged.
The benefic of sect (Jupiter day / Venus night) is the most helpful planet.
The malefic contrary to sect (Saturn night / Mars day) is the most challenging.

Additional sect conditions per Valens:
- A diurnal planet is "rejoicing" in a masculine sign above the horizon (day)
- A nocturnal planet is "rejoicing" in a feminine sign below the horizon (night)

Sources: Vettius Valens (Anthology), Ptolemy (Tetrabiblos), Firmicus Maternus
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Sign gender/polarity (masculine = odd signs, feminine = even signs)
MASCULINE_SIGNS = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
FEMININE_SIGNS = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"}

# Sect allegiance
DIURNAL_PLANETS = {"Sun", "Jupiter", "Saturn"}
NOCTURNAL_PLANETS = {"Moon", "Venus", "Mars"}


def _is_above_horizon(planet_lon: float, asc_lon: float) -> bool:
    """A planet is above the horizon if it's between DESC and ASC
    going counter-clockwise (houses 7-12)."""
    desc_lon = (asc_lon + 180) % 360
    return ((planet_lon - desc_lon) % 360) < 180


def _mercury_sect(mercury_lon: float, sun_lon: float) -> str:
    """Mercury is diurnal when it rises before the Sun (morning star),
    nocturnal when it sets after the Sun (evening star).
    Approximation: Mercury east of Sun (greater longitude) = evening star."""
    diff = (mercury_lon - sun_lon) % 360
    return "nocturnal" if diff < 180 else "diurnal"


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="sect",
            name="Sect (Diurnal/Nocturnal)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    planets = natal_chart_data.get("planets", {})
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    sun_lon = planets["Sun"]["longitude"]

    # Core determination: is the Sun above the horizon?
    is_diurnal = _is_above_horizon(sun_lon, asc_lon)
    chart_sect = "diurnal" if is_diurnal else "nocturnal"

    # Mercury's sect
    merc_sect = _mercury_sect(planets["Mercury"]["longitude"], sun_lon)

    # Classify each planet
    planet_conditions = {}
    for planet_name, planet_data in planets.items():
        if planet_name in ("Uranus", "Neptune", "Pluto", "North Node"):
            continue  # Outer planets and nodes have no traditional sect

        sign = planet_data["sign"]
        lon = planet_data["longitude"]
        above = _is_above_horizon(lon, asc_lon)
        is_masculine_sign = sign in MASCULINE_SIGNS

        if planet_name == "Mercury":
            natural_sect = merc_sect
        elif planet_name in DIURNAL_PLANETS:
            natural_sect = "diurnal"
        else:
            natural_sect = "nocturnal"

        in_sect = (natural_sect == chart_sect)

        # Hayz / rejoicing condition (Valens)
        # Diurnal planet rejoices: masculine sign + above horizon (in day chart)
        # Nocturnal planet rejoices: feminine sign + below horizon (in night chart)
        if natural_sect == "diurnal":
            rejoicing = is_masculine_sign and above
        else:
            rejoicing = not is_masculine_sign and not above

        planet_conditions[planet_name] = {
            "natural_sect": natural_sect,
            "in_sect": in_sect,
            "above_horizon": above,
            "sign_gender": "masculine" if is_masculine_sign else "feminine",
            "rejoicing": rejoicing,
        }

    # Identify key sect roles
    benefic_of_sect = "Jupiter" if is_diurnal else "Venus"
    benefic_contrary = "Venus" if is_diurnal else "Jupiter"
    malefic_of_sect = "Saturn" if is_diurnal else "Mars"
    malefic_contrary = "Mars" if is_diurnal else "Saturn"

    # Count planets in/out of sect
    in_sect_count = sum(1 for p in planet_conditions.values() if p["in_sect"])
    out_sect_count = len(planet_conditions) - in_sect_count

    data = {
        "chart_sect": chart_sect,
        "is_diurnal": is_diurnal,
        "mercury_sect": merc_sect,
        "benefic_of_sect": benefic_of_sect,
        "benefic_contrary": benefic_contrary,
        "malefic_of_sect": malefic_of_sect,
        "malefic_contrary": malefic_contrary,
        "in_sect_count": in_sect_count,
        "out_sect_count": out_sect_count,
        "planet_conditions": planet_conditions,
    }

    return SystemResult(
        id="sect",
        name="Sect (Diurnal/Nocturnal)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Vettius Valens, Anthology — sect, hayz, rejoicing conditions",
            "Ptolemy, Tetrabiblos — diurnal/nocturnal distinction",
        ],
        question="Q1_IDENTITY",
    )
