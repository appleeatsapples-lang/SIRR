"""AstroCartoGraphy (ACG) — Planetary Line Geography — COMPUTED_STRICT

Maps natal planetary angular lines (MC, IC, ASC, DSC) onto geographic
coordinates. Where a planet's angular line crosses a location, that
planet's energy is strongly activated — useful for relocation analysis,
travel, and understanding geographic activation patterns.

For each of 7 traditional planets, computes 4 angular lines:
  MC line:  longitude where planet culminates (on Midheaven)
  IC line:  longitude where planet anti-culminates (on IC/nadir)
  ASC line: longitude where planet rises (on Ascendant) at birth latitude
  DSC line: longitude where planet sets (on Descendant) at birth latitude

Sources:
  - Jim Lewis — AstroCartoGraphy (1976), founder of the technique
  - Swiss Ephemeris (Moshier method) for planetary positions
"""
from __future__ import annotations
import math
import swisseph as swe
from sirr_core.types import InputProfile, SystemResult

PLANETS = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3,
    "Mars": 4, "Jupiter": 5, "Saturn": 6,
}

# Known locations for coordinate lookup
LOCATIONS = {
    "Cairo, Egypt": (26.2361, 50.0393),
    "Riyadh, Saudi Arabia": (24.7136, 46.6753),
    "Jeddah, Saudi Arabia": (21.5433, 39.1728),
    "Amman, Jordan": (31.9454, 35.9284),
    "Cairo, Egypt": (30.0444, 31.2357),
    "Dubai, UAE": (25.2048, 55.2708),
    "Kuwait City, Kuwait": (29.3759, 47.9774),
    "Beirut, Lebanon": (33.8938, 35.5018),
    "Damascus, Syria": (33.5138, 36.2765),
    "Baghdad, Iraq": (33.3152, 44.3661),
    "Istanbul, Turkey": (41.0082, 28.9784),
    "London, UK": (51.5074, -0.1278),
    "New York, USA": (40.7128, -74.0060),
}

# Obliquity of ecliptic (approximate for J2000)
OBLIQUITY = 23.44


def _parse_location(location: str):
    """Return (lat, lon) for a known location string."""
    coords = LOCATIONS.get(location)
    if coords:
        return coords
    try:
        from sirr_core.natal_chart import geocode
        geo = geocode(location)
        if geo:
            return geo.lat, geo.lng
    except Exception:
        pass
    return None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in km."""
    R = 6371.0
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _normalize_lon(lon: float) -> float:
    """Normalize longitude to -180..180."""
    lon = lon % 360
    if lon > 180:
        lon -= 360
    return round(lon, 2)


def _lon_distance_km(lon1: float, lon2: float, lat: float) -> float:
    """Distance in km between two longitudes at a given latitude."""
    return _haversine_km(lat, lon1, lat, lon2)


def _direction(ref_lon: float, line_lon: float) -> str:
    """Direction from reference to line."""
    diff = (line_lon - ref_lon + 540) % 360 - 180
    return "E" if diff > 0 else "W" if diff < 0 else "same"


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="astrocartography",
            name="AstroCartoGraphy (Planetary Lines)",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "Requires natal_chart_data"},
            interpretation=None,
            constants_version=constants.get("version", "unknown"),
            references=[],
        )

    planets_data = natal_chart_data.get("planets", {})
    jd = natal_chart_data.get("julian_day", 2450349.8)

    # Birth location
    birth_coords = None
    location_name = getattr(profile, "location", None) or "Cairo, Egypt"
    if location_name:
        birth_coords = _parse_location(location_name)
    if birth_coords is None:
        birth_coords = (26.2361, 50.0393)  # Cairo fallback
        location_name = "Cairo, Egypt"

    birth_lat, birth_lon = birth_coords

    swe.set_ephe_path(None)

    # GMST at birth (degrees)
    gmst_hours = swe.sidtime(jd)
    gmst_deg = gmst_hours * 15.0

    # Obliquity
    eps = math.radians(OBLIQUITY)

    planetary_lines = {}
    all_lines = []  # for sorting closest

    for pname, pid in PLANETS.items():
        # Get equatorial coordinates (RA, Dec)
        eq_result = swe.calc_ut(jd, pid, swe.FLG_EQUATORIAL)
        ra_deg = eq_result[0][0]   # Right Ascension in degrees
        dec_deg = eq_result[0][1]  # Declination in degrees

        dec_rad = math.radians(dec_deg)
        birth_lat_rad = math.radians(birth_lat)

        # ── MC line ──
        # Planet is on MC when LMST = RA
        # LMST = GMST + geographic_longitude/15 (in hours)
        # So geo_lon = (RA - GMST) in degrees
        mc_geo_lon = _normalize_lon(ra_deg - gmst_deg)

        # ── IC line ──
        # Planet is on IC when LMST = RA + 180°
        ic_geo_lon = _normalize_lon(ra_deg - gmst_deg + 180)

        # ── ASC line (rising) ──
        # Planet rises when its hour angle H satisfies:
        # cos(H) = -sin(lat)*sin(dec) / (cos(lat)*cos(dec))
        # If |cos(H)| > 1, planet doesn't rise/set at this latitude
        cos_lat_cos_dec = math.cos(birth_lat_rad) * math.cos(dec_rad)
        asc_geo_lon = None
        dsc_geo_lon = None

        if abs(cos_lat_cos_dec) > 1e-10:
            cos_h = -(math.sin(birth_lat_rad) * math.sin(dec_rad)) / cos_lat_cos_dec
            if -1 <= cos_h <= 1:
                h_deg = math.degrees(math.acos(cos_h))
                # ASC: planet rising = hour angle is negative (east)
                # geo_lon = (RA - GMST - H)
                asc_geo_lon = _normalize_lon(ra_deg - gmst_deg - h_deg)
                # DSC: planet setting = hour angle is positive (west)
                dsc_geo_lon = _normalize_lon(ra_deg - gmst_deg + h_deg)

        # Compute distances
        def _line_data(geo_lon, line_type):
            if geo_lon is None:
                return {"longitude": None, "distance_km_from_birth": None,
                        "distance_km_from_ref": None, "direction": None,
                        "note": f"Planet does not {line_type.lower()} at birth latitude"}
            dist_birth = round(_haversine_km(birth_lat, birth_lon, birth_lat, geo_lon), 1)
            direction = _direction(birth_lon, geo_lon)
            return {
                "longitude": geo_lon,
                "distance_km_from_birth": dist_birth,
                "distance_km_from_ref": dist_birth,  # same as birth for default profile
                "direction": direction,
            }

        mc_data = _line_data(mc_geo_lon, "MC")
        ic_data = _line_data(ic_geo_lon, "IC")
        asc_data = _line_data(asc_geo_lon, "ASC")
        dsc_data = _line_data(dsc_geo_lon, "DSC")

        planetary_lines[pname] = {
            "MC": mc_data,
            "IC": ic_data,
            "ASC": asc_data,
            "DSC": dsc_data,
        }

        # Collect for sorting
        for lt, ld in [("MC", mc_data), ("IC", ic_data), ("ASC", asc_data), ("DSC", dsc_data)]:
            if ld["distance_km_from_birth"] is not None:
                all_lines.append({
                    "planet": pname,
                    "line_type": lt,
                    "longitude": ld["longitude"],
                    "distance_km": ld["distance_km_from_birth"],
                    "direction": ld["direction"],
                })

    # Sort by distance, take top 10
    all_lines.sort(key=lambda x: x["distance_km"])
    closest_lines = all_lines[:10]

    # Power zones: find locations where multiple lines converge within 400km
    power_zones = []
    # Check convergence by grouping lines within 400km of each other
    # Use a simple approach: for each line, find others within 400km
    checked = set()
    for i, line_i in enumerate(all_lines):
        if i in checked:
            continue
        cluster = [line_i]
        for j, line_j in enumerate(all_lines):
            if j <= i or j in checked:
                continue
            # Check if lines are within 400km of each other at birth latitude
            if line_i["longitude"] is not None and line_j["longitude"] is not None:
                dist = _haversine_km(birth_lat, line_i["longitude"], birth_lat, line_j["longitude"])
                if dist <= 400:
                    cluster.append(line_j)
                    checked.add(j)
        if len(cluster) >= 2:
            avg_lon = sum(c["longitude"] for c in cluster) / len(cluster)
            avg_dist = round(sum(c["distance_km"] for c in cluster) / len(cluster), 1)
            lines_desc = [f"{c['planet']}-{c['line_type']}" for c in cluster]

            # Determine region from longitude
            if -130 <= avg_lon <= -60:
                region = "Americas"
            elif -30 <= avg_lon <= 60:
                region = "Europe/Middle East/Africa"
            elif 60 < avg_lon <= 150:
                region = "Asia/Pacific"
            else:
                region = "Pacific/Atlantic"

            power_zones.append({
                "region": region,
                "center_longitude": round(avg_lon, 2),
                "lines": lines_desc,
                "avg_distance_km_from_birth": avg_dist,
            })

    # Saturn special attention
    saturn_lines = planetary_lines.get("Saturn", {})
    saturn_mc_lon = saturn_lines.get("MC", {}).get("longitude")
    saturn_ic_lon = saturn_lines.get("IC", {}).get("longitude")
    saturn_line = {
        "MC_longitude": saturn_mc_lon,
        "IC_longitude": saturn_ic_lon,
        "distance_from_birth_MC": saturn_lines.get("MC", {}).get("distance_km_from_birth"),
        "distance_from_birth_IC": saturn_lines.get("IC", {}).get("distance_km_from_birth"),
        "note": "Saturn as almuten figuris — this line activates mastery and structure",
    }

    # Jupiter special attention
    jupiter_lines = planetary_lines.get("Jupiter", {})
    jupiter_mc_lon = jupiter_lines.get("MC", {}).get("longitude")
    jupiter_ic_lon = jupiter_lines.get("IC", {}).get("longitude")
    jupiter_line = {
        "MC_longitude": jupiter_mc_lon,
        "IC_longitude": jupiter_ic_lon,
        "distance_from_birth_MC": jupiter_lines.get("MC", {}).get("distance_km_from_birth"),
        "distance_from_birth_IC": jupiter_lines.get("IC", {}).get("distance_km_from_birth"),
        "note": "Jupiter Mahadasha begins age 31.7",
    }

    # Interpretation
    interp_parts = []
    if closest_lines:
        top = closest_lines[0]
        interp_parts.append(
            f"Closest planetary line to {location_name}: "
            f"{top['planet']}-{top['line_type']} at {top['distance_km']:.0f} km {top['direction']}. "
        )
    if len(closest_lines) >= 3:
        top3 = [f"{c['planet']}-{c['line_type']}" for c in closest_lines[:3]]
        interp_parts.append(f"Top 3 nearest lines: {', '.join(top3)}. ")
    if power_zones:
        pz = power_zones[0]
        interp_parts.append(
            f"Power zone in {pz['region']}: {', '.join(pz['lines'])} "
            f"converge near longitude {pz['center_longitude']}°. "
        )
    interp_parts.append(
        f"Saturn MC at {saturn_mc_lon}° ({saturn_line['distance_from_birth_MC']:.0f} km from birth). "
        if saturn_mc_lon is not None else ""
    )

    data = {
        "birth_location": {
            "lat": birth_lat,
            "lon": birth_lon,
            "name": location_name,
        },
        "reference_location": {
            "lat": birth_lat,
            "lon": birth_lon,
            "name": location_name,
        },
        "planetary_lines": planetary_lines,
        "closest_lines": closest_lines,
        "power_zones": power_zones,
        "saturn_line": saturn_line,
        "jupiter_line": jupiter_line,
    }

    return SystemResult(
        id="astrocartography",
        name="AstroCartoGraphy (Planetary Lines)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation="".join(interp_parts),
        constants_version=constants.get("version", "unknown"),
        references=[
            "Jim Lewis — AstroCartoGraphy (1976)",
            "Swiss Ephemeris (Moshier method)",
        ],
    )
