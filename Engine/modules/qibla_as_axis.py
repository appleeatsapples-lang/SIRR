"""Qibla as Axis — Directional Computation — COMPUTED_STRICT
Computes the qibla direction from birth location and derives
the perpendicular axis as a structural compass signature.
"""
from __future__ import annotations
import math
from sirr_core.types import InputProfile, SystemResult

# Mecca coordinates
MECCA_LAT = 21.4225
MECCA_LON = 39.8262

# Default: Cairo, Egypt
DEFAULT_LAT = 26.2361
DEFAULT_LON = 50.0393

CARDINAL_DIRECTIONS = [
    (0, "N"), (45, "NE"), (90, "E"), (135, "SE"),
    (180, "S"), (225, "SW"), (270, "W"), (315, "NW"), (360, "N")
]


def _qibla_bearing(lat: float, lon: float) -> float:
    """Compute initial bearing from (lat, lon) to Mecca using great circle."""
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    lat2 = math.radians(MECCA_LAT)
    lon2 = math.radians(MECCA_LON)

    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    bearing = math.degrees(math.atan2(x, y))
    return bearing % 360


def _nearest_cardinal(angle: float) -> str:
    for i in range(len(CARDINAL_DIRECTIONS) - 1):
        a1 = CARDINAL_DIRECTIONS[i][0]
        a2 = CARDINAL_DIRECTIONS[i + 1][0]
        if a1 <= angle < a2:
            if angle - a1 < a2 - angle:
                return CARDINAL_DIRECTIONS[i][1]
            else:
                return CARDINAL_DIRECTIONS[i + 1][1]
    return "N"


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    lat = profile.latitude or DEFAULT_LAT
    lon = profile.longitude or DEFAULT_LON

    qibla_angle = round(_qibla_bearing(lat, lon), 1)
    cardinal = _nearest_cardinal(qibla_angle)
    perpendicular = round((qibla_angle + 90) % 360, 1)
    perpendicular_cardinal = _nearest_cardinal(perpendicular)
    anti_qibla = round((qibla_angle + 180) % 360, 1)

    # Distance to Mecca (haversine, km)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    lat2 = math.radians(MECCA_LAT)
    lon2 = math.radians(MECCA_LON)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = round(6371 * c, 1)

    return SystemResult(
        id="qibla_as_axis",
        name="Qibla as Axis (القبلة كمحور)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "birth_lat": lat,
            "birth_lon": lon,
            "qibla_angle": qibla_angle,
            "qibla_cardinal": cardinal,
            "perpendicular_angle": perpendicular,
            "perpendicular_cardinal": perpendicular_cardinal,
            "anti_qibla_angle": anti_qibla,
            "distance_to_mecca_km": distance_km,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Great circle bearing to Mecca (21.4225°N, 39.8262°E)"],
        question="Q3_NATURE"
    )
