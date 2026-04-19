"""
Kala Sarpa Yoga Check (कालसर्प योग)
──────────────────────────────────────
Determines whether all seven classical planets are hemmed between
Rahu and Ketu in the natal chart.

Algorithm (from vedic_lookups.json / BPHS Ch. 3):
  1. Get ecliptic longitude of all 7 classical planets + Rahu + Ketu
  2. Compute the Rahu→Ketu arc (going forward in longitude)
  3. Check if ALL classical planets fall within that arc
  4. If yes → Kala Sarpa Yoga present; identify type (anuloma/viloma)

Source: Brihat Parashara Hora Shastra; Phaladeepika
SOURCE_TIER: B (classical Vedic, widely accepted in Jyotish)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# 12 types of KSY based on Rahu's house position
KSY_TYPES = {
    1: "Ananta", 2: "Kulika", 3: "Vasuki", 4: "Shankhapala",
    5: "Padma", 6: "Maha Padma", 7: "Takshaka", 8: "Karkotaka",
    9: "Shankhachuda", 10: "Ghataka", 11: "Vishdhara", 12: "Sheshnag",
}


def _normalize(lon: float) -> float:
    """Normalize longitude to [0, 360)."""
    return lon % 360.0


def _in_arc(planet_lon: float, rahu_lon: float, ketu_lon: float) -> bool:
    """Check if planet is in the Rahu→Ketu forward arc."""
    r = _normalize(rahu_lon)
    k = _normalize(ketu_lon)
    p = _normalize(planet_lon)
    if r < k:
        return r <= p <= k
    else:  # arc wraps around 360
        return p >= r or p <= k


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal = kwargs.get("natal_chart_data")
    if not natal or "planets" not in natal:
        return SystemResult(
            id="kala_sarpa_check",
            name="Kala Sarpa Yoga Check",
            certainty="NEEDS_EPHEMERIS",
            data={"ksy_present": None, "reason": "No natal chart data"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["BPHS Ch. 3"],
            question="Q1_IDENTITY",
        )

    planets = natal["planets"]

    # Extract Rahu and Ketu longitudes
    rahu_lon = None
    ketu_lon = None
    classical = {}  # Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
    CLASSICAL_NAMES = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}

    for name, info in planets.items():
        lon = info if isinstance(info, (int, float)) else info.get("longitude", info.get("lon"))
        if lon is None:
            continue
        if name in ("Rahu", "mean_node", "North Node"):
            rahu_lon = float(lon)
        elif name in ("Ketu", "South Node"):
            ketu_lon = float(lon)
        elif name in CLASSICAL_NAMES:
            classical[name] = float(lon)

    # Ketu is always 180° from Rahu (mean nodes)
    if rahu_lon is not None and ketu_lon is None:
        ketu_lon = _normalize(rahu_lon + 180.0)
    if ketu_lon is not None and rahu_lon is None:
        rahu_lon = _normalize(ketu_lon + 180.0)

    if rahu_lon is None or len(classical) < 7:
        return SystemResult(
            id="kala_sarpa_check",
            name="Kala Sarpa Yoga Check",
            certainty="NEEDS_EPHEMERIS",
            data={"ksy_present": None, "reason": "Missing planet data"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["BPHS Ch. 3"],
            question="Q1_IDENTITY",
        )

    # Check if all 7 classical planets are between Rahu and Ketu
    all_in_rahu_ketu_arc = all(
        _in_arc(lon, rahu_lon, ketu_lon) for lon in classical.values()
    )
    # Also check reverse (Ketu→Rahu) — determines anuloma vs viloma
    all_in_ketu_rahu_arc = all(
        _in_arc(lon, ketu_lon, rahu_lon) for lon in classical.values()
    )

    ksy_present = all_in_rahu_ketu_arc or all_in_ketu_rahu_arc
    direction = None
    if all_in_rahu_ketu_arc:
        direction = "anuloma"  # Rahu leading (forward KSY)
    elif all_in_ketu_rahu_arc:
        direction = "viloma"  # Ketu leading (reverse KSY)

    # Determine KSY type from Rahu's house (approximate from longitude)
    rahu_house = int(rahu_lon / 30.0) + 1
    ksy_type = KSY_TYPES.get(rahu_house, "Unknown") if ksy_present else None

    # Count planets in each half
    in_rahu_arc = sum(1 for lon in classical.values() if _in_arc(lon, rahu_lon, ketu_lon))
    in_ketu_arc = 7 - in_rahu_arc

    # Partial KSY check (6 of 7 planets hemmed = "partial" in some traditions)
    partial = not ksy_present and (in_rahu_arc >= 6 or in_ketu_arc >= 6)

    return SystemResult(
        id="kala_sarpa_check",
        name="Kala Sarpa Yoga Check",
        certainty="COMPUTED_STRICT",
        data={
            "ksy_present": ksy_present,
            "direction": direction,
            "ksy_type": ksy_type,
            "rahu_longitude": round(rahu_lon, 4),
            "ketu_longitude": round(ketu_lon, 4),
            "rahu_house": rahu_house,
            "planets_in_rahu_arc": in_rahu_arc,
            "planets_in_ketu_arc": in_ketu_arc,
            "partial_ksy": partial,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Brihat Parashara Hora Shastra", "Phaladeepika"],
        question="Q1_IDENTITY",
    )
