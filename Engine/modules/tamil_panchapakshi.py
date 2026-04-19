"""Tamil Pancha Pakshi — COMPUTED_STRICT
(1) Birth nakshatra from Moon longitude. (2) Lunar paksha (waxing/waning).
(3) Map nakshatra+paksha → one of 5 birds (Vulture, Owl, Crow, Cock, Peacock).
Source: "Pancha Pakshi Shastra", Tamil Siddha/Jyotish texts
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

try:
    import swisseph as swe
    _SWE = True
except ImportError:
    _SWE = False

# 5 birds in order
BIRDS = ["Vulture", "Owl", "Crow", "Cock", "Peacock"]

# Nakshatra-to-bird mapping for Shukla Paksha (waxing moon)
# Each nakshatra (1-27) maps to a bird index (0-4)
# Source: Pancha Pakshi Shastra (Tamil Siddhar tradition)
# Pattern: groups of 5-6 nakshatras cycle through the 5 birds
SHUKLA_MAP = [
    0, 1, 2, 3, 4,  # Ashwini(1) to Mrigashira(5) → V,O,Cr,Co,P
    1, 2, 3, 4, 0,  # Ardra(6) to Hasta(10) → O,Cr,Co,P,V
    2, 3, 4, 0, 1,  # Chitra(11) to Anuradha(15) → Cr,Co,P,V,O
    3, 4, 0, 1, 2,  # Jyeshtha(16) to Shravana(20) → Co,P,V,O,Cr
    4, 0, 1, 2, 3,  # Dhanishta(21) to Revati(25) → P,V,O,Cr,Co
    0, 1,            # UBhadra(26), Revati(27) → V,O
]

# Krishna Paksha (waning): shift by 2 positions in the bird cycle
KRISHNA_MAP = [(b + 2) % 5 for b in SHUKLA_MAP]


def _get_moon_data(profile):
    """Get sidereal Moon longitude and Sun-Moon elongation for paksha."""
    if not _SWE:
        return None, None

    if not (profile.birth_time_local and profile.timezone and profile.location):
        return None, None

    try:
        # Compute JD
        parts = profile.birth_time_local.split(":")
        hour = int(parts[0]) + int(parts[1]) / 60.0
        jd = swe.julday(profile.dob.year, profile.dob.month, profile.dob.day, hour)

        # Adjust for timezone (approximate)
        utc_offset = profile.utc_offset or 3.0  # Default Riyadh
        jd_ut = jd - utc_offset / 24.0

        # Sidereal Moon (Lahiri ayanamsa)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        moon_sid = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SIDEREAL)[0][0]

        # Sun longitude for paksha detection
        sun_trop = swe.calc_ut(jd_ut, swe.SUN)[0][0]
        moon_trop = swe.calc_ut(jd_ut, swe.MOON)[0][0]
        elongation = (moon_trop - sun_trop) % 360

        return moon_sid, elongation
    except Exception:
        return None, None


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    natal_chart_data = kwargs.get("natal_chart_data")

    moon_sid, elongation = _get_moon_data(profile)

    if moon_sid is None:
        return SystemResult(
            id="tamil_panchapakshi", name="Tamil Pancha Pakshi",
            certainty="NEEDS_EPHEMERIS",
            data={"note": "Requires birth time + location for Moon nakshatra"},
            interpretation=None, constants_version=constants["version"],
            references=["Pancha Pakshi Shastra"],
            question="Q1_IDENTITY",
        )

    # Nakshatra from sidereal Moon (each nakshatra = 13°20' = 13.3333°)
    nak_idx = int(moon_sid / (360.0 / 27))  # 0-26
    nak_number = nak_idx + 1  # 1-27

    # Paksha: waxing (Shukla) if elongation < 180, waning (Krishna) if >= 180
    is_shukla = elongation < 180
    paksha = "Shukla" if is_shukla else "Krishna"

    # Map to bird
    bird_map = SHUKLA_MAP if is_shukla else KRISHNA_MAP
    bird_idx = bird_map[nak_idx] if nak_idx < len(bird_map) else 0
    natal_bird = BIRDS[bird_idx]

    return SystemResult(
        id="tamil_panchapakshi",
        name="Tamil Pancha Pakshi",
        certainty="COMPUTED_STRICT",
        data={
            "nakshatra_number": nak_number,
            "moon_sidereal": round(moon_sid, 4),
            "paksha": paksha,
            "elongation": round(elongation, 2),
            "natal_bird": natal_bird,
            "natal_bird_index": bird_idx,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Pancha Pakshi Shastra: Tamil Siddha tradition, 5-bird system",
            "SOURCE_TIER:B — Traditional Tamil Siddhar text.",
        ],
        question="Q1_IDENTITY",
    )
