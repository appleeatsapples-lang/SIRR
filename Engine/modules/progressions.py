"""Secondary Progressions — COMPUTED_STRICT
The most widely used predictive technique in Western astrology.
Each day after birth corresponds to one year of life (day-for-a-year).

For someone aged N years, the progressed chart is cast for birth_JD + N days.
The progressed Moon is the most dynamic body (~12-15° per year = 1 sign
per ~2.5 years). The progressed Sun moves ~1° per year.

Sources: Alan Leo (1902 codification), Placidus de Titis (original formulation)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PLANET_IDS = [
    ("Sun", 0), ("Moon", 1), ("Mercury", 2), ("Venus", 3),
    ("Mars", 4), ("Jupiter", 5), ("Saturn", 6),
]


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


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="progressions",
            name="Secondary Progressions",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    import swisseph as swe
    swe.set_ephe_path(None)

    jd_birth = natal_chart_data["julian_day"]

    # Calculate exact age in years (fractional)
    from datetime import date
    birth = profile.dob
    today = profile.today
    # Fractional year: full years + fraction of current year
    age_years = today.year - birth.year
    # Fraction within the current birthday year
    try:
        birthday_this_year = date(today.year, birth.month, birth.day)
    except ValueError:
        # Leap day edge case
        birthday_this_year = date(today.year, birth.month, birth.day - 1)

    if today < birthday_this_year:
        age_years -= 1
        try:
            birthday_prev = date(today.year - 1, birth.month, birth.day)
        except ValueError:
            birthday_prev = date(today.year - 1, birth.month, birth.day - 1)
        days_since = (today - birthday_prev).days
        year_length = (birthday_this_year - birthday_prev).days
    else:
        days_since = (today - birthday_this_year).days
        try:
            birthday_next = date(today.year + 1, birth.month, birth.day)
        except ValueError:
            birthday_next = date(today.year + 1, birth.month, birth.day - 1)
        year_length = (birthday_next - birthday_this_year).days

    age_fractional = age_years + days_since / year_length

    # Progressed JD = birth JD + age (1 day per year)
    jd_progressed = jd_birth + age_fractional

    # Compute progressed planetary positions
    prog_planets = {}
    for name, pid in PLANET_IDS:
        r = swe.calc_ut(jd_progressed, pid)
        prog_planets[name] = _sign_data(r[0][0])

    # Natal positions for comparison
    natal_sun = natal_chart_data["planets"]["Sun"]
    natal_moon = natal_chart_data["planets"]["Moon"]

    # Progressed Sun advance from natal (degrees moved = ~1°/year)
    sun_advance = (prog_planets["Sun"]["longitude"] - natal_sun["longitude"]) % 360
    if sun_advance > 180:
        sun_advance -= 360

    # Progressed Moon sign changes are the key interpretive factor
    prog_moon_sign = prog_planets["Moon"]["sign"]
    natal_moon_sign = natal_moon["sign"]
    moon_changed_sign = prog_moon_sign != natal_moon_sign

    data = {
        "age": round(age_fractional, 2),
        "progressed_sun_sign": prog_planets["Sun"]["sign"],
        "progressed_moon_sign": prog_moon_sign,
        "natal_moon_sign": natal_moon_sign,
        "moon_sign_changed": moon_changed_sign,
        "sun_advance_degrees": round(sun_advance, 2),
        "planets": prog_planets,
    }

    return SystemResult(
        id="progressions",
        name="Secondary Progressions",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Alan Leo — secondary progressions (day-for-a-year)",
            "Placidus de Titis — original formulation",
            "Swiss Ephemeris",
        ],
        question="Q4_TIMING",
    )
