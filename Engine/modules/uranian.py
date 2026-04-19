"""Uranian Astrology (Hamburg School) — 90° Dial System — COMPUTED_STRICT

The Hamburg School of Astrology (founded by Alfred Witte, 1919) uses the 90°
dial to collapse the zodiac into a single quadrant, making hard aspects
(0°/90°/180°/270°) appear as conjunctions. It adds 8 Transneptunian Points
(TNPs) — hypothetical bodies with computed orbital positions.

Algorithm:
  1. Collect classical planet longitudes + ASC/MC from natal chart
  2. Compute 8 TNP longitudes via Swiss Ephemeris (fictitious planets 40-47)
  3. Reduce all positions to 90° dial: dial90 = longitude % 90
  4. Compute all pairwise midpoints on the 90° circle
  5. Detect planetary pictures: A = B/C (midpoint of B,C within 1° of A)
  6. Rank points by participation frequency (dominance scoring)

Sources: Alfred Witte, Regelwerk für Planetenbilder (1928);
         Reinhold Ebertin, The Combination of Stellar Influences (1972);
         Swiss Ephemeris documentation (fictitious planets)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Classical planets used (Sun through Pluto + nodes not needed for Uranian)
PLANET_IDS = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4,
    "Jupiter": 5, "Saturn": 6, "Uranus": 7, "Neptune": 8, "Pluto": 9,
}

# 8 Hamburg School Transneptunian Points — Swiss Ephemeris fictitious planet IDs
TNP_IDS = {
    "Cupido": 40,    # Union, family, art, social bonds
    "Hades": 41,     # Decay, past, hidden, death
    "Zeus": 42,      # Power, conflict, dominance
    "Kronos": 43,    # Authority, structure, mastery
    "Apollon": 44,   # Expansion, inspiration, commerce
    "Admetos": 45,   # Compression, focus, ending
    "Vulkanus": 46,  # Intensity, force, eruption
    "Poseidon": 47,  # Spirituality, ideals, clarity
}

TNP_THEMES = {
    "Cupido": ["family", "union", "art"],
    "Hades": ["past", "hidden", "decay"],
    "Zeus": ["power", "conflict", "energy"],
    "Kronos": ["authority", "mastery", "elevation"],
    "Apollon": ["expansion", "success", "commerce"],
    "Admetos": ["depth", "focus", "restriction"],
    "Vulkanus": ["intensity", "force", "transformation"],
    "Poseidon": ["spirituality", "ideals", "vision"],
}

HAMBURG_ORB = 1.0  # degrees — strict Hamburg standard


def _dial90(lon: float) -> float:
    """Reduce longitude to 90° dial position."""
    return lon % 90.0


def _circular_dist_90(a: float, b: float) -> float:
    """Shortest distance on a 90° circle."""
    d = abs(a - b) % 90.0
    return min(d, 90.0 - d)


def _midpoint_90(a: float, b: float) -> float:
    """Short-arc midpoint on 90° circle."""
    diff = (b - a) % 90.0
    if diff <= 45.0:
        return (a + diff / 2.0) % 90.0
    else:
        return (a - (90.0 - diff) / 2.0) % 90.0


def _sign_from_lon(lon: float) -> str:
    return SIGNS[int(lon % 360) // 30]


def compute(profile: InputProfile, constants: dict,
            natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None or not profile.birth_time_local:
        return SystemResult(
            id="uranian", name="Uranian Astrology (Hamburg School)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data and birth time required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q1_IDENTITY",
        )

    import swisseph as swe

    TZ_OFFSETS = {
        "Asia/Riyadh": 3, "Asia/Dubai": 4, "Asia/Kuwait": 3,
        "Asia/Amman": 2, "Africa/Cairo": 2, "Asia/Beirut": 2,
        "Asia/Damascus": 2, "Asia/Baghdad": 3, "Europe/Istanbul": 3,
        "Europe/London": 0, "America/New_York": -5, "UTC": 0,
    }

    # Build JD for TNP computation
    birth = profile.dob
    h, m = map(int, profile.birth_time_local.split(":"))
    tz_offset = TZ_OFFSETS.get(profile.timezone, 3)
    hour_ut = (h + m / 60.0) - tz_offset
    jd = swe.julday(birth.year, birth.month, birth.day, hour_ut)

    # Step 1: Collect classical planet longitudes from natal_chart_data
    planets_data = natal_chart_data.get("planets", {})
    points = {}

    for name, pid in PLANET_IDS.items():
        pdata = planets_data.get(name, {})
        lon = pdata.get("longitude")
        if lon is not None:
            points[name] = {
                "longitude": round(lon, 4),
                "sign": _sign_from_lon(lon),
                "dial90": round(_dial90(lon), 4),
                "source": "classical",
            }

    # Add ASC and MC from natal chart
    for angle_name in ("ASC", "MC"):
        angle_data = natal_chart_data.get(angle_name)
        if angle_data is None:
            angle_data = natal_chart_data.get("houses", {}).get(angle_name)
        if isinstance(angle_data, dict):
            lon = angle_data.get("longitude", angle_data.get("degree"))
        elif isinstance(angle_data, (int, float)):
            lon = angle_data
        else:
            lon = None
        if lon is not None:
            points[angle_name] = {
                "longitude": round(lon, 4),
                "sign": _sign_from_lon(lon),
                "dial90": round(_dial90(lon), 4),
                "source": "angle",
            }

    # Step 2: Compute 8 TNP longitudes
    for tnp_name, tnp_id in TNP_IDS.items():
        try:
            result = swe.calc_ut(jd, tnp_id)
            lon = result[0] if isinstance(result[0], float) else result[0][0]
            points[tnp_name] = {
                "longitude": round(lon, 4),
                "sign": _sign_from_lon(lon),
                "dial90": round(_dial90(lon), 4),
                "source": "transneptunian",
            }
        except Exception:
            pass

    # Step 3: Compute all pairwise midpoints on 90° dial
    point_names = sorted(points.keys())
    midpoints = []
    for i in range(len(point_names)):
        for j in range(i + 1, len(point_names)):
            a_name = point_names[i]
            b_name = point_names[j]
            a_dial = points[a_name]["dial90"]
            b_dial = points[b_name]["dial90"]
            mp = _midpoint_90(a_dial, b_dial)
            midpoints.append({
                "point_a": a_name,
                "point_b": b_name,
                "midpoint_dial90": round(mp, 4),
            })

    # Step 4: Detect planetary pictures (A = B/C)
    # A picture exists when point A's dial90 is within orb of the midpoint of B and C
    pictures = []
    for mp in midpoints:
        mp_val = mp["midpoint_dial90"]
        for p_name in point_names:
            # Skip if p_name is one of the midpoint pair
            if p_name == mp["point_a"] or p_name == mp["point_b"]:
                continue
            p_dial = points[p_name]["dial90"]
            orb = _circular_dist_90(p_dial, mp_val)
            if orb <= HAMBURG_ORB:
                # Collect theme tags from TNPs involved
                themes = []
                for involved in (p_name, mp["point_a"], mp["point_b"]):
                    if involved in TNP_THEMES:
                        themes.extend(TNP_THEMES[involved])

                pictures.append({
                    "notation": f"{p_name}={mp['point_a']}/{mp['point_b']}",
                    "promittor": p_name,
                    "first_point": mp["point_a"],
                    "second_point": mp["point_b"],
                    "orb": round(orb, 4),
                    "theme_tags": themes if themes else ["classical"],
                })

    # Step 5: Dominance scoring — rank points by picture participation
    freq = {}
    for pic in pictures:
        for key in ("promittor", "first_point", "second_point"):
            name = pic[key]
            freq[name] = freq.get(name, 0) + 1

    dominance = sorted(
        [{"point": k, "frequency": v, "rank": 0} for k, v in freq.items()],
        key=lambda x: -x["frequency"],
    )
    for i, d in enumerate(dominance):
        d["rank"] = i + 1

    # Determine dominant point
    dominant_point = dominance[0]["point"] if dominance else "None"

    data = {
        "method": "hamburg_90dial_v1",
        "point_count": len(points),
        "tnp_count": sum(1 for p in points.values() if p["source"] == "transneptunian"),
        "midpoint_count": len(midpoints),
        "picture_count": len(pictures),
        "dominant_point": dominant_point,
        "points": points,
        "planetary_pictures": pictures[:50],  # Cap for output size
        "dominance": dominance[:10],  # Top 10
    }

    return SystemResult(
        id="uranian",
        name="Uranian Astrology (Hamburg School)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Alfred Witte, Regelwerk für Planetenbilder (1928)",
            "Reinhold Ebertin, The Combination of Stellar Influences (1972)",
            "Swiss Ephemeris documentation — fictitious/transneptunian planets",
        ],
        question="Q1_IDENTITY",
    )
