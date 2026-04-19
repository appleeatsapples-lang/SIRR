"""Firdaria (Persian Planetary Periods) — LOOKUP_FIXED
Day/night birth sequences per Abu Ma'shar, with Chaldean sub-periods.
Sub-period rule: first sub-ruler = major period ruler, then Chaldean order
(Saturn→Jupiter→Mars→Sun→Venus→Mercury→Moon), looping. Nodes have no sub-periods.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def _get_sub_period(major_planet: str, years_into: float, period_length: int,
                    chaldean_order: list, has_sub: bool) -> dict:
    """Compute sub-period ruler within a major period."""
    if not has_sub:
        return {"sub_planet": major_planet, "sub_index": 0, "sub_count": 1}

    # 7 sub-periods per major period
    sub_count = 7
    sub_length = period_length / sub_count

    # Build sub-period sequence: major ruler first, then Chaldean order skipping major
    sub_sequence = [major_planet]
    # Find major's position in Chaldean order, start from next
    if major_planet in chaldean_order:
        idx = chaldean_order.index(major_planet)
        for i in range(1, 7):
            sub_sequence.append(chaldean_order[(idx + i) % 7])
    else:
        # Shouldn't happen for planets, but defensive
        sub_sequence = chaldean_order[:7]

    sub_idx = min(int(years_into / sub_length), sub_count - 1)
    return {"sub_planet": sub_sequence[sub_idx], "sub_index": sub_idx, "sub_count": sub_count}


PLANET_QUALITY = {
    "Sun": "benefic", "Moon": "benefic", "Venus": "benefic", "Jupiter": "benefic",
    "Mercury": "neutral", "Saturn": "malefic", "Mars": "malefic",
    "North Node": "benefic", "South Node": "malefic",
}


def _combined_quality(main_planet: str, sub_planet: str) -> str:
    """Derive period quality from major + sub-period rulers."""
    main_q = PLANET_QUALITY.get(main_planet, "neutral")
    sub_q = PLANET_QUALITY.get(sub_planet, "neutral")
    if main_q == sub_q:
        return main_q
    if "malefic" in (main_q, sub_q):
        return "challenging"
    return "mixed"


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1

    # Determine birth type (day/night)
    is_day = True
    certainty = "LOOKUP_FIXED"
    if profile.birth_time_local:
        try:
            hour = int(profile.birth_time_local.split(":")[0])
            is_day = 6 <= hour < 18
        except (ValueError, IndexError):
            pass
    else:
        # No birth time available — default to day, flag as approximate
        certainty = "APPROX"

    firdaria = constants["firdaria"]
    sequence = firdaria["day_birth_sequence"] if is_day else firdaria["night_birth_sequence"]
    chaldean_order = firdaria["chaldean_order"]

    major = None
    period_start = 0
    period_length = 1
    has_sub = True
    for period in sequence:
        if period["start"] <= age < period["end"]:
            major = period["planet"]
            period_start = period["start"]
            period_length = period["years"]
            has_sub = not period.get("no_sub", False)
            break

    if not major:
        major = "Beyond sequence (75+)"
        period_start = 75
        period_length = 1
        has_sub = False

    years_into = age - period_start
    sub = _get_sub_period(major, years_into, period_length, chaldean_order, has_sub)

    return SystemResult(
        id="firdaria",
        name="Firdaria (Persian Planetary Period)",
        certainty=certainty,
        data={
            "age": age,
            "birth_type": "Day" if is_day else "Night",
            "major_planet": major,
            "period_range": f"{period_start}-{period_start + period_length}",
            "sub_planet": sub["sub_planet"],
            "sub_period_approx": f"year {years_into + 1} of {period_length}",
            "combined": f"{major}/{sub['sub_planet']}",
            "period_quality": _combined_quality(major, sub["sub_planet"]),
        },
        interpretation="Persian timing. Day/night sequences per Abu Ma'shar with Chaldean sub-periods.",
        constants_version=constants["version"],
        references=["Abu Ma'shar, De Revolutionibus Nativitatum", "Bonatti, Liber Astronomiae"],
        question="Q4_TIMING"
    )
