"""Declinations — Parallel & Contraparallel Aspects — COMPUTED_STRICT
Computes each planet's declination (angular distance from the celestial equator)
and detects:
1. Parallel aspects: two planets at the same declination (±1° orb) — acts like conjunction
2. Contraparallel aspects: equal magnitude, opposite sign (±1° orb) — acts like opposition
3. Out-of-bounds planets: declination exceeds the Sun's maximum (~23°26')

Declination is orthogonal to ecliptic longitude and reveals connections invisible
in standard aspect analysis.

Sources: Kt Boehrer (Declination: The Other Dimension),
         Leigh Westin (Beyond the Solstice by Declination)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

OBLIQUITY = 23.4393  # Mean obliquity of ecliptic (J2000, approximate)
PARALLEL_ORB = 1.0
OOB_THRESHOLD = 23.4393

PLANET_IDS = [
    ("Sun", 0), ("Moon", 1), ("Mercury", 2), ("Venus", 3),
    ("Mars", 4), ("Jupiter", 5), ("Saturn", 6),
    ("Uranus", 7), ("Neptune", 8), ("Pluto", 9),
]


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None or not profile.birth_time_local or not profile.timezone or not profile.location:
        return SystemResult(
            id="declinations", name="Declinations (Parallel/Contraparallel)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data and birth time required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    import swisseph as swe
    swe.set_ephe_path(None)

    jd_ut = natal_chart_data.get("julian_day")
    if jd_ut is None:
        return SystemResult(
            id="declinations", name="Declinations (Parallel/Contraparallel)",
            certainty="NEEDS_INPUT",
            data={"error": "julian_day not in natal_chart_data"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    # Compute declinations using equatorial coordinates
    planet_decls = {}
    for name, pid in PLANET_IDS:
        actual_id = pid if pid != 11 else 10
        result = swe.calc_ut(jd_ut, actual_id, swe.FLG_EQUATORIAL)
        decl = result[0][1]  # [RA, Dec, distance, ...]
        planet_decls[name] = round(decl, 4)

    # Out-of-bounds detection
    oob_planets = []
    for name, decl in planet_decls.items():
        if abs(decl) > OOB_THRESHOLD:
            oob_planets.append({
                "planet": name,
                "declination": decl,
                "direction": "north" if decl > 0 else "south",
            })

    # Parallel and contraparallel detection
    parallels = []
    contraparallels = []
    names = list(planet_decls.keys())

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pa, pb = names[i], names[j]
            da, db = planet_decls[pa], planet_decls[pb]

            # Parallel: same sign declination, within orb
            if abs(da - db) <= PARALLEL_ORB:
                parallels.append({
                    "pair": [pa, pb],
                    "declinations": [da, db],
                    "orb": round(abs(da - db), 4),
                })

            # Contraparallel: opposite sign declination, within orb
            if abs(da + db) <= PARALLEL_ORB:
                contraparallels.append({
                    "pair": [pa, pb],
                    "declinations": [da, db],
                    "orb": round(abs(da + db), 4),
                })

    data = {
        "declinations": planet_decls,
        "parallel_count": len(parallels),
        "contraparallel_count": len(contraparallels),
        "parallels": parallels,
        "contraparallels": contraparallels,
        "oob_count": len(oob_planets),
        "oob_planets": oob_planets,
    }

    return SystemResult(
        id="declinations",
        name="Declinations (Parallel/Contraparallel)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Kt Boehrer, Declination: The Other Dimension",
            "Swiss Ephemeris (equatorial coordinates)",
        ],
        question="Q3_NATURE",
    )
