"""Harmonic Charts — COMPUTED_STRICT
Computes harmonic charts by multiplying all natal positions by N (mod 360).
Standard harmonics analyzed:
  H4 — squares and oppositions (tension, effort)
  H5 — quintiles (creative talent, unique ability)
  H7 — septiles (inspiration, fate, mystical)
  H9 — novile/navamsha (spiritual completion, Vedic D9)

For each harmonic, finds tight conjunctions (orb <= 8°) between planets,
revealing hidden chart patterns invisible in the radix.

Sources: John Addey (Harmonics in Astrology),
         David Hamblin (Harmonic Charts)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

HARMONICS = [4, 5, 7, 9]
CONJUNCTION_ORB = 8.0  # Wider orb in harmonic charts (Addey standard)

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _angular_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="harmonic_charts", name="Harmonic Charts",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    planets = natal_chart_data.get("planets", {})

    harmonics_data = {}
    total_conjunctions = 0

    for h in HARMONICS:
        # Compute harmonic positions
        h_positions = {}
        for name, pdata in planets.items():
            h_lon = (pdata["longitude"] * h) % 360
            sign_idx = int(h_lon // 30) % 12
            h_positions[name] = {
                "longitude": round(h_lon, 2),
                "sign": SIGNS[sign_idx],
                "degree": int(h_lon % 30),
            }

        # Find conjunctions in this harmonic
        names = list(h_positions.keys())
        conjunctions = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                orb = _angular_diff(
                    h_positions[names[i]]["longitude"],
                    h_positions[names[j]]["longitude"]
                )
                if orb <= CONJUNCTION_ORB:
                    conjunctions.append({
                        "pair": [names[i], names[j]],
                        "orb": round(orb, 2),
                    })

        conjunctions.sort(key=lambda x: x["orb"])
        total_conjunctions += len(conjunctions)

        harmonics_data[f"H{h}"] = {
            "harmonic": h,
            "conjunction_count": len(conjunctions),
            "conjunctions": conjunctions[:10],
        }

    data = {
        "harmonics": harmonics_data,
        "total_conjunction_count": total_conjunctions,
    }

    return SystemResult(
        id="harmonic_charts",
        name="Harmonic Charts",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "John Addey, Harmonics in Astrology",
            "David Hamblin, Harmonic Charts",
        ],
        question="Q3_NATURE",
    )
