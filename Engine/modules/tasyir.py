"""Tasyir — Islamic Primary Directions — COMPUTED_STRICT
The tasyir (Arabic: تسيير, "directing") is the Islamic tradition's primary
directional technique, where each degree of the equator passing over the
meridian equals one year of life.

Al-Biruni's method:
  1. Identify the hyleg (giver of life): usually the Sun (day) or Moon (night)
  2. Direct the hyleg along the equator at 1°/year
  3. When the directed hyleg reaches the degree of a natal planet or angle,
     that planet's nature activates at that age

This module uses the simpler "degree = year" equatorial arc:
  Directed_position = Natal_position + (age × 1°)
Then checks for conjunctions with natal planets/angles.

Sources: Al-Biruni (The Book of Instruction in the Elements of the Art of Astrology),
         Abu Ma'shar (Introduction to Astrology)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

DIRECTION_ORB = 1.0  # Standard orb for primary directions


def _angular_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="tasyir", name="Tasyir (Islamic Primary Directions)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q4_TIMING",
        )

    planets = natal_chart_data.get("planets", {})
    asc_lon = natal_chart_data["ascendant"]["longitude"]
    mc_lon = natal_chart_data["midheaven"]["longitude"]
    sun_lon = planets["Sun"]["longitude"]
    desc_lon = (asc_lon + 180) % 360
    is_diurnal = ((sun_lon - desc_lon) % 360) < 180

    # Select hyleg: Sun for day charts, Moon for night charts
    hyleg = "Sun" if is_diurnal else "Moon"
    hyleg_lon = planets[hyleg]["longitude"]

    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1

    # Direct the hyleg: 1° per year
    directed_lon = (hyleg_lon + age) % 360
    directed_sign_idx = int(directed_lon // 30) % 12

    # Collect all natal significators
    significators = {}
    for name, pdata in planets.items():
        significators[name] = pdata["longitude"]
    significators["ASC"] = asc_lon
    significators["MC"] = mc_lon
    significators["DESC"] = (asc_lon + 180) % 360
    significators["IC"] = (mc_lon + 180) % 360

    # Find current contacts (hyleg directed to natal positions)
    current_contacts = []
    for sig_name, sig_lon in significators.items():
        if sig_name == hyleg:
            continue
        orb = _angular_diff(directed_lon, sig_lon)
        if orb <= DIRECTION_ORB:
            current_contacts.append({
                "significator": sig_name,
                "orb": round(orb, 4),
                "type": "conjunction",
            })

    # Future directions: when will hyleg hit each significator?
    future_hits = []
    for sig_name, sig_lon in significators.items():
        if sig_name == hyleg:
            continue
        # Age at which directed hyleg = significator
        arc = (sig_lon - hyleg_lon) % 360
        hit_age = round(arc, 1)
        if hit_age > age and hit_age < 100:  # Future hits within reasonable lifespan
            future_hits.append({
                "significator": sig_name,
                "age": hit_age,
                "sign": SIGNS[int(sig_lon // 30) % 12],
            })

    # Past hits (already activated)
    past_hits = []
    for sig_name, sig_lon in significators.items():
        if sig_name == hyleg:
            continue
        arc = (sig_lon - hyleg_lon) % 360
        hit_age = round(arc, 1)
        if hit_age <= age and hit_age > 0:
            past_hits.append({
                "significator": sig_name,
                "age": hit_age,
            })

    past_hits.sort(key=lambda x: x["age"])
    future_hits.sort(key=lambda x: x["age"])

    data = {
        "hyleg": hyleg,
        "hyleg_longitude": round(hyleg_lon, 2),
        "directed_longitude": round(directed_lon, 2),
        "directed_sign": SIGNS[directed_sign_idx],
        "age": age,
        "is_diurnal": is_diurnal,
        "current_contact_count": len(current_contacts),
        "current_contacts": current_contacts,
        "past_hits": past_hits[:10],
        "future_hits": future_hits[:5],
    }

    return SystemResult(
        id="tasyir",
        name="Tasyir (Islamic Primary Directions)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Al-Biruni, The Book of Instruction — tasyir method",
            "Abu Ma'shar, Introduction to Astrology — directional technique",
        ],
        question="Q4_TIMING",
    )
