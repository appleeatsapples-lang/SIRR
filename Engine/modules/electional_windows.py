"""Electional Timing Windows — Ilm al-Ikhtiyarat — COMPUTED_STRICT
Computes structural timing windows for a 90-day horizon based on lunar
phase cycles, planetary day/hour favorability, Void of Course Moon,
and Moon sign favorability by action category.

Five action categories: communication_launch, career_authority,
creative_relationship, financial_material, spiritual_inner_work.

Sources: Abu Ma'shar (Kitab al-Ikhtiyarat), Dorotheus of Sidon
         (Carmen Astrologicum), Bonatti (Liber Astronomiae)
"""
from __future__ import annotations
from datetime import date, timedelta
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Day of week (0=Mon) → planetary ruler
DAY_RULERS = {
    0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
    4: "Venus", 5: "Saturn", 6: "Sun",
}

# Action category definitions
CATEGORIES = {
    "communication_launch": {
        "moon_signs": {"Gemini", "Virgo", "Aquarius"},
        "avoid_retrograde": "Mercury",
        "favorable_days": {"Wednesday", "Sunday"},
        "label": "Communication & Launch",
    },
    "career_authority": {
        "moon_signs": {"Capricorn", "Aries"},
        "avoid_retrograde": None,
        "favorable_days": {"Saturday", "Sunday"},
        "label": "Career & Authority",
    },
    "creative_relationship": {
        "moon_signs": {"Taurus", "Libra", "Pisces"},
        "avoid_retrograde": "Venus",
        "favorable_days": {"Friday"},
        "label": "Creative & Relationship",
    },
    "financial_material": {
        "moon_signs": {"Taurus", "Capricorn"},
        "avoid_retrograde": None,
        "favorable_days": {"Thursday", "Friday"},
        "waxing_required": True,
        "label": "Financial & Material",
    },
    "spiritual_inner_work": {
        "moon_signs": {"Pisces", "Cancer", "Scorpio"},
        "avoid_retrograde": None,
        "favorable_days": {"Monday", "Saturday"},
        "label": "Spiritual & Inner Work",
    },
}

DOW_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]

# Major aspects for VOC Moon detection
ASPECT_ORBS = [0, 60, 90, 120, 180]  # conjunction, sextile, square, trine, opposition


def _sign_of(longitude: float) -> str:
    return SIGNS[int(longitude // 30) % 12]


def _is_waxing(moon_lon: float, sun_lon: float) -> bool:
    return (moon_lon - sun_lon) % 360 < 180


def _phase_name(phase_angle: float) -> str:
    if phase_angle < 45:
        return "New Moon"
    elif phase_angle < 90:
        return "Waxing Crescent"
    elif phase_angle < 135:
        return "First Quarter"
    elif phase_angle < 180:
        return "Waxing Gibbous"
    elif phase_angle < 225:
        return "Full Moon"
    elif phase_angle < 270:
        return "Waning Gibbous"
    elif phase_angle < 315:
        return "Last Quarter"
    else:
        return "Waning Crescent"


def _compute_daily_data(start_date: date, days: int, tz_offset: float):
    """Pre-compute Moon sign, phase, and planet positions for each day."""
    import swisseph as swe
    swe.set_ephe_path(None)

    daily = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        jd = swe.julday(d.year, d.month, d.day, 12.0 - tz_offset)

        moon = swe.calc_ut(jd, swe.MOON)
        sun = swe.calc_ut(jd, swe.SUN)
        moon_lon = moon[0][0]
        sun_lon = sun[0][0]
        moon_speed = moon[0][3]

        phase_angle = (moon_lon - sun_lon) % 360

        daily.append({
            "date": d,
            "jd": jd,
            "moon_lon": moon_lon,
            "moon_sign": _sign_of(moon_lon),
            "moon_speed": moon_speed,
            "sun_lon": sun_lon,
            "phase_angle": phase_angle,
            "phase_name": _phase_name(phase_angle),
            "waxing": _is_waxing(moon_lon, sun_lon),
            "dow_name": DOW_NAMES[d.weekday()],
        })
    return daily


def _find_retrograde_periods(start_date: date, days: int,
                              planet_id: int, tz_offset: float) -> list:
    """Find retrograde periods for a planet within the date range."""
    import swisseph as swe
    swe.set_ephe_path(None)

    periods = []
    in_retro = False
    retro_start = None

    for i in range(-7, days + 7):  # extend search slightly
        d = start_date + timedelta(days=i)
        jd = swe.julday(d.year, d.month, d.day, 12.0 - tz_offset)
        r = swe.calc_ut(jd, planet_id)
        speed = r[0][3]

        if speed < 0 and not in_retro:
            in_retro = True
            retro_start = d
        elif speed >= 0 and in_retro:
            in_retro = False
            # Clip to our range
            s = max(retro_start, start_date)
            e = min(d, start_date + timedelta(days=days - 1))
            if s <= e:
                periods.append({
                    "start": s.isoformat(),
                    "end": e.isoformat(),
                })

    # Handle case where retrograde extends past our range
    if in_retro and retro_start is not None:
        s = max(retro_start, start_date)
        e = start_date + timedelta(days=days - 1)
        if s <= e:
            periods.append({
                "start": s.isoformat(),
                "end": e.isoformat(),
            })

    return periods


def _is_voc_moon(jd: float, moon_lon: float) -> bool:
    """Check if Moon is Void of Course (no major aspects before sign change).

    Simplified: if Moon is in the last 5 degrees of a sign and not applying
    to any major aspect with traditional planets, consider VOC.
    """
    import swisseph as swe

    deg_in_sign = moon_lon % 30
    if deg_in_sign < 25:
        return False  # not near sign boundary

    # Check if Moon applies to any major aspect with traditional planets
    planet_ids = [swe.SUN, swe.MERCURY, swe.VENUS, swe.MARS,
                  swe.JUPITER, swe.SATURN]
    for pid in planet_ids:
        p_lon = swe.calc_ut(jd, pid)[0][0]
        for aspect in ASPECT_ORBS:
            diff = (moon_lon - p_lon) % 360
            # Check applying aspect within remaining degrees in sign
            remaining = 30 - deg_in_sign
            for target in [aspect, 360 - aspect]:
                if abs(diff - target) < remaining:
                    return False  # Moon applies to an aspect
    return True


def _is_in_retrograde(d: date, retro_periods: list) -> bool:
    ds = d.isoformat()
    for p in retro_periods:
        if p["start"] <= ds <= p["end"]:
            return True
    return False


def _find_new_full_moons(daily: list) -> tuple:
    """Find next new moon and full moon from daily data."""
    new_moon = None
    full_moon = None
    prev_pa = daily[0]["phase_angle"] if daily else 0

    for day in daily[1:]:
        pa = day["phase_angle"]
        # New moon: phase wraps from >300 to <60
        if prev_pa > 300 and pa < 60 and new_moon is None:
            new_moon = {
                "date": day["date"].isoformat(),
                "sign": day["moon_sign"],
            }
        # Full moon: phase crosses 180
        if prev_pa < 180 and pa >= 180 and full_moon is None:
            full_moon = {
                "date": day["date"].isoformat(),
                "sign": day["moon_sign"],
            }
        prev_pa = pa
        if new_moon and full_moon:
            break

    return new_moon, full_moon


def _score_day(day: dict, cat_key: str, cat: dict,
               mercury_retro: list, venus_retro: list) -> float:
    """Score a day's favorability for a given action category (0-10)."""
    score = 0.0

    # Moon sign match (+4)
    if day["moon_sign"] in cat["moon_signs"]:
        score += 4.0

    # Favorable day of week (+2)
    if day["dow_name"] in cat["favorable_days"]:
        score += 2.0

    # Waxing bonus for financial (+2)
    if cat.get("waxing_required") and day["waxing"]:
        score += 2.0
    elif cat.get("waxing_required") and not day["waxing"]:
        score -= 2.0

    # New/Full moon bonus (+1)
    if day["phase_name"] in ("New Moon", "Full Moon"):
        score += 1.0

    # Retrograde penalty (-3)
    retro_planet = cat.get("avoid_retrograde")
    if retro_planet == "Mercury" and _is_in_retrograde(day["date"], mercury_retro):
        score -= 3.0
    elif retro_planet == "Venus" and _is_in_retrograde(day["date"], venus_retro):
        score -= 3.0

    # VOC Moon penalty (-2)
    if day.get("voc"):
        score -= 2.0

    return score


def _build_windows(scored_days: list, top_n: int = 5) -> list:
    """Group consecutive high-scoring days into windows."""
    if not scored_days:
        return []

    # Sort by score descending
    ranked = sorted(scored_days, key=lambda x: x["score"], reverse=True)

    windows = []
    used_dates = set()

    for day in ranked:
        if len(windows) >= top_n:
            break
        d = day["date"]
        if d in used_dates:
            continue

        # Try to extend into a 2-3 day window
        window_dates = [d]
        used_dates.add(d)

        # Check next day
        next_d = d + timedelta(days=1)
        for sd in scored_days:
            if sd["date"] == next_d and sd["score"] > 0 and next_d not in used_dates:
                window_dates.append(next_d)
                used_dates.add(next_d)
                break

        quality = "excellent" if day["score"] >= 5 else "good"
        windows.append({
            "start": window_dates[0].isoformat(),
            "end": window_dates[-1].isoformat(),
            "moon_sign": day["moon_sign"],
            "quality": quality,
            "notes": f"{day['phase_name']}, {day['dow_name']}",
        })

    return windows


def _build_avoid_periods(scored_days: list, mercury_retro: list,
                          venus_retro: list, cat: dict,
                          top_n: int = 5) -> list:
    """Identify worst periods for this category."""
    avoids = []

    # Retrograde periods
    retro_planet = cat.get("avoid_retrograde")
    if retro_planet == "Mercury":
        for p in mercury_retro:
            avoids.append({
                "start": p["start"],
                "end": p["end"],
                "reason": "Mercury retrograde",
                "notes": f"Avoid new {cat['label'].lower()} initiatives",
            })
    elif retro_planet == "Venus":
        for p in venus_retro:
            avoids.append({
                "start": p["start"],
                "end": p["end"],
                "reason": "Venus retrograde",
                "notes": f"Avoid new {cat['label'].lower()} initiatives",
            })

    # Add worst-scored individual days as VOC/unfavorable
    worst = sorted(scored_days, key=lambda x: x["score"])
    used = set()
    for day in worst:
        if len(avoids) >= top_n:
            break
        d = day["date"]
        if d.isoformat() in used:
            continue
        if day.get("voc") or day["score"] < -1:
            used.add(d.isoformat())
            reason = "VOC Moon" if day.get("voc") else "Unfavorable alignment"
            avoids.append({
                "start": d.isoformat(),
                "end": d.isoformat(),
                "reason": reason,
                "notes": f"Moon in {day['moon_sign']}, {day['phase_name']}",
            })

    return avoids[:top_n]


def compute(profile: InputProfile, constants: dict,
            natal_chart_data: dict = None, **kwargs) -> SystemResult:
    import swisseph as swe

    ref_date = profile.today
    horizon = 90
    tz_offset = 3.0  # Asia/Riyadh

    # Compute daily ephemeris data
    daily = _compute_daily_data(ref_date, horizon, tz_offset)

    # Mark VOC Moon days
    for day in daily:
        day["voc"] = _is_voc_moon(day["jd"], day["moon_lon"])

    # Find retrograde periods
    mercury_retro = _find_retrograde_periods(
        ref_date, horizon, swe.MERCURY, tz_offset)
    venus_retro = _find_retrograde_periods(
        ref_date, horizon, swe.VENUS, tz_offset)

    # Find next new/full moons
    new_moon, full_moon = _find_new_full_moons(daily)

    # Score each day per category and build windows
    action_windows = {}
    for cat_key, cat in CATEGORIES.items():
        scored = []
        for day in daily:
            s = _score_day(day, cat_key, cat, mercury_retro, venus_retro)
            scored.append({
                "date": day["date"],
                "moon_sign": day["moon_sign"],
                "phase_name": day["phase_name"],
                "dow_name": day["dow_name"],
                "score": s,
                "voc": day["voc"],
            })

        best = _build_windows(scored, top_n=5)
        avoid = _build_avoid_periods(scored, mercury_retro, venus_retro,
                                      cat, top_n=5)

        action_windows[cat_key] = {
            "best_windows": best,
            "avoid_periods": avoid,
        }

    # Build interpretation summary
    interp_lines = [f"Electional Windows — 90-day horizon from {ref_date}"]
    if mercury_retro:
        interp_lines.append(
            f"Mercury retrograde: {mercury_retro[0]['start']} to "
            f"{mercury_retro[0]['end']}")
    if new_moon:
        interp_lines.append(
            f"Next New Moon: {new_moon['date']} in {new_moon['sign']}")
    if full_moon:
        interp_lines.append(
            f"Next Full Moon: {full_moon['date']} in {full_moon['sign']}")
    for cat_key, cat in CATEGORIES.items():
        wins = action_windows[cat_key]["best_windows"]
        if wins:
            interp_lines.append(
                f"{cat['label']}: best window {wins[0]['start']} "
                f"({wins[0]['moon_sign']}, {wins[0]['quality']})")
    interpretation = "\n".join(interp_lines)

    data = {
        "reference_date": ref_date.isoformat(),
        "window_horizon_days": horizon,
        "mercury_retrograde_periods": mercury_retro,
        "venus_retrograde_periods": venus_retro,
        "action_windows": action_windows,
        "next_new_moon": new_moon,
        "next_full_moon": full_moon,
        "interpretation": interpretation,
    }

    return SystemResult(
        id="electional_windows",
        name="Electional Timing Windows",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interpretation,
        constants_version=constants["version"],
        references=[
            "Abu Ma'shar, Kitab al-Ikhtiyarat (Book of Elections)",
            "Dorotheus of Sidon, Carmen Astrologicum",
            "Guido Bonatti, Liber Astronomiae",
        ],
        question="Q4_TIMING",
    )
