"""
SIRR Natal Chart Utility — Geocoding + Ephemeris Computation.

Preprocessing utility for the web server and runner. NOT a SIRR module.
Uses pyswisseph for astronomical calculations.

Usage:
    from sirr_core.natal_chart import geocode, compute_chart

    geo = geocode("Cairo, Egypt")
    chart = compute_chart(date(1990,3,15), "14:22", geo.lat, geo.lng, geo.utc_offset)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import date
from typing import Dict, List, Optional, Tuple


# ── Zodiac Signs ──────────────────────────────────────────────────────

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ── Nakshatras (27 lunar mansions) ────────────────────────────────────

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]


# ── Geocoding Database ────────────────────────────────────────────────

@dataclass
class GeoResult:
    """Result of a geocoding lookup."""
    lat: float
    lng: float
    tz_name: str
    utc_offset: float       # hours from UTC (standard time)
    city: str               # normalized city name

# (lat, lng, tz_name, utc_offset, display_name)
# utc_offset is STANDARD time (not DST-adjusted)
CITY_DB: Dict[str, Tuple[float, float, str, float, str]] = {
    # ── Middle East ──
    "riyadh":           (24.7136, 46.6753, "Asia/Riyadh", 3, "Riyadh, Saudi Arabia"),
    "jeddah":           (21.5433, 39.1728, "Asia/Riyadh", 3, "Jeddah, Saudi Arabia"),
    "mecca":            (21.3891, 39.8579, "Asia/Riyadh", 3, "Mecca, Saudi Arabia"),
    "medina":           (24.4539, 39.6142, "Asia/Riyadh", 3, "Medina, Saudi Arabia"),
    "dammam":           (26.4207, 50.0888, "Asia/Riyadh", 3, "Dammam, Saudi Arabia"),
    "dubai":            (25.2048, 55.2708, "Asia/Dubai", 4, "Dubai, UAE"),
    "abu dhabi":        (24.4539, 54.3773, "Asia/Dubai", 4, "Abu Dhabi, UAE"),
    "doha":             (25.2854, 51.5310, "Asia/Qatar", 3, "Doha, Qatar"),
    "kuwait city":      (29.3759, 47.9774, "Asia/Kuwait", 3, "Kuwait City, Kuwait"),
    "kuwait":           (29.3759, 47.9774, "Asia/Kuwait", 3, "Kuwait City, Kuwait"),
    "manama":           (26.2285, 50.5860, "Asia/Bahrain", 3, "Manama, Bahrain"),
    "muscat":           (23.5880, 58.3829, "Asia/Muscat", 4, "Muscat, Oman"),
    "amman":            (31.9454, 35.9284, "Asia/Amman", 2, "Amman, Jordan"),
    "beirut":           (33.8938, 35.5018, "Asia/Beirut", 2, "Beirut, Lebanon"),
    "damascus":         (33.5138, 36.2765, "Asia/Damascus", 2, "Damascus, Syria"),
    "baghdad":          (33.3152, 44.3661, "Asia/Baghdad", 3, "Baghdad, Iraq"),
    "tehran":           (35.6892, 51.3890, "Asia/Tehran", 3.5, "Tehran, Iran"),
    "isfahan":          (32.6546, 51.6680, "Asia/Tehran", 3.5, "Isfahan, Iran"),
    "jerusalem":        (31.7683, 35.2137, "Asia/Jerusalem", 2, "Jerusalem"),
    "tel aviv":         (32.0853, 34.7818, "Asia/Jerusalem", 2, "Tel Aviv, Israel"),
    "istanbul":         (41.0082, 28.9784, "Europe/Istanbul", 3, "Istanbul, Turkey"),
    "ankara":           (39.9334, 32.8597, "Europe/Istanbul", 3, "Ankara, Turkey"),
    "sanaa":            (15.3694, 44.1910, "Asia/Aden", 3, "Sanaa, Yemen"),
    "tikrit":           (34.6137, 43.6789, "Asia/Baghdad", 3, "Tikrit, Iraq"),
    "samarra":          (34.1959, 43.8750, "Asia/Baghdad", 3, "Samarra, Iraq"),
    # ── Caucasus / Central Asia ──
    "gori":             (41.9826, 44.1132, "Asia/Tbilisi", 3, "Gori, Georgia"),
    "tbilisi":          (41.7151, 44.8271, "Asia/Tbilisi", 3, "Tbilisi, Georgia"),
    "merkheuli":        (42.3833, 41.7833, "Asia/Tbilisi", 3, "Merkheuli, Georgia"),
    "balkh":            (36.7581, 66.8981, "Asia/Kabul", 4.5, "Balkh, Afghanistan"),
    "kabul":            (34.5553, 69.2075, "Asia/Kabul", 4.5, "Kabul, Afghanistan"),
    "shahrisabz":       (39.0517, 66.8303, "Asia/Samarkand", 5, "Shahrisabz, Uzbekistan"),
    "samarkand":        (39.6542, 66.9597, "Asia/Samarkand", 5, "Samarkand, Uzbekistan"),
    # ── South Asia ──
    "mumbai":           (19.0760, 72.8777, "Asia/Kolkata", 5.5, "Mumbai, India"),
    "delhi":            (28.7041, 77.1025, "Asia/Kolkata", 5.5, "Delhi, India"),
    "new delhi":        (28.6139, 77.2090, "Asia/Kolkata", 5.5, "New Delhi, India"),
    "bangalore":        (12.9716, 77.5946, "Asia/Kolkata", 5.5, "Bangalore, India"),
    "chennai":          (13.0827, 80.2707, "Asia/Kolkata", 5.5, "Chennai, India"),
    "kolkata":          (22.5726, 88.3639, "Asia/Kolkata", 5.5, "Kolkata, India"),
    "karachi":          (24.8607, 67.0011, "Asia/Karachi", 5, "Karachi, Pakistan"),
    "lahore":           (31.5497, 74.3436, "Asia/Karachi", 5, "Lahore, Pakistan"),
    "islamabad":        (33.6844, 73.0479, "Asia/Karachi", 5, "Islamabad, Pakistan"),
    "dhaka":            (23.8103, 90.4125, "Asia/Dhaka", 6, "Dhaka, Bangladesh"),
    "colombo":          (6.9271, 79.8612, "Asia/Colombo", 5.5, "Colombo, Sri Lanka"),
    # ── East Asia ──
    "beijing":          (39.9042, 116.4074, "Asia/Shanghai", 8, "Beijing, China"),
    "shanghai":         (31.2304, 121.4737, "Asia/Shanghai", 8, "Shanghai, China"),
    "shaoshan":         (27.9152, 112.4937, "Asia/Shanghai", 8, "Shaoshan, China"),
    "hong kong":        (22.3193, 114.1694, "Asia/Hong_Kong", 8, "Hong Kong"),
    "tokyo":            (35.6762, 139.6503, "Asia/Tokyo", 9, "Tokyo, Japan"),
    "kyoto":            (35.0116, 135.7681, "Asia/Tokyo", 9, "Kyoto, Japan"),
    "seoul":            (37.5665, 126.9780, "Asia/Seoul", 9, "Seoul, South Korea"),
    "pyongyang":        (39.0392, 125.7625, "Asia/Pyongyang", 9, "Pyongyang, North Korea"),
    "mangyongdae":      (39.0050, 125.7289, "Asia/Pyongyang", 9, "Mangyongdae, North Korea"),
    "taipei":           (25.0330, 121.5654, "Asia/Taipei", 8, "Taipei, Taiwan"),
    "bangkok":          (13.7563, 100.5018, "Asia/Bangkok", 7, "Bangkok, Thailand"),
    "jakarta":          (-6.2088, 106.8456, "Asia/Jakarta", 7, "Jakarta, Indonesia"),
    "kuala lumpur":     (3.1390, 101.6869, "Asia/Kuala_Lumpur", 8, "Kuala Lumpur, Malaysia"),
    "singapore":        (1.3521, 103.8198, "Asia/Singapore", 8, "Singapore"),
    # Historical — Mongolia
    "khentii":          (48.0000, 109.5000, "Asia/Ulaanbaatar", 8, "Khentii, Mongolia"),
    "ulaanbaatar":      (47.9077, 106.9222, "Asia/Ulaanbaatar", 8, "Ulaanbaatar, Mongolia"),
    # ── Africa ──
    "cairo":            (30.0444, 31.2357, "Africa/Cairo", 2, "Cairo, Egypt"),
    "alexandria":       (31.2001, 29.9187, "Africa/Cairo", 2, "Alexandria, Egypt"),
    "casablanca":       (33.5731, -7.5898, "Africa/Casablanca", 1, "Casablanca, Morocco"),
    "lagos":            (6.5244, 3.3792, "Africa/Lagos", 1, "Lagos, Nigeria"),
    "nairobi":          (-1.2921, 36.8219, "Africa/Nairobi", 3, "Nairobi, Kenya"),
    "johannesburg":     (-26.2041, 28.0473, "Africa/Johannesburg", 2, "Johannesburg, South Africa"),
    "addis ababa":      (9.0250, 38.7469, "Africa/Addis_Ababa", 3, "Addis Ababa, Ethiopia"),
    "koboko":           (3.4141, 30.9603, "Africa/Kampala", 3, "Koboko, Uganda"),
    "kampala":          (0.3476, 32.5825, "Africa/Kampala", 3, "Kampala, Uganda"),
    "qasr abu hadi":    (31.1706, 16.5892, "Africa/Tripoli", 2, "Qasr Abu Hadi, Libya"),
    "tripoli":          (32.9023, 13.1800, "Africa/Tripoli", 2, "Tripoli, Libya"),
    "kutama":           (-17.3167, 30.1500, "Africa/Harare", 2, "Kutama, Zimbabwe"),
    "harare":           (-17.8252, 31.0335, "Africa/Harare", 2, "Harare, Zimbabwe"),
    # ── Europe ──
    "london":           (51.5074, -0.1278, "Europe/London", 0, "London, UK"),
    "paris":            (48.8566, 2.3522, "Europe/Paris", 1, "Paris, France"),
    "berlin":           (52.5200, 13.4050, "Europe/Berlin", 1, "Berlin, Germany"),
    "madrid":           (40.4168, -3.7038, "Europe/Madrid", 1, "Madrid, Spain"),
    "rome":             (41.9028, 12.4964, "Europe/Rome", 1, "Rome, Italy"),
    "amsterdam":        (52.3676, 4.9041, "Europe/Amsterdam", 1, "Amsterdam, Netherlands"),
    "moscow":           (55.7558, 37.6173, "Europe/Moscow", 3, "Moscow, Russia"),
    "vienna":           (48.2082, 16.3738, "Europe/Vienna", 1, "Vienna, Austria"),
    "athens":           (37.9838, 23.7275, "Europe/Athens", 2, "Athens, Greece"),
    # Historical birthplaces — Germany
    "braunau":          (48.2567, 13.0333, "Europe/Vienna", 1, "Braunau, Austria"),
    "braunau am inn":   (48.2567, 13.0333, "Europe/Vienna", 1, "Braunau am Inn, Austria"),
    "trier":            (49.7490, 6.6371, "Europe/Berlin", 1, "Trier, Germany"),
    "rocken":           (51.2500, 12.1167, "Europe/Berlin", 1, "Röcken, Germany"),
    "schonhausen":      (52.6333, 12.0000, "Europe/Berlin", 1, "Schönhausen, Germany"),
    "rheydt":           (51.1622, 6.4456, "Europe/Berlin", 1, "Rheydt, Germany"),
    "munich":           (48.1351, 11.5820, "Europe/Berlin", 1, "Munich, Germany"),
    "ulm":              (48.4011, 9.9876,  "Europe/Berlin", 1, "Ulm, Germany"),
    "ulm germany":      (48.4011, 9.9876,  "Europe/Berlin", 1, "Ulm, Germany"),
    "freiberg":         (49.8528, 18.3467, "Europe/Prague", 1, "Freiberg, Czech Republic"),
    "pribor":           (49.6408, 18.1450, "Europe/Prague", 1, "Příbor, Czech Republic"),
    # Historical birthplaces — Italy / Mediterranean
    "predappio":        (44.1019, 11.9819, "Europe/Rome", 1, "Predappio, Italy"),
    "florence":         (43.7696, 11.2558, "Europe/Rome", 1, "Florence, Italy"),
    "firenze":          (43.7696, 11.2558, "Europe/Rome", 1, "Florence, Italy"),
    "ajaccio":          (41.9192, 8.7386, "Europe/Paris", 1, "Ajaccio, Corsica"),
    "antium":           (41.4480, 12.6700, "Europe/Rome", 1, "Antium (Anzio), Italy"),
    "anzio":            (41.4480, 12.6700, "Europe/Rome", 1, "Anzio, Italy"),
    # Historical birthplaces — Eastern Europe / Balkans / Croatia
    "zagreb":           (45.8150, 15.9819, "Europe/Zagreb", 1, "Zagreb, Croatia"),
    "zagreb croatia":   (45.8150, 15.9819, "Europe/Zagreb", 1, "Zagreb, Croatia"),
    "smiljan":          (44.5667, 15.3167, "Europe/Zagreb", 1, "Smiljan, Croatia"),
    "smiljan croatia":  (44.5667, 15.3167, "Europe/Zagreb", 1, "Smiljan, Croatia"),
    "sighisoara":       (46.2197, 24.7956, "Europe/Bucharest", 2, "Sighișoara, Romania"),
    "pozarevac":        (44.6225, 21.1869, "Europe/Belgrade", 1, "Požarevac, Serbia"),
    "nyirbator":        (47.8369, 22.1294, "Europe/Budapest", 1, "Nyírbátor, Hungary"),
    "pella":            (40.7617, 22.5217, "Europe/Athens", 2, "Pella, Greece"),
    # Historical birthplaces — Switzerland
    "kesswil":          (47.5960, 9.3167, "Europe/Zurich", 1, "Kesswil, Switzerland"),
    # Historical birthplaces — UK
    "malmesbury":       (51.5858, -2.0990, "Europe/London", 0, "Malmesbury, England"),
    "leamington spa":   (52.2852, -1.5201, "Europe/London", 0, "Leamington Spa, England"),
    # Historical birthplaces — Iberia
    "ferrol":           (43.4840, -8.2328, "Europe/Madrid", 0, "Ferrol, Spain"),
    # Historical birthplaces — Russia
    "pokrovskoye":      (57.7833, 64.1333, "Asia/Yekaterinburg", 5, "Pokrovskoye, Russia"),
    "ulyanovsk":        (54.3142, 48.4031, "Europe/Samara", 4, "Ulyanovsk, Russia"),
    "st petersburg":    (59.9343, 30.3351, "Europe/Moscow", 3, "St. Petersburg, Russia"),
    "simbirsk":         (54.3142, 48.4031, "Europe/Samara", 4, "Simbirsk (Ulyanovsk), Russia"),
    # ── Americas ──
    "new york":         (40.7128, -74.0060, "America/New_York", -5, "New York, USA"),
    "brooklyn":         (40.6782, -73.9442, "America/New_York", -5, "Brooklyn, USA"),
    "los angeles":      (34.0522, -118.2437, "America/Los_Angeles", -8, "Los Angeles, USA"),
    "san francisco":    (37.7749, -122.4194, "America/Los_Angeles", -8, "San Francisco, USA"),
    "louisville":       (38.2527, -85.7585,  "America/New_York",    -5, "Louisville, USA"),
    "chicago":          (41.8781, -87.6298, "America/Chicago", -6, "Chicago, USA"),
    "houston":          (29.7604, -95.3698, "America/Chicago", -6, "Houston, USA"),
    "washington":       (38.9072, -77.0369, "America/New_York", -5, "Washington DC, USA"),
    "toronto":          (43.6532, -79.3832, "America/Toronto", -5, "Toronto, Canada"),
    "edmonton":         (53.5461, -113.4938, "America/Edmonton", -7, "Edmonton, Canada"),
    "mexico city":      (19.4326, -99.1332, "America/Mexico_City", -6, "Mexico City, Mexico"),
    "sao paulo":        (-23.5505, -46.6333, "America/Sao_Paulo", -3, "São Paulo, Brazil"),
    "buenos aires":     (-34.6037, -58.3816, "America/Argentina/Buenos_Aires", -3, "Buenos Aires, Argentina"),
    "bogota":           (4.7110, -74.0721, "America/Bogota", -5, "Bogotá, Colombia"),
    "lima":             (-12.0464, -77.0428, "America/Lima", -5, "Lima, Peru"),
    "valparaiso":       (-33.0472, -71.6127, "America/Santiago", -4, "Valparaíso, Chile"),
    "santiago":         (-33.4489, -70.6693, "America/Santiago", -4, "Santiago, Chile"),
    # ── Oceania ──
    "sydney":           (-33.8688, 151.2093, "Australia/Sydney", 10, "Sydney, Australia"),
    "melbourne":        (-37.8136, 144.9631, "Australia/Melbourne", 10, "Melbourne, Australia"),
    "auckland":         (-36.8485, 174.7633, "Pacific/Auckland", 12, "Auckland, New Zealand"),
}

# Build a mapping from the old natal_chart module's location format
_LEGACY_LOCATION_MAP = {
    "Riyadh, Saudi Arabia": "riyadh",
    "Jeddah, Saudi Arabia": "jeddah",
    "Amman, Jordan": "amman",
    "Cairo, Egypt": "cairo",
    "Dubai, UAE": "dubai",
    "Kuwait City, Kuwait": "kuwait city",
    "Beirut, Lebanon": "beirut",
    "Damascus, Syria": "damascus",
    "Baghdad, Iraq": "baghdad",
    "Istanbul, Turkey": "istanbul",
    "London, UK": "london",
    "New York, USA": "new york",
}


def geocode(place: str) -> Optional[GeoResult]:
    """
    Resolve a place string to coordinates + timezone.

    Accepts:
      - City name: "Cairo", "New York", "tokyo"
      - Legacy format: "Cairo, Egypt"
      - Lat,lng: "30.0444,31.2357" (assumes UTC+0, caller should override)
      - Lat,lng with tz: "30.0444,31.2357,2" (third value = UTC offset)

    Returns GeoResult or None if unrecognized.
    """
    if not place or not place.strip():
        return None

    raw = place.strip()

    # 1. Try lat,lng[,tz_offset] format
    m = re.match(r'^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)(?:\s*,\s*(-?\d+\.?\d*))?$', raw)
    if m:
        lat = float(m.group(1))
        lng = float(m.group(2))
        tz_off = float(m.group(3)) if m.group(3) else 0.0
        return GeoResult(lat=lat, lng=lng, tz_name="UTC", utc_offset=tz_off, city=raw)

    # 2. Try legacy format ("City, Country")
    legacy_key = raw
    if legacy_key in _LEGACY_LOCATION_MAP:
        return _lookup_city(_LEGACY_LOCATION_MAP[legacy_key])

    # 3. Normalize and try city lookup
    normalized = raw.lower().strip().rstrip(".,")
    # Strip country suffix for matching: "cairo, egypt" → "cairo"
    result = _lookup_city(normalized)
    if result:
        return result

    # Try just the city part (before comma)
    if "," in normalized:
        city_part = normalized.split(",")[0].strip()
        result = _lookup_city(city_part)
        if result:
            return result

    return None


def _lookup_city(key: str) -> Optional[GeoResult]:
    """Look up a city in the database by normalized key."""
    if key in CITY_DB:
        lat, lng, tz_name, utc_offset, display = CITY_DB[key]
        return GeoResult(lat=lat, lng=lng, tz_name=tz_name, utc_offset=utc_offset, city=display)
    return None


# ── Planets ───────────────────────────────────────────────────────────

PLANETS = [
    ("Sun", 0),       # swe.SUN
    ("Moon", 1),       # swe.MOON
    ("Mercury", 2),    # swe.MERCURY
    ("Venus", 3),      # swe.VENUS
    ("Mars", 4),       # swe.MARS
    ("Jupiter", 5),    # swe.JUPITER
    ("Saturn", 6),     # swe.SATURN
    ("Uranus", 7),     # swe.URANUS
    ("Neptune", 8),    # swe.NEPTUNE
    ("Pluto", 9),      # swe.PLUTO
    ("North Node", 11), # swe.MEAN_NODE
]


# ── Chart Computation ─────────────────────────────────────────────────

def _sign_from_longitude(lon: float) -> Tuple[str, int, int]:
    """Return (sign_name, degree_in_sign, minute) from ecliptic longitude."""
    sign_idx = int(lon // 30) % 12
    deg_in_sign = lon % 30
    degree = int(deg_in_sign)
    minute = int((deg_in_sign - degree) * 60)
    return SIGNS[sign_idx], degree, minute


def _nakshatra_from_longitude(moon_lon: float) -> Tuple[str, int]:
    """Return (nakshatra_name, pada) from Moon's ecliptic longitude."""
    nak_span = 360.0 / 27.0   # 13°20' = 13.3333°
    pada_span = nak_span / 4.0  # 3°20' per pada
    nak_idx = int(moon_lon / nak_span) % 27
    pada = int((moon_lon % nak_span) / pada_span) + 1
    if pada > 4:
        pada = 4
    return NAKSHATRAS[nak_idx], pada


def compute_chart(
    dob: date,
    birth_time: str,
    lat: float,
    lng: float,
    tz_offset: float,
) -> dict:
    """
    Compute a full natal chart using Swiss Ephemeris.

    Args:
        dob: Date of birth
        birth_time: "HH:MM" format (local time)
        lat: Latitude in decimal degrees
        lng: Longitude in decimal degrees
        tz_offset: Hours from UTC (e.g., 3 for Asia/Riyadh)

    Returns:
        Dict matching the natal_chart module's output format:
        {planets, ascendant, midheaven, julian_day, coordinates,
         sun_sign, moon_sign, rising_sign, moon_nakshatra, moon_pada}
    """
    import swisseph as swe
    swe.set_ephe_path(None)

    # Parse birth time → Universal Time
    h, m = map(int, birth_time.split(":"))
    ut = (h + m / 60.0) - tz_offset
    jd_ut = swe.julday(dob.year, dob.month, dob.day, ut)

    # Compute planetary positions
    planets = {}
    for name, pid in PLANETS:
        actual_id = pid if pid != 11 else 10  # pyswisseph MEAN_NODE = 10
        result = swe.calc_ut(jd_ut, actual_id)
        longitude = result[0][0]
        sign, degree, minute = _sign_from_longitude(longitude)

        planets[name] = {
            "longitude": round(longitude, 4),
            "sign": sign,
            "degree": degree,
            "minute": minute,
            "formatted": f"{degree}\u00b0{minute:02d}' {sign}",
        }

    # Moon's nakshatra and pada
    moon_lon = planets["Moon"]["longitude"]
    nak_name, nak_pada = _nakshatra_from_longitude(moon_lon)

    # Compute Ascendant and MC (Whole Sign houses)
    cusps, asmc = swe.houses(jd_ut, lat, lng, b'W')
    asc_lon = asmc[0]
    mc_lon = asmc[1]

    asc_sign, asc_deg, asc_min = _sign_from_longitude(asc_lon)
    mc_sign, mc_deg, mc_min = _sign_from_longitude(mc_lon)

    # Ketu (South Node) = North Node + 180°
    nn_lon = planets["North Node"]["longitude"]
    ketu_lon = (nn_lon + 180.0) % 360.0
    ketu_sign, ketu_deg, ketu_min = _sign_from_longitude(ketu_lon)
    planets["South Node"] = {
        "longitude": round(ketu_lon, 4),
        "sign": ketu_sign,
        "degree": ketu_deg,
        "minute": ketu_min,
        "formatted": f"{ketu_deg}\u00b0{ketu_min:02d}' {ketu_sign}",
    }

    return {
        "planets": planets,
        "ascendant": {
            "longitude": round(asc_lon, 4),
            "sign": asc_sign,
            "degree": asc_deg,
            "minute": asc_min,
            "formatted": f"{asc_deg}\u00b0{asc_min:02d}' {asc_sign}",
        },
        "midheaven": {
            "longitude": round(mc_lon, 4),
            "sign": mc_sign,
            "degree": mc_deg,
            "minute": mc_min,
            "formatted": f"{mc_deg}\u00b0{mc_min:02d}' {mc_sign}",
        },
        "house_cusps": [round(c, 4) for c in cusps[:12]],
        "julian_day": round(jd_ut, 6),
        "coordinates": {"lat": lat, "lon": lng},
        "sun_sign": planets["Sun"]["sign"],
        "moon_sign": planets["Moon"]["sign"],
        "rising_sign": asc_sign,
        "moon_nakshatra": nak_name,
        "moon_pada": nak_pada,
    }
