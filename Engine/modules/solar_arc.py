"""Solar Arc Directions — COMPUTED_STRICT
The solar arc equals the distance the progressed Sun has traveled from its natal
position. This arc is then added to ALL natal positions uniformly, producing
directed positions for each planet and angle.

Solar Arc = Progressed_Sun - Natal_Sun
Directed_Planet = Natal_Planet + Solar_Arc

The progressed Sun is computed using the day-for-a-year method:
  JD_progressed = JD_birth + age_in_years (in days)

When a directed planet aspects a natal position (conjunction within 1° orb),
it represents a major life activation at that age.

Sources: Noel Tyl (Solar Arcs: Astrology's Most Successful Predictive System),
         Charles E.O. Carter (Symbolic Directions in Modern Astrology)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

DIRECTION_ORB = 1.0  # degrees


def _angular_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None or not profile.birth_time_local:
        return SystemResult(
            id="solar_arc", name="Solar Arc Directions",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data and birth time required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q4_TIMING",
        )

    import swisseph as swe
    swe.set_ephe_path(None)

    jd_ut = natal_chart_data.get("julian_day")
    if jd_ut is None:
        return SystemResult(
            id="solar_arc", name="Solar Arc Directions",
            certainty="NEEDS_INPUT",
            data={"error": "julian_day not in natal_chart_data"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q4_TIMING",
        )

    planets = natal_chart_data.get("planets", {})
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    mc_lon = natal_chart_data["midheaven"]["longitude"]
    natal_sun = planets["Sun"]["longitude"]

    # Compute age in fractional years
    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1
    age_frac = age + (profile.today.month - profile.dob.month) / 12.0

    # Progressed Sun: birth JD + age (in days, day-for-year)
    jd_progressed = jd_ut + age_frac
    prog_sun_result = swe.calc_ut(jd_progressed, 0)  # Sun = 0
    prog_sun_lon = prog_sun_result[0][0]

    solar_arc = (prog_sun_lon - natal_sun) % 360
    if solar_arc > 180:
        solar_arc -= 360  # Keep arc reasonable

    # Apply arc to all natal positions
    directed = {}
    for name, pdata in planets.items():
        d_lon = (pdata["longitude"] + solar_arc) % 360
        sign_idx = int(d_lon // 30) % 12
        directed[name] = {
            "natal": round(pdata["longitude"], 2),
            "directed": round(d_lon, 2),
            "sign": SIGNS[sign_idx],
        }

    # Directed angles
    d_asc = (asc_lon + solar_arc) % 360
    d_mc = (mc_lon + solar_arc) % 360
    directed["ASC"] = {"natal": round(asc_lon, 2), "directed": round(d_asc, 2), "sign": SIGNS[int(d_asc // 30) % 12]}
    directed["MC"] = {"natal": round(mc_lon, 2), "directed": round(d_mc, 2), "sign": SIGNS[int(d_mc // 30) % 12]}

    # Find contacts: directed position conjunct natal position (diff planets)
    contacts = []
    natal_points = {}
    for name, pdata in planets.items():
        natal_points[name] = pdata["longitude"]
    natal_points["ASC"] = asc_lon
    natal_points["MC"] = mc_lon

    for d_name, d_data in directed.items():
        d_lon = d_data["directed"]
        for n_name, n_lon in natal_points.items():
            if d_name == n_name:
                continue
            orb = _angular_diff(d_lon, n_lon)
            if orb <= DIRECTION_ORB:
                contacts.append({
                    "directed": d_name,
                    "natal": n_name,
                    "orb": round(orb, 4),
                    "type": "conjunction",
                })

    contacts.sort(key=lambda x: x["orb"])

    data = {
        "solar_arc": round(solar_arc, 4),
        "age_years": round(age_frac, 1),
        "contact_count": len(contacts),
        "contacts": contacts[:15],
        "directed_positions": directed,
    }

    return SystemResult(
        id="solar_arc",
        name="Solar Arc Directions",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Noel Tyl, Solar Arcs: Astrology's Most Successful Predictive System",
            "Swiss Ephemeris (progressed Sun computation)",
        ],
        question="Q4_TIMING",
    )
