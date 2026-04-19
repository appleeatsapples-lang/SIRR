"""Sudarshana Chakra (सुदर्शन चक्र) — Triple Wheel of Time — COMPUTED_STRICT

Constructs three concentric zodiacal wheels:
  - Lagna (Ascendant) wheel  → body / material circumstances
  - Sun wheel                → soul / authority / vitality
  - Moon wheel               → mind / emotions / public life

All three wheels advance at exactly 1 sign per completed year of life.
The active sign in each wheel determines which natal planets are "activated"
for that year, creating a multi-perspective annual forecast.

Key insight: because all wheels advance at the same rate, the angular
separation between them NEVER changes. "Triple activation" (all three
wheels on the same sign) only occurs if the native's Lagna, Sun, and
Moon are all in the same sidereal sign — otherwise it is geometrically
impossible.

Micro-periods (Sudarshana Antardasha): each year is subdivided into 12
sub-periods of ~30.44 days, one per house from the year's active house.

Uses sidereal (Lahiri ayanamsha) positions.

Input:  natal_chart_data (tropical planet longitudes + ascendant), profile (DOB)
Output: Three-wheel annual map with activated signs, resident planets,
        micro-period schedule, and triple-activation flag.

Source: Brihat Parashara Hora Shastra (BPHS), Chapter 74
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Classical 7 planets used in Vedic Jyotish
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# Wheel labels and their interpretive domains
WHEEL_KEYS = [
    ("lagna", "body/material"),
    ("sun",   "soul/authority"),
    ("moon",  "mind/emotions"),
]


def compute(
    profile: InputProfile,
    constants: dict,
    natal_chart_data: dict = None,
    **kwargs,
) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="sudarshana",
            name="Sudarshana Chakra (Triple Wheel of Time)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    jd_ut = natal_chart_data.get("julian_day")
    if jd_ut is None:
        return SystemResult(
            id="sudarshana",
            name="Sudarshana Chakra (Triple Wheel of Time)",
            certainty="NEEDS_INPUT",
            data={"error": "julian_day not in natal_chart_data"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q4_TIMING",
        )

    # --- Compute sidereal positions via Lahiri ayanamsha ---
    import swisseph as swe
    swe.set_ephe_path(None)
    ayanamsha = swe.get_ayanamsa_ut(jd_ut)

    # Sidereal sign indices for all classical planets
    sid_signs = {}
    for name in PLANETS:
        trop_lon = natal_chart_data["planets"][name]["longitude"]
        sid_lon = (trop_lon - ayanamsha) % 360
        sid_signs[name] = int(sid_lon // 30) % 12

    # Sidereal Ascendant sign index
    asc_trop_lon = natal_chart_data["ascendant"]["longitude"]
    asc_sid_lon = (asc_trop_lon - ayanamsha) % 360
    asc_sid_idx = int(asc_sid_lon // 30) % 12

    # --- Wheel starting signs (sidereal) ---
    wheel_starts = {
        "lagna": asc_sid_idx,
        "sun":   sid_signs["Sun"],
        "moon":  sid_signs["Moon"],
    }

    # --- Completed age ---
    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1
    if age < 0:
        age = 0

    # Active house number (1-12), same for all wheels
    active_house = (age % 12) + 1

    # --- Build each wheel's active sign and resident planets ---
    wheels = {}
    active_sign_indices = {}
    for wheel_key, domain in WHEEL_KEYS:
        start_idx = wheel_starts[wheel_key]
        active_idx = (start_idx + age) % 12
        active_sign_indices[wheel_key] = active_idx

        # Find natal planets residing in the active sign
        resident_planets = [
            p for p in PLANETS if sid_signs[p] == active_idx
        ]

        wheels[wheel_key] = {
            "start_sign": SIGNS[start_idx],
            "active_sign": SIGNS[active_idx],
            "active_sign_index": active_idx,
            "domain": domain,
            "resident_planets": resident_planets,
            "planet_count": len(resident_planets),
        }

    # --- Triple activation check ---
    unique_active = set(active_sign_indices.values())
    triple_activation = len(unique_active) == 1
    # This can only be True if Lagna, Sun, and Moon are all in the same
    # sidereal sign natally (they maintain fixed separation forever)
    natal_triple_conjunction = (
        asc_sid_idx == sid_signs["Sun"] == sid_signs["Moon"]
    )

    # --- Micro-periods (Sudarshana Antardasha) ---
    # Each year subdivided into 12 periods of ~30.44 days
    # Starting from the active house, advancing 1 house per period
    micro_periods = []
    for i in range(12):
        for wheel_key, _ in WHEEL_KEYS:
            start_idx = wheel_starts[wheel_key]
            break  # Use lagna wheel for micro-period sequence
        micro_sign_idx = (active_sign_indices["lagna"] + i) % 12
        micro_periods.append({
            "period": i + 1,
            "sign": SIGNS[micro_sign_idx],
            "approximate_days": round(365.25 / 12, 1),
        })

    # --- Year quality assessment ---
    # Count total activated planets across all three wheels
    all_activated = set()
    for w in wheels.values():
        all_activated.update(w["resident_planets"])

    benefics_activated = [
        p for p in all_activated if p in ("Jupiter", "Venus", "Moon", "Mercury")
    ]
    malefics_activated = [
        p for p in all_activated if p in ("Saturn", "Mars", "Sun")
    ]

    # --- Assemble output ---
    data = {
        "ayanamsha": round(ayanamsha, 4),
        "completed_years": age,
        "active_house": active_house,
        "cycle_position": f"Year {active_house} of 12",
        "wheels": wheels,
        "triple_activation": triple_activation,
        "natal_triple_conjunction": natal_triple_conjunction,
        "micro_periods": micro_periods,
        "total_activated_planets": sorted(all_activated),
        "benefics_activated": sorted(benefics_activated),
        "malefics_activated": sorted(malefics_activated),
        "year_quality": (
            "strongly_benefic" if len(benefics_activated) >= 3 else
            "benefic" if len(benefics_activated) > len(malefics_activated) else
            "malefic" if len(malefics_activated) > len(benefics_activated) else
            "mixed" if all_activated else
            "neutral"
        ),
    }

    return SystemResult(
        id="sudarshana",
        name="Sudarshana Chakra (Triple Wheel of Time)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Brihat Parashara Hora Shastra (BPHS), Chapter 74",
            "Lahiri ayanamsha (Swiss Ephemeris)",
        ],
        question="Q4_TIMING",
    )
