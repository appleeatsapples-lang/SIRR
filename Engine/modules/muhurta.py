"""Muhurta — Vedic Auspicious Timing — COMPUTED_STRICT
Computes the 30 muhurta divisions of the day (sunrise to sunrise),
Abhijit muhurta, Rahu Kalam, Gulika Kalam, and Yamagandam for the
profile's today date at the profile's birth location.

Each muhurta is approximately 48 minutes (daytime muhurtas are longer
in summer, shorter in winter, as they divide actual daylight).

Sources: Muhurta Chintamani, Brihat Samhita (Varahamihira),
         Phaladeepika (Mantreswara)
"""
from __future__ import annotations
from datetime import date
from sirr_core.types import InputProfile, SystemResult

# 30 muhurta names (from sunrise, 15 day + 15 night)
MUHURTA_NAMES = [
    "Rudra", "Ahi", "Mitra", "Pitru", "Vasu",
    "Vara", "Vishwedeva", "Vidhi", "Satamukhi", "Puruhuta",
    "Vahini", "Naktanakara", "Varuna", "Aryaman", "Bhaga",
    # Night muhurtas (15-29)
    "Girisha", "Ajapada", "Ahirbudhnya", "Pushya", "Ashvini",
    "Yama", "Agni", "Vidhatr", "Kanda", "Aditi",
    "Jiva", "Vishnu", "Dyumadgadyuti", "Brahma", "Samudram",
]

# Quality ratings
MUHURTA_QUALITY = {
    "Rudra": "inauspicious",
    "Ahi": "inauspicious",
    "Mitra": "auspicious",
    "Pitru": "neutral",
    "Vasu": "auspicious",
    "Vara": "auspicious",
    "Vishwedeva": "auspicious",
    "Vidhi": "neutral",
    "Satamukhi": "neutral",
    "Puruhuta": "neutral",
    "Vahini": "neutral",
    "Naktanakara": "inauspicious",
    "Varuna": "auspicious",
    "Aryaman": "auspicious",
    "Bhaga": "auspicious",
    "Girisha": "neutral",
    "Ajapada": "neutral",
    "Ahirbudhnya": "neutral",
    "Pushya": "auspicious",
    "Ashvini": "auspicious",
    "Yama": "inauspicious",
    "Agni": "neutral",
    "Vidhatr": "neutral",
    "Kanda": "inauspicious",
    "Aditi": "auspicious",
    "Jiva": "excellent",
    "Vishnu": "excellent",
    "Dyumadgadyuti": "auspicious",
    "Brahma": "excellent",
    "Samudram": "neutral",
}

# What each auspicious muhurta is good for
MUHURTA_GOOD_FOR = {
    "Mitra": "partnerships, agreements, friendship",
    "Vasu": "wealth, acquisitions, foundation laying",
    "Vara": "general auspiciousness, ceremonies",
    "Vishwedeva": "religious ceremonies, worship",
    "Varuna": "water-related, travel, purification",
    "Aryaman": "marriage, relationships, alliances",
    "Bhaga": "prosperity, fortune, celebrations",
    "Pushya": "nourishment, healing, charity",
    "Ashvini": "medicine, healing, journeys",
    "Aditi": "beginning new ventures, freedom",
    "Jiva": "all auspicious activities, life-giving",
    "Vishnu": "preservation, protection, all good works",
    "Dyumadgadyuti": "learning, teaching, intellectual work",
    "Brahma": "creation, sacred rituals, highest endeavors",
}

# Day rulers (0=Monday)
DAY_RULERS = {
    0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
    4: "Venus", 5: "Saturn", 6: "Sun",
}

# Rahu Kalam: ordinal position of the 1.5-hour period from sunrise
# (0-indexed: 0 = first 1.5hr, 1 = second, etc.)
RAHU_KALAM_SLOT = {
    0: 1,  # Monday: 2nd slot
    1: 6,  # Tuesday: 7th slot
    2: 4,  # Wednesday: 5th slot
    3: 5,  # Thursday: 6th slot
    4: 3,  # Friday: 4th slot
    5: 2,  # Saturday: 3rd slot
    6: 7,  # Sunday: 8th slot (last)
}

# Gulika Kalam: ordinal slot from sunrise
GULIKA_KALAM_SLOT = {
    0: 5,  # Monday: 6th slot
    1: 4,  # Tuesday: 5th slot
    2: 3,  # Wednesday: 4th slot
    3: 2,  # Thursday: 3rd slot
    4: 1,  # Friday: 2nd slot
    5: 0,  # Saturday: 1st slot
    6: 6,  # Sunday: 7th slot
}

# Yamagandam: ordinal slot from sunrise
YAMAGANDAM_SLOT = {
    0: 3,  # Monday: 4th slot
    1: 2,  # Tuesday: 3rd slot
    2: 1,  # Wednesday: 2nd slot
    3: 0,  # Thursday: 1st slot
    4: 6,  # Friday: 7th slot
    5: 5,  # Saturday: 6th slot
    6: 4,  # Sunday: 5th slot
}


def _get_sunrise_sunset(d: date, lat: float, lon: float, tz_offset: float):
    """Compute sunrise and sunset using pyswisseph."""
    import swisseph as swe
    swe.set_ephe_path(None)

    jd = swe.julday(d.year, d.month, d.day, 0.0)

    # Sunrise
    _, rise = swe.rise_trans(jd, swe.SUN, swe.CALC_RISE, (lon, lat, 0.0))
    rise_jd = rise[0]

    # Sunset
    _, sett = swe.rise_trans(jd, swe.SUN, swe.CALC_SET, (lon, lat, 0.0))
    set_jd = sett[0]

    # Convert to local hours
    _, _, _, rise_h = swe.revjul(rise_jd)
    _, _, _, set_h = swe.revjul(set_jd)

    rise_local = rise_h + tz_offset
    set_local = set_h + tz_offset

    return rise_local, set_local


def _hours_to_time_str(h: float) -> str:
    """Convert decimal hours to HH:MM string."""
    if h < 0:
        h += 24
    if h >= 24:
        h -= 24
    hr = int(h)
    mn = int((h - hr) * 60)
    return f"{hr:02d}:{mn:02d}"


def _compute_kalam_period(sunrise_h: float, day_duration_h: float,
                           slot: int) -> tuple:
    """Compute start/end of a kalam period (each is 1/8 of day duration)."""
    slot_duration = day_duration_h / 8.0
    start = sunrise_h + slot * slot_duration
    end = start + slot_duration
    return start, end


def compute(profile: InputProfile, constants: dict,
            natal_chart_data: dict = None, **kwargs) -> SystemResult:
    today = profile.today
    location = profile.location or "Cairo, Egypt"

    # Get coordinates
    lat, lon = 26.2361, 50.0393  # Cairo default
    tz_offset = 3.0  # Asia/Riyadh

    if getattr(profile, 'latitude', None) is not None:
        lat = profile.latitude
        lon = profile.longitude
        tz_offset = getattr(profile, 'utc_offset', None) or 3.0
    else:
        try:
            from modules.natal_chart import LOCATIONS, TZ_OFFSETS
            coords = LOCATIONS.get(location)
            if coords:
                lat, lon = coords
            tz_offset = TZ_OFFSETS.get(profile.timezone, 3.0)
        except ImportError:
            pass

    # Compute sunrise/sunset
    sunrise_h, sunset_h = _get_sunrise_sunset(today, lat, lon, tz_offset)
    day_duration = sunset_h - sunrise_h
    night_duration = 24.0 - day_duration

    # Day muhurta duration (15 muhurtas in daytime)
    day_muhurta_dur = day_duration / 15.0
    # Night muhurta duration (15 muhurtas in nighttime)
    night_muhurta_dur = night_duration / 15.0

    # Day of week
    dow = today.weekday()  # 0=Monday
    day_ruler = DAY_RULERS[dow]

    # Compute all 30 muhurtas with start/end times
    muhurtas = []
    for i in range(30):
        name = MUHURTA_NAMES[i]
        quality = MUHURTA_QUALITY.get(name, "neutral")
        good_for = MUHURTA_GOOD_FOR.get(name, "")

        if i < 15:
            # Day muhurta
            start_h = sunrise_h + i * day_muhurta_dur
            end_h = start_h + day_muhurta_dur
        else:
            # Night muhurta
            night_idx = i - 15
            start_h = sunset_h + night_idx * night_muhurta_dur
            end_h = start_h + night_muhurta_dur

        muhurtas.append({
            "name": name,
            "start": _hours_to_time_str(start_h),
            "end": _hours_to_time_str(end_h),
            "quality": quality,
            "good_for": good_for,
        })

    # Current muhurta (at noon local = approximate "now" for daily report)
    noon = 12.0
    current_idx = 0
    if noon >= sunrise_h and noon < sunset_h:
        current_idx = int((noon - sunrise_h) / day_muhurta_dur)
        current_idx = min(current_idx, 14)
    elif noon >= sunset_h:
        current_idx = 15 + int((noon - sunset_h) / night_muhurta_dur)
        current_idx = min(current_idx, 29)
    current_muhurta = {
        "name": muhurtas[current_idx]["name"],
        "quality": muhurtas[current_idx]["quality"],
    }

    # Abhijit muhurta (midday, centered on local noon)
    # Traditionally: the 8th muhurta of 15 daytime muhurtas
    abhijit_start = sunrise_h + 7 * day_muhurta_dur
    abhijit_end = abhijit_start + day_muhurta_dur
    abhijit_muhurta = {
        "start": _hours_to_time_str(abhijit_start),
        "end": _hours_to_time_str(abhijit_end),
    }

    # Rahu Kalam
    rahu_slot = RAHU_KALAM_SLOT[dow]
    rahu_start, rahu_end = _compute_kalam_period(
        sunrise_h, day_duration, rahu_slot)
    rahu_kalam = {
        "start": _hours_to_time_str(rahu_start),
        "end": _hours_to_time_str(rahu_end),
    }

    # Gulika Kalam
    gulika_slot = GULIKA_KALAM_SLOT[dow]
    gulika_start, gulika_end = _compute_kalam_period(
        sunrise_h, day_duration, gulika_slot)
    gulika_kalam = {
        "start": _hours_to_time_str(gulika_start),
        "end": _hours_to_time_str(gulika_end),
    }

    # Yamagandam
    yama_slot = YAMAGANDAM_SLOT[dow]
    yama_start, yama_end = _compute_kalam_period(
        sunrise_h, day_duration, yama_slot)
    yamagandam = {
        "start": _hours_to_time_str(yama_start),
        "end": _hours_to_time_str(yama_end),
    }

    # Best muhurtas today (auspicious + excellent, daytime only)
    best_muhurtas = [
        m for m in muhurtas[:15]
        if m["quality"] in ("auspicious", "excellent")
    ]

    # Build interpretation
    interp_lines = [
        f"Muhurta — Vedic Auspicious Timing for {today}",
        f"Location: {location} (sunrise {_hours_to_time_str(sunrise_h)}, "
        f"sunset {_hours_to_time_str(sunset_h)})",
        f"Day ruler: {day_ruler}",
        f"Current muhurta (midday): {current_muhurta['name']} "
        f"({current_muhurta['quality']})",
        f"Abhijit muhurta: {abhijit_muhurta['start']}-{abhijit_muhurta['end']}",
        f"Rahu Kalam: {rahu_kalam['start']}-{rahu_kalam['end']} (avoid)",
    ]
    if best_muhurtas:
        interp_lines.append("Best windows today:")
        for m in best_muhurtas[:3]:
            interp_lines.append(
                f"  {m['name']} ({m['start']}-{m['end']}): {m['good_for']}")
    interpretation = "\n".join(interp_lines)

    data = {
        "date": today.isoformat(),
        "location": location,
        "sunrise_local": _hours_to_time_str(sunrise_h),
        "sunset_local": _hours_to_time_str(sunset_h),
        "day_ruler": day_ruler,
        "current_muhurta": current_muhurta,
        "abhijit_muhurta": abhijit_muhurta,
        "rahu_kalam": rahu_kalam,
        "gulika_kalam": gulika_kalam,
        "yamagandam": yamagandam,
        "best_muhurtas_today": best_muhurtas,
        "interpretation": interpretation,
    }

    return SystemResult(
        id="muhurta",
        name="Muhurta",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interpretation,
        constants_version=constants["version"],
        references=[
            "Muhurta Chintamani",
            "Varahamihira, Brihat Samhita",
            "Mantreswara, Phaladeepika",
        ],
        question="Q4_TIMING",
    )
