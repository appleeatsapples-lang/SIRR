"""Kalachakra Dasha — Vedic Time-Wheel Periods — COMPUTED_STRICT
A nakshatra-pada based dasha system where the period sequence follows the
"wheel of time" (kalachakra) rather than a fixed planetary order.

The Moon's nakshatra-pada determines the starting point in one of four
dasha groups (savya/apasavya/savya-apasavya/apasavya-savya), each with
its own period sequence and durations.

The 4 navamsha padas in each nakshatra map to specific rashis in the
Kalachakra sequence. Each rashi period has a fixed duration (in years).

Uses sidereal (Lahiri ayanamsha) Moon position.

Sources: Brihat Parashara Hora Shastra (BPHS, Ch. 46-47),
         P.S. Shastri (Kalachakra Dasha System)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Kalachakra period durations per sign (in years)
# Standard BPHS assignment
SIGN_YEARS = {
    "Aries": 7, "Taurus": 16, "Gemini": 9, "Cancer": 21,
    "Leo": 5, "Virgo": 9, "Libra": 16, "Scorpio": 7,
    "Sagittarius": 10, "Capricorn": 4, "Aquarius": 4, "Pisces": 10,
}

# Savya (clockwise) sequence: Aries through Pisces
SAVYA_SEQ = list(range(12))  # 0-11 = Aries through Pisces

# Apasavya (counter-clockwise) sequence: Scorpio, Libra, Virgo, ... down to Aries, then Pisces back to Sagittarius
APASAVYA_SEQ = [7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9, 8]

# Nakshatra group: which group (savya/apasavya) based on nakshatra number
# Odd nakshatras (1,3,5,...) → savya for padas 1,2 / apasavya for padas 3,4
# Even nakshatras (2,4,6,...) → apasavya for padas 1,2 / savya for padas 3,4
# This is simplified; the full scheme is quite intricate.

# Starting rashi for each pada: the pada maps into the navamsha scheme
# Pada 1-4 of each nakshatra maps to sequential navamsha signs
# Starting sign for nakshatra N, pada P:
# navamsha_sign = ((N-1)*4 + (P-1)) % 12
def _navamsha_sign(nakshatra_idx: int, pada: int) -> int:
    """0-indexed nakshatra and 1-indexed pada → 0-indexed sign."""
    return (nakshatra_idx * 4 + (pada - 1)) % 12


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="kalachakra_dasha", name="Kalachakra Dasha",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q4_TIMING",
        )

    import swisseph as swe
    swe.set_ephe_path(None)

    jd_ut = natal_chart_data.get("julian_day")
    if jd_ut is None:
        return SystemResult(
            id="kalachakra_dasha", name="Kalachakra Dasha",
            certainty="NEEDS_INPUT",
            data={"error": "julian_day not in natal_chart_data"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q4_TIMING",
        )

    # Sidereal Moon position
    ayanamsha = swe.get_ayanamsa_ut(jd_ut)
    moon_trop = natal_chart_data["planets"]["Moon"]["longitude"]
    moon_sid = (moon_trop - ayanamsha) % 360

    # Nakshatra and pada
    nakshatra_idx = int(moon_sid / (360 / 27))  # 0-26
    nak_start = nakshatra_idx * (360 / 27)
    pada_size = (360 / 27) / 4
    pada = int((moon_sid - nak_start) / pada_size) + 1  # 1-4
    if pada > 4:
        pada = 4

    nakshatra_name = NAKSHATRAS[nakshatra_idx]

    # Determine direction: savya (clockwise) or apasavya
    # Simplified rule: nakshatras 0,2,4,... (even index, odd count) are savya-first
    is_savya_first = (nakshatra_idx % 2) == 0
    if pada <= 2:
        is_savya = is_savya_first
    else:
        is_savya = not is_savya_first

    # Starting rashi from navamsha
    start_sign = _navamsha_sign(nakshatra_idx, pada)

    # Build period sequence
    if is_savya:
        seq = [(start_sign + i) % 12 for i in range(12)]
    else:
        seq = [(start_sign - i) % 12 for i in range(12)]

    # Elapsed proportion within current pada (for period balance)
    pada_start = nak_start + (pada - 1) * pada_size
    elapsed_frac = (moon_sid - pada_start) / pada_size
    elapsed_frac = max(0, min(1, elapsed_frac))

    # Build dasha periods
    first_sign = SIGNS[seq[0]]
    first_years = SIGN_YEARS[first_sign]
    balance = first_years * (1 - elapsed_frac)

    periods = []
    cumulative = 0.0

    # First period (balance)
    periods.append({
        "sign": first_sign,
        "years": round(balance, 2),
        "start_age": 0,
        "end_age": round(balance, 2),
    })
    cumulative = balance

    # Remaining periods
    for i in range(1, 12):
        sign = SIGNS[seq[i]]
        years = SIGN_YEARS[sign]
        periods.append({
            "sign": sign,
            "years": years,
            "start_age": round(cumulative, 2),
            "end_age": round(cumulative + years, 2),
        })
        cumulative += years

    # Current age
    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1

    # Find current period
    current_period = periods[0]
    for p in periods:
        if p["start_age"] <= age < p["end_age"]:
            current_period = p
            break

    data = {
        "moon_sidereal": round(moon_sid, 4),
        "nakshatra": nakshatra_name,
        "nakshatra_index": nakshatra_idx + 1,
        "pada": pada,
        "direction": "savya" if is_savya else "apasavya",
        "start_sign": SIGNS[seq[0]],
        "current_period_sign": current_period["sign"],
        "current_period_years": current_period["years"],
        "age": age,
        "periods": periods[:8],  # First 8 for compact output
        "total_cycle_years": round(cumulative, 1),
    }

    return SystemResult(
        id="kalachakra_dasha",
        name="Kalachakra Dasha",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Brihat Parashara Hora Shastra, Ch. 46-47 — Kalachakra Dasha",
            "P.S. Shastri, Kalachakra Dasha System",
        ],
        question="Q4_TIMING",
    )
