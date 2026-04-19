"""Prashna Natal (Vedic Horary) — Full Horary System

Prashna (Sanskrit: प्रश्न, 'question') casts a chart for the moment the
engine is run — the act of inquiry itself. Classical sources:
  - Prashna Marga (Kerala, ~16th c.) — foundational Kerala prashna text
  - Brihat Prashna Saara (Satyacharya) — classical prashna methodology
  - Prashna Tantra (Neelakantha) — lagna & moon analysis rules

Supports two modes:
  - **full horary**: when question_time is provided (ISO format or HH:MM)
  - **birth_fallback**: uses solar noon at birth location (APPROX)

Full horary adds seven traditional significators, radicality check,
Moon Void-of-Course detection, and Via Combusta check.

Certainty:
  - COMPUTED_STRICT when question_time provided and chart is radical
  - APPROX when birth fallback or non-radical
  - NEEDS_INPUT when no question_time and no birth_time available
"""
from __future__ import annotations
import math
from datetime import date as Date, datetime
from sirr_core.types import InputProfile, SystemResult

# ── Sign data ──────────────────────────────────────────────────────────────
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# ── Chaldean order for planetary hours ─────────────────────────────────────
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Day rulers: Monday=0 in Python weekday()
DAY_RULERS_MAP = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
                  4: "Venus", 5: "Saturn", 6: "Sun"}

# ── Major aspects (orbs in degrees for Moon aspects) ───────────────────────
MAJOR_ASPECTS = [
    ("conjunction", 0, 8),
    ("sextile", 60, 6),
    ("square", 90, 7),
    ("trine", 120, 8),
    ("opposition", 180, 8),
]

# Planet IDs for pyswisseph
PLANET_IDS = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4,
    "Jupiter": 5, "Saturn": 6,
}

# ── Nakshatra data (27 nakshatras, 13°20' each) ────────────────────────────
NAKSHATRAS = [
    ("Ashwini", "Ketu"),      ("Bharani", "Venus"),     ("Krittika", "Sun"),
    ("Rohini", "Moon"),       ("Mrigashira", "Mars"),   ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"), ("Pushya", "Saturn"),     ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"),        ("Purva Phalguni", "Venus"), ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"),        ("Chitra", "Mars"),       ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"),  ("Anuradha", "Saturn"),   ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"),         ("Purva Ashadha", "Venus"), ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"),     ("Dhanishtha", "Mars"),   ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"), ("Uttara Bhadrapada", "Saturn"), ("Revati", "Mercury"),
]

# ── Tara cycle (9 taras × 3 sets = 27 nakshatras from natal Moon) ─────────
TARA_NAMES = [
    ("Janma", "Neutral"),       # 1 — birth nakshatra
    ("Sampat", "Favorable"),    # 2 — wealth
    ("Vipat", "Unfavorable"),   # 3 — danger
    ("Kshema", "Favorable"),    # 4 — wellbeing
    ("Pratyak", "Unfavorable"), # 5 — obstacle
    ("Sadhaka", "Favorable"),   # 6 — achievement
    ("Vadha", "Unfavorable"),   # 7 — destruction
    ("Mitra", "Favorable"),     # 8 — friend
    ("Ati-Mitra", "Favorable"), # 9 — best friend
]

REFERENCES = [
    "Prashna Marga (Kerala, ~16th c.) — primary horary text",
    "Brihat Prashna Saara (Satyacharya) — classical prashna rules",
    "Prashna Tantra (Neelakantha) — lagna & Moon analysis",
    "SOURCE_TIER:A — Classical Vedic primary texts with documented Sanskrit originals.",
]


def _nakshatra_index(sidereal_deg: float) -> int:
    """0-based nakshatra index from sidereal longitude (0–360)."""
    return int(sidereal_deg / (360 / 27)) % 27


def _sign_from_deg(sidereal_deg: float) -> tuple:
    """Return (sign_name, degree_within_sign) from sidereal longitude."""
    sign_idx = int(sidereal_deg / 30) % 12
    deg_in_sign = sidereal_deg % 30
    return SIGNS[sign_idx], round(deg_in_sign, 4)


def _tara(natal_nak_idx: int, prashna_nak_idx: int) -> tuple:
    """Compute tara count + name + quality from natal → prashna nakshatra."""
    count = ((prashna_nak_idx - natal_nak_idx) % 27) + 1  # 1–27
    tara_idx = (count - 1) % 9   # cycles of 9
    name, quality = TARA_NAMES[tara_idx]
    return count, name, quality


def _get_sidereal_asc(jd_ut: float, lat: float, lon: float):
    """Return sidereal ascendant degree using Swiss Ephemeris (Lahiri)."""
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa_ut(jd_ut)
        houses, ascmc = swe.houses(jd_ut, lat, lon, b"W")  # Whole Sign
        tropical_asc = ascmc[0]
        sidereal_asc = (tropical_asc - ayanamsa) % 360
        return sidereal_asc
    except Exception:
        return None


def _get_sidereal_planet(jd_ut: float, planet_id: int):
    """Return sidereal longitude for a planet using Lahiri ayanamsa."""
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        result = swe.calc_ut(jd_ut, planet_id, swe.FLG_SIDEREAL)
        return result[0][0]
    except Exception:
        return None


def _geocode(location: str):
    """Return (lat, lon, utc_offset) via sirr_core geocoder."""
    try:
        from sirr_core.natal_chart import geocode
        geo = geocode(location)
        if geo:
            return geo.lat, geo.lng, geo.utc_offset
    except Exception:
        pass
    return None


def _parse_today(today_val) -> Date:
    """Parse today field from profile."""
    if isinstance(today_val, Date):
        return today_val
    if isinstance(today_val, str):
        try:
            return Date.fromisoformat(today_val)
        except ValueError:
            pass
    return None


def _angular_distance(lon1: float, lon2: float) -> float:
    """Signed angular distance from lon1 to lon2 (positive = lon2 is ahead)."""
    diff = (lon2 - lon1) % 360
    if diff > 180:
        diff -= 360
    return diff


def _find_aspect(moon_lon: float, planet_lon: float):
    """Find closest major aspect between Moon and planet, if within orb."""
    sep = abs(_angular_distance(moon_lon, planet_lon))
    for name, exact_angle, orb in MAJOR_ASPECTS:
        if abs(sep - exact_angle) <= orb:
            return {"aspect": name, "orb": round(abs(sep - exact_angle), 2)}
    return None


def _compute_moon_aspects(jd_ut: float, moon_lon: float):
    """Compute Moon's last (separating) and next (applying) aspects."""
    import swisseph as swe
    swe.set_ephe_path(None)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Get all planet positions
    planet_lons = {}
    for name, pid in PLANET_IDS.items():
        if name == "Moon":
            continue
        lon = _get_sidereal_planet(jd_ut, pid)
        if lon is not None:
            planet_lons[name] = lon

    # Moon speed ≈ 13.2°/day; scan backwards and forwards
    # For separating: check aspect at jd - small step
    # For applying: check aspect at jd + small step
    # Simplified: compute current aspects and classify by direction

    last_aspect = None
    next_aspect = None
    closest_sep = 999
    closest_app = 999

    moon_speed = 13.2  # degrees per day (approximate)

    for planet, plon in planet_lons.items():
        for asp_name, exact_angle, orb in MAJOR_ASPECTS:
            raw_sep = _angular_distance(moon_lon, plon)
            # Check if within extended orb
            abs_sep = abs(abs(raw_sep) - exact_angle)
            if abs_sep > orb + 2:
                continue

            # Determine separating vs applying
            # Moon moves ~13°/day forward. If Moon is past exact aspect, separating.
            # Forward check: compute Moon's approach to exact aspect point
            target_lon = (plon + exact_angle) % 360
            target_lon2 = (plon - exact_angle) % 360

            dist1 = _angular_distance(moon_lon, target_lon)
            dist2 = _angular_distance(moon_lon, target_lon2)

            # Use whichever target is closest
            if abs(dist1) < abs(dist2):
                dist = dist1
            else:
                dist = dist2

            if dist > 0 and dist < closest_app:
                # Moon is approaching this aspect
                closest_app = dist
                next_aspect = {
                    "planet": planet,
                    "aspect": asp_name,
                    "degrees_to_exact": round(dist, 2),
                }
            elif dist <= 0 and abs(dist) < closest_sep:
                # Moon has passed this aspect
                closest_sep = abs(dist)
                last_aspect = {
                    "planet": planet,
                    "aspect": asp_name,
                    "degrees_past": round(abs(dist), 2),
                }

    return last_aspect, next_aspect


def _is_void_of_course(jd_ut: float, moon_lon: float):
    """Check if Moon is void of course (no applying aspects before sign change).

    Simplified: if no applying aspect found within remaining degrees in sign.
    """
    deg_in_sign = moon_lon % 30
    remaining_in_sign = 30 - deg_in_sign

    # Check all planets for applying aspects
    for name, pid in PLANET_IDS.items():
        if name == "Moon":
            continue
        plon = _get_sidereal_planet(jd_ut, pid)
        if plon is None:
            continue
        for asp_name, exact_angle, orb in MAJOR_ASPECTS:
            target = (plon + exact_angle) % 360
            target2 = (plon - exact_angle) % 360
            for t in (target, target2):
                dist = _angular_distance(moon_lon, t)
                if 0 < dist <= remaining_in_sign:
                    return False  # Moon will perfect an aspect before leaving sign
    return True


def _is_via_combusta(moon_lon: float) -> bool:
    """Check if Moon is in Via Combusta (15° Libra – 15° Scorpio).

    Sidereal: Libra starts at 180°, so Via Combusta = 195° to 225°.
    """
    return 195.0 <= moon_lon <= 225.0


def _compute_planetary_hour(today: Date, hour: int, minute: int, utc_offset: float):
    """Compute the planetary hour ruler at the given time."""
    weekday = today.weekday()
    day_ruler = DAY_RULERS_MAP[weekday]
    day_ruler_idx = CHALDEAN_ORDER.index(day_ruler)

    # Approximate sunrise at 6:00 AM local
    total_minutes = hour * 60 + minute
    sunrise_minutes = 6 * 60
    hours_from_sunrise = (total_minutes - sunrise_minutes) // 60
    if hours_from_sunrise < 0:
        hours_from_sunrise += 24

    hour_ruler_idx = (day_ruler_idx + hours_from_sunrise) % 7
    return CHALDEAN_ORDER[hour_ruler_idx]


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    today_raw = getattr(profile, "today", None) or getattr(profile, "dob", None)
    today = _parse_today(today_raw)
    if today is None:
        return SystemResult(
            id="prashna_natal",
            name="Prashna Natal (Vedic Horary)",
            certainty="NEEDS_INPUT",
            interpretation="Question moment unavailable — 'today' field required.",
            data={"error": "No 'today' field — cannot establish question moment"},
            constants_version=constants.get("version", "unknown"),
            references=REFERENCES,
        )

    # ── Determine horary mode ──────────────────────────────────────────────
    question_time_raw = getattr(profile, "question_time", None)
    question_location = getattr(profile, "question_location", None) or getattr(profile, "location", None)
    birth_time = getattr(profile, "birth_time_local", None)

    horary_mode = "birth_fallback"
    using_noon = False

    if question_time_raw:
        horary_mode = "full"
        # Parse ISO datetime or HH:MM
        if "T" in str(question_time_raw):
            try:
                dt = datetime.fromisoformat(str(question_time_raw))
                h, m = dt.hour, dt.minute
                # Override today with the date from question_time
                today = dt.date()
            except ValueError:
                h, m = 12, 0
                using_noon = True
        else:
            try:
                h, m = map(int, str(question_time_raw).split(":"))
            except (ValueError, AttributeError):
                h, m = 12, 0
                using_noon = True
    elif birth_time and str(getattr(profile, "dob", "")) == str(today):
        try:
            h, m = map(int, birth_time.split(":"))
        except (ValueError, AttributeError):
            h, m = 12, 0
            using_noon = True
    else:
        h, m = 12, 0
        using_noon = True

    q_time_str = f"{h:02d}:{m:02d}"

    # ── Geocode question location ─────────────────────────────────────────
    geo = _geocode(question_location) if question_location else None
    if geo is None:
        return SystemResult(
            id="prashna_natal",
            name="Prashna Natal (Vedic Horary)",
            certainty="NEEDS_INPUT",
            interpretation="Question location unknown — cannot cast prashna lagna.",
            data={"error": f"Cannot geocode question location: {question_location!r}"},
            constants_version=constants.get("version", "unknown"),
            references=REFERENCES,
        )

    lat, lon, utc_offset = geo

    # ── Compute Julian Day for question moment ────────────────────────────
    try:
        import swisseph as swe
        ut_hours = (h + m / 60.0) - utc_offset
        jd_ut = swe.julday(today.year, today.month, today.day, ut_hours)
    except ImportError:
        return SystemResult(
            id="prashna_natal",
            name="Prashna Natal (Vedic Horary)",
            certainty="NEEDS_EPHEMERIS",
            interpretation="Swiss Ephemeris (pyswisseph) required for prashna chart.",
            data={"error": "pyswisseph not installed"},
            constants_version=constants.get("version", "unknown"),
            references=REFERENCES,
        )

    # ── Compute Prashna Lagna (Ascendant) ────────────────────────────────
    prashna_asc = _get_sidereal_asc(jd_ut, lat, lon)
    if prashna_asc is None:
        return SystemResult(
            id="prashna_natal",
            name="Prashna Natal (Vedic Horary)",
            certainty="NEEDS_EPHEMERIS",
            interpretation="Ascendant computation failed — ephemeris unavailable.",
            data={"error": "Swiss Ephemeris ascendant computation failed"},
            constants_version=constants.get("version", "unknown"),
            references=REFERENCES,
        )

    lagna_sign, lagna_deg = _sign_from_deg(prashna_asc)
    lagna_lord = SIGN_LORDS[lagna_sign]

    # ── Compute Prashna Moon ──────────────────────────────────────────────
    prashna_moon = _get_sidereal_planet(jd_ut, PLANET_IDS["Moon"])
    if prashna_moon is None:
        return SystemResult(
            id="prashna_natal",
            name="Prashna Natal (Vedic Horary)",
            certainty="NEEDS_EPHEMERIS",
            interpretation="Moon computation failed — ephemeris unavailable.",
            data={"error": "Moon computation failed"},
            constants_version=constants.get("version", "unknown"),
            references=REFERENCES,
        )

    moon_sign, moon_deg_in_sign = _sign_from_deg(prashna_moon)
    moon_nak_idx = _nakshatra_index(prashna_moon)
    moon_nak_name, moon_nak_lord = NAKSHATRAS[moon_nak_idx]

    # ── Get natal Moon nakshatra from kwargs or compute from birth ────────
    natal_chart_data = kwargs.get("natal_chart_data")
    natal_moon_nak_idx = None
    natal_moon_nak_name = None

    if natal_chart_data:
        natal_moon_lon = natal_chart_data.get("moon_sidereal")
        if natal_moon_lon is not None:
            natal_moon_nak_idx = _nakshatra_index(float(natal_moon_lon))
            natal_moon_nak_name = NAKSHATRAS[natal_moon_nak_idx][0]

    if natal_moon_nak_idx is None:
        dob = getattr(profile, "dob", None)
        birth_loc = getattr(profile, "location", None)
        birth_time_str = getattr(profile, "birth_time_local", None)

        if dob and birth_time_str and birth_loc:
            birth_geo = _geocode(birth_loc)
            if birth_geo:
                _, _, birth_utc = birth_geo
                try:
                    bh, bm = map(int, birth_time_str.split(":"))
                    birth_ut = (bh + bm / 60.0) - birth_utc
                    birth_dob = Date.fromisoformat(str(dob)) if isinstance(dob, str) else dob
                    jd_birth = swe.julday(birth_dob.year, birth_dob.month, birth_dob.day, birth_ut)
                    natal_moon = _get_sidereal_planet(jd_birth, PLANET_IDS["Moon"])
                    if natal_moon is not None:
                        natal_moon_nak_idx = _nakshatra_index(natal_moon)
                        natal_moon_nak_name = NAKSHATRAS[natal_moon_nak_idx][0]
                except Exception:
                    pass

    # ── Tara calculation ──────────────────────────────────────────────────
    tara_count = tara_name = tara_quality = None
    if natal_moon_nak_idx is not None:
        tara_count, tara_name, tara_quality = _tara(natal_moon_nak_idx, moon_nak_idx)

    # ── Moon's dispositor (ishta graha) ───────────────────────────────────
    ishta_graha = SIGN_LORDS[moon_sign]

    # ── Horary significators (full mode and birth_fallback) ──────────────
    # Planetary hour ruler
    planetary_hour_ruler = _compute_planetary_hour(today, h, m, utc_offset)

    # Moon aspects
    moon_last_aspect, moon_next_aspect = _compute_moon_aspects(jd_ut, prashna_moon)

    # Void of course
    moon_voc = _is_void_of_course(jd_ut, prashna_moon)

    # Via Combusta
    via_combusta = _is_via_combusta(prashna_moon)

    # ── Radicality check ──────────────────────────────────────────────────
    radicality_notes = []

    # Check 1: Ascendant not in first 3° or last 3° of sign
    if lagna_deg < 3.0:
        radicality_notes.append(f"Ascendant at {lagna_deg:.1f}° — early degrees (< 3°), question may be premature")
    elif lagna_deg > 27.0:
        radicality_notes.append(f"Ascendant at {lagna_deg:.1f}° — late degrees (> 27°), question may be stale")

    # Check 2: Moon void of course
    if moon_voc:
        radicality_notes.append("Moon is Void of Course — no applying aspects before sign change")

    # Check 3: Via Combusta
    if via_combusta:
        radicality_notes.append("Moon in Via Combusta (15° Libra – 15° Scorpio) — afflicted zone")

    # Check 4: Ascendant matches querent's natal ascendant (optional confirmation)
    natal_asc_sign = None
    if natal_chart_data and "ascendant" in natal_chart_data:
        natal_asc_sign = natal_chart_data["ascendant"].get("sign")
        if natal_asc_sign and natal_asc_sign == lagna_sign:
            radicality_notes.append(f"Prashna ascendant matches natal ascendant ({natal_asc_sign}) — strong radicality confirmation")

    # Determine radicality
    critical_issues = 0
    if lagna_deg < 3.0 or lagna_deg > 27.0:
        critical_issues += 1
    if moon_voc:
        critical_issues += 1
    if via_combusta:
        critical_issues += 1

    if critical_issues == 0:
        radicality = "RADICAL"
    elif critical_issues == 1:
        radicality = "QUESTIONABLE"
    else:
        radicality = "NON_RADICAL"

    # Querent significator = Lord of Ascendant
    querent_significator = lagna_lord

    # ── Prashna verdict ───────────────────────────────────────────────────
    verdict_parts = []
    verdict_parts.append(f"Question moment rises {lagna_sign} (lord: {lagna_lord})")
    verdict_parts.append(f"Prashna Moon in {moon_nak_name} nakshatra, {moon_sign}")
    if tara_name and tara_quality:
        verdict_parts.append(f"Tara from natal Moon: {tara_name} ({tara_quality})")
    verdict = ". ".join(verdict_parts) + "."

    # ── Certainty ─────────────────────────────────────────────────────────
    if horary_mode == "full" and not using_noon and radicality == "RADICAL":
        certainty = "COMPUTED_STRICT"
    else:
        certainty = "APPROX"

    # ── Build data dict ───────────────────────────────────────────────────
    data = {
        "horary_mode": horary_mode,
        "question_date": str(today),
        "question_time": q_time_str,
        "question_time_used": q_time_str,
        "question_location": question_location,
        "time_source": "solar_noon_fallback" if using_noon else ("explicit_question_time" if horary_mode == "full" else "explicit_or_birth_time"),
        "prashna_lagna": lagna_sign,
        "prashna_lagna_deg": round(lagna_deg, 2),
        "prashna_lagna_lord": lagna_lord,
        "question_asc_sign": lagna_sign,
        "question_asc_degree": round(prashna_asc, 2),
        "prashna_moon_sign": moon_sign,
        "prashna_moon_deg": round(prashna_moon, 4),
        "prashna_moon_nakshatra": moon_nak_name,
        "prashna_moon_nak_lord": moon_nak_lord,
        "natal_moon_nakshatra": natal_moon_nak_name,
        "tara_count": tara_count,
        "tara_name": tara_name,
        "tara_quality": tara_quality,
        "ishta_graha": ishta_graha,
        "planetary_hour_ruler": planetary_hour_ruler,
        "moon_last_aspect": moon_last_aspect,
        "moon_next_aspect": moon_next_aspect,
        "moon_void_of_course": moon_voc,
        "via_combusta": via_combusta,
        "radicality": radicality,
        "radicality_notes": radicality_notes,
        "querent_significator": querent_significator,
        "prashna_verdict": verdict,
        "note": "Prashna reads the structural quality of the inquiry moment, not fate.",
    }

    # ── Prashna root (for convergence) ────────────────────────────────────
    nak_num = moon_nak_idx + 1  # 1-based
    prashna_root = nak_num
    while prashna_root > 9:
        prashna_root = sum(int(d) for d in str(prashna_root))
    data["prashna_root"] = prashna_root

    # ── Interpretation ────────────────────────────────────────────────────
    interp_parts = [
        f"The inquiry moment rises {lagna_sign}, governed by {lagna_lord}. ",
        f"The Moon occupies {moon_nak_name} nakshatra in {moon_sign}, under {moon_nak_lord}. ",
    ]
    if tara_name:
        interp_parts.append(f"From the natal Moon, this is the {tara_name} tara — {tara_quality.lower()} in quality. ")
    interp_parts.append(f"Chart radicality: {radicality}. ")
    if moon_voc:
        interp_parts.append("Moon is Void of Course — matters may not manifest as expected. ")
    if via_combusta:
        interp_parts.append("Moon in Via Combusta — the inquiry traverses an afflicted zone. ")
    interp_parts.append("Prashna reads the structural signature of the inquiry moment, not the outcome.")

    return SystemResult(
        id="prashna_natal",
        name="Prashna Natal (Vedic Horary)",
        certainty=certainty,
        interpretation="".join(interp_parts),
        data=data,
        constants_version=constants.get("version", "unknown"),
        references=REFERENCES,
    )
