"""Babylonian Nativity Horoscope
Positions planets in the Babylonian sidereal zodiac using the Huber
ayanamsa reconstruction (Spica at 0° Libra calibration).

Input:  natal_chart_data (tropical planet longitudes), profile (DOB, birth_time)
Output: Babylonian sidereal positions with Akkadian sign names, lunar data,
        Babylonian month, and birth watch.

COMPUTED_STRICT when natal_chart_data is present, NEEDS_INPUT otherwise.
"""
from __future__ import annotations
import math
from sirr_core.types import InputProfile, SystemResult

# ── Akkadian zodiac names (12 × 30° sidereal signs) ──
AKKADIAN_SIGNS = [
    ("HUN",       "Aries"),
    ("GU4.AN",    "Taurus"),
    ("MASH.MASH", "Gemini"),
    ("ALLA",      "Cancer"),
    ("UR.A",      "Leo"),
    ("ABSIN",     "Virgo"),
    ("RIN",       "Libra"),
    ("GIR.TAB",   "Scorpio"),
    ("PA",        "Sagittarius"),
    ("MASH",      "Capricorn"),
    ("GU",        "Aquarius"),
    ("ZIB.ME",    "Pisces"),
]

# ── Babylonian planet order (benefic→malefic) ──
PLANET_ORDER = ["Moon", "Sun", "Jupiter", "Venus", "Mercury", "Saturn", "Mars"]

# ── Babylonian months (Nisannu = 1, anchored to spring equinox) ──
BABYLONIAN_MONTHS = [
    "Nisannu",   "Ayaru",     "Simanu",   "Du'uzu",
    "Abu",       "Ululu",     "Tashritu",  "Arahsamna",
    "Kislimu",   "Tebetu",    "Shabatu",   "Addaru",
]

# ── Night watches (3 watches × ~4 hours each, sunset ~18:00 local) ──
WATCHES = [
    (18, 22, "First Watch (evening)"),
    (22, 2,  "Middle Watch (midnight)"),
    (2,  6,  "Third Watch (morning)"),
]

# New Moon epoch for synodic calculation (same as maramataka.py)
NEW_MOON_EPOCH_JD = 2451550.26   # 2000-Jan-06 18:14 UTC
SYNODIC_PERIOD = 29.53059

# Known timezone offsets
TZ_OFFSETS = {
    "Asia/Riyadh": 3, "Asia/Dubai": 4, "Asia/Kuwait": 3,
    "Asia/Amman": 2, "Africa/Cairo": 2, "Asia/Beirut": 2,
    "Asia/Damascus": 2, "Asia/Baghdad": 3, "Europe/Istanbul": 3,
    "Europe/London": 0, "America/New_York": -5, "UTC": 0,
}


def _huber_ayanamsa(year: int) -> float:
    """Huber reconstruction: Spica at 0° Libra calibration.

    ayanamsa ≈ 24.0 - (2000 - year) × 0.01388
    Precession rate ~50.26 arcsec/year ≈ 0.01396°/year.
    """
    return 24.0 - (2000 - year) * 0.01388


def _to_sidereal(tropical_lon: float, ayanamsa: float) -> float:
    """Convert tropical longitude to Babylonian sidereal."""
    return (tropical_lon - ayanamsa) % 360.0


def _sign_from_longitude(sidereal_lon: float):
    """Return (sign_index, degree_in_sign) from sidereal longitude."""
    idx = int(sidereal_lon // 30) % 12
    deg = sidereal_lon % 30
    return idx, deg


def _compute_lunar_day(jd: float) -> int:
    """Lunar day 1-30 from synodic month."""
    phase = (jd - NEW_MOON_EPOCH_JD) % SYNODIC_PERIOD
    day = int(phase / SYNODIC_PERIOD * 30) + 1
    return min(day, 30)


def _month_length(lunar_day_phase: float) -> int:
    """Babylonian months alternate 29/30 days; approximate from phase."""
    cycle_num = int((lunar_day_phase - NEW_MOON_EPOCH_JD) / SYNODIC_PERIOD)
    return 30 if cycle_num % 2 == 0 else 29


def _babylonian_month(dob_month: int, dob_day: int) -> str:
    """Map Gregorian date to approximate Babylonian month.

    Nisannu starts near spring equinox (~March 21).
    Offset: March→Nisannu, April→Ayaru, etc.
    """
    # Month index: March=0 (Nisannu) through February=11 (Addaru)
    idx = (dob_month - 3) % 12
    return BABYLONIAN_MONTHS[idx]


def _birth_watch(hour: int) -> str:
    """Determine which of the 3 Babylonian night watches the birth falls in.

    Daytime births return 'Daytime (no watch)'.
    """
    if 6 <= hour < 18:
        return "Daytime (no watch)"
    # First watch: 18-22
    if 18 <= hour < 22:
        return WATCHES[0][2]
    # Middle watch: 22-02
    if hour >= 22 or hour < 2:
        return WATCHES[1][2]
    # Third watch: 02-06
    return WATCHES[2][2]


def _lunar_latitude_approx(jd: float) -> float:
    """Approximate lunar latitude from nodal cycle.

    The Moon's nodal period is ~27.2122 days (draconic month).
    Max latitude ±5.15°. Simple sinusoidal approximation.
    """
    DRACONIC_PERIOD = 27.21222
    # Use a known node-crossing epoch (ascending node)
    NODE_EPOCH_JD = 2451565.0  # ~Jan 21 2000 (approximate ascending node)
    phase = ((jd - NODE_EPOCH_JD) / DRACONIC_PERIOD) * 2 * math.pi
    return round(5.15 * math.sin(phase), 2)


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal_data = kwargs.get("natal_chart_data")

    if not natal_data or not profile.birth_time_local:
        return SystemResult(
            id="babylonian_horoscope",
            name="Babylonian Nativity Horoscope",
            certainty="NEEDS_INPUT",
            data={"error": "Requires natal_chart_data and birth_time_local"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    planets_data = natal_data.get("planets", {})
    year = profile.dob.year
    ayanamsa = round(_huber_ayanamsa(year), 4)

    # ── Convert each planet to Babylonian sidereal ──
    babylonian_positions = {}
    for planet_name in PLANET_ORDER:
        pdata = planets_data.get(planet_name)
        if not pdata:
            continue
        trop_lon = pdata["longitude"]
        sid_lon = round(_to_sidereal(trop_lon, ayanamsa), 4)
        sign_idx, deg_in_sign = _sign_from_longitude(sid_lon)
        akkadian, english = AKKADIAN_SIGNS[sign_idx]
        babylonian_positions[planet_name] = {
            "akkadian_sign": akkadian,
            "english_sign": english,
            "degree_in_sign": round(deg_in_sign, 2),
            "longitude_sidereal": sid_lon,
        }

    # ── Lunar data ──
    h, m = map(int, profile.birth_time_local.split(":"))
    tz_offset = TZ_OFFSETS.get(profile.timezone, 3)
    ut = (h + m / 60.0) - tz_offset

    import swisseph as swe
    swe.set_ephe_path(None)
    jd = swe.julday(profile.dob.year, profile.dob.month, profile.dob.day, ut)

    lunar_day = _compute_lunar_day(jd)
    month_len = _month_length(jd)
    lunar_lat = _lunar_latitude_approx(jd)

    # ── Babylonian month and birth watch ──
    bab_month = _babylonian_month(profile.dob.month, profile.dob.day)
    watch = _birth_watch(h)

    data = {
        "method": "Huber sidereal reconstruction (Spica = 0° RIN)",
        "babylonian_ayanamsa": ayanamsa,
        "babylonian_positions": babylonian_positions,
        "planet_order": PLANET_ORDER,
        "lunar_day": lunar_day,
        "babylonian_month": bab_month,
        "month_length": month_len,
        "lunar_latitude": lunar_lat,
        "birth_watch": watch,
    }

    return SystemResult(
        id="babylonian_horoscope",
        name="Babylonian Nativity Horoscope",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Huber, P. (1958) — Babylonian ayanamsa reconstruction",
            "MUL.APIN tablet series — Akkadian zodiac sign names",
            "Hunger & Pingree (1999) — Astral Sciences in Mesopotamia",
        ],
        question="Q1_IDENTITY",
    )
