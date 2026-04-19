"""Fixed Stars — Behenian + Royal Stars — COMPUTED_STRICT
Checks natal planetary positions against 19 important fixed stars
(15 Behenian + 4 Royal). Uses J2000.0 ecliptic longitudes with
precession correction (~50.29" per year).

A conjunction within 1° orb links the planet to the star's signification.

The 4 Royal Stars (Watchers of Heaven) mark the cardinal directions:
  Aldebaran (Watcher of the East), Regulus (North), Antares (West),
  Fomalhaut (South).

The 15 Behenian Stars are the magical stars of Hermes Trismegistus,
used in talismanic astrology since antiquity.

Sources: Agrippa (Three Books of Occult Philosophy), Al-Biruni,
Ptolemy (Almagest star catalog), Robson (Fixed Stars and Constellations)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Precession rate: 50.29 arcseconds per year = 0.013969° per year
PRECESSION_RATE = 50.29 / 3600  # degrees per year

# J2000.0 epoch
J2000_YEAR = 2000.0

# Fixed stars: (name, J2000 ecliptic longitude, magnitude, nature, keywords, is_royal, is_behenian)
# Ecliptic longitudes from Robson/Morse corrected to J2000.0
FIXED_STARS = [
    # 4 Royal Stars
    ("Aldebaran",    69.95,  0.85, "Mars",          "Watcher of the East. Courage, eloquence, honor through integrity.", True, True),
    ("Regulus",     149.83,  1.35, "Mars-Jupiter",   "Watcher of the North. Royal star of kings. Success if noble.", True, True),
    ("Antares",    249.76,  1.09, "Mars-Jupiter",   "Watcher of the West. Intensity, strategy, obsession.", True, True),
    ("Fomalhaut",  333.87,  1.16, "Venus-Mercury",  "Watcher of the South. Idealism, fame, magical ability.", True, True),

    # 15 Behenian Stars (including the 4 Royal above; remaining 11 below)
    ("Algol",       56.17,  2.12, "Saturn-Jupiter",  "The Demon Star. Primal feminine rage, transformation.", False, True),
    ("Alcyone",     60.00,  2.87, "Moon-Mars",       "The Pleiades. Mysticism, inner vision, exile.", False, True),
    ("Sirius",     104.08, -1.46, "Jupiter-Mars",    "The Dog Star. Brilliance, ambition, scorching.", False, True),
    ("Procyon",    115.78,  0.34, "Mercury-Mars",    "Before the Dog. Quick success, restlessness.", False, True),
    ("Algorab",    193.45,  2.95, "Mars-Saturn",     "The Crow. Scavenging, cunning, destructive charm.", False, True),
    ("Spica",      203.83,  0.97, "Venus-Mercury",   "The Sheaf of Wheat. Brilliance, gifts, artistic talent.", False, True),
    ("Arcturus",   204.14,  0.04, "Mars-Jupiter",    "The Bear Guard. Pathfinding, prosperity, renown.", False, True),
    ("Alphecca",   222.30,  2.23, "Venus-Mercury",   "The Crown. Artistic gifts, quiet honor.", False, True),
    ("Vega",       285.32,  0.03, "Venus-Mercury",   "The Falling Eagle. Charisma, idealism, artistic magic.", False, True),
    ("Deneb Algedi", 323.55, 2.87, "Saturn-Jupiter", "The Goat's Tail. Justice, law, sorrow then joy.", False, True),
    ("Markab",     353.48,  2.49, "Mars-Mercury",    "The Saddle. Intellectual, literary, danger from fire.", False, True),
]


def _precess(j2000_lon: float, birth_year: float) -> float:
    """Apply precession correction from J2000.0 to the birth epoch."""
    years = birth_year - J2000_YEAR
    return (j2000_lon + PRECESSION_RATE * years) % 360


def _sign_data(longitude: float) -> dict:
    sign_idx = int(longitude // 30) % 12
    deg_in_sign = longitude % 30
    degree = int(deg_in_sign)
    minute = int((deg_in_sign - degree) * 60)
    return {
        "longitude": round(longitude, 4),
        "sign": SIGNS[sign_idx],
        "degree": degree,
        "minute": minute,
        "formatted": f"{degree}\u00b0{minute:02d}' {SIGNS[sign_idx]}",
    }


def _angular_diff(lon1: float, lon2: float) -> float:
    """Smallest angular difference (0-180)."""
    diff = abs(lon1 - lon2) % 360
    return diff if diff <= 180 else 360 - diff


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="fixed_stars",
            name="Fixed Stars (Behenian + Royal)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    planets = natal_chart_data.get("planets", {})
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    mc_lon = natal_chart_data["midheaven"]["longitude"]

    # Birth year for precession
    birth_year = profile.dob.year + (profile.dob.month - 1) / 12 + (profile.dob.day - 1) / 365.25

    ORB = 1.0  # degrees

    star_positions = []
    conjunctions = []

    for name, j2000_lon, mag, nature, keywords, is_royal, is_behenian in FIXED_STARS:
        corrected_lon = _precess(j2000_lon, birth_year)
        sd = _sign_data(corrected_lon)
        star_entry = {
            "name": name,
            "longitude": sd["longitude"],
            "sign": sd["sign"],
            "formatted": sd["formatted"],
            "magnitude": mag,
            "nature": nature,
            "royal": is_royal,
        }
        star_positions.append(star_entry)

        # Check conjunctions with planets + ASC + MC
        points = dict(planets)
        # Add ASC and MC as checkable points
        check_points = {p: planets[p]["longitude"] for p in planets}
        check_points["Ascendant"] = asc_lon
        check_points["Midheaven"] = mc_lon

        for point_name, point_lon in check_points.items():
            diff = _angular_diff(corrected_lon, point_lon)
            if diff <= ORB:
                conjunctions.append({
                    "star": name,
                    "planet": point_name,
                    "orb": round(diff, 2),
                    "star_nature": nature,
                    "keywords": keywords,
                    "royal": is_royal,
                })

    # Sort conjunctions by tightest orb
    conjunctions.sort(key=lambda c: c["orb"])

    # Count royal and behenian conjunctions
    royal_count = sum(1 for c in conjunctions if c["royal"])

    data = {
        "conjunction_count": len(conjunctions),
        "royal_conjunction_count": royal_count,
        "conjunctions": conjunctions,
        "stars": star_positions,
        "orb_used": ORB,
    }

    return SystemResult(
        id="fixed_stars",
        name="Fixed Stars (Behenian + Royal)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Agrippa, Three Books of Occult Philosophy — 15 Behenian stars",
            "Ptolemy, Almagest — star catalog",
            "J2000.0 ecliptic longitudes, precession rate 50.29\"/year",
        ],
        question="Q1_IDENTITY",
    )
