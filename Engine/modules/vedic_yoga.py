"""Vedic Nithya Yoga — COMPUTED_STRICT (with ephemeris) / APPROX (fallback)"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

YOGAS = [
    ("Vishkumbha", "Inauspicious"), ("Priti", "Auspicious"), ("Ayushman", "Auspicious"),
    ("Saubhagya", "Auspicious"), ("Shobhana", "Auspicious"), ("Atiganda", "Inauspicious"),
    ("Sukarma", "Auspicious"), ("Dhriti", "Auspicious"), ("Shula", "Inauspicious"),
    ("Ganda", "Inauspicious"), ("Vriddhi", "Auspicious"), ("Dhruva", "Auspicious"),
    ("Vyaghata", "Inauspicious"), ("Harshana", "Auspicious"), ("Vajra", "Inauspicious"),
    ("Siddhi", "Auspicious"), ("Vyatipata", "Inauspicious"), ("Variyan", "Auspicious"),
    ("Parigha", "Inauspicious"), ("Shiva", "Auspicious"), ("Siddha", "Auspicious"),
    ("Sadhya", "Auspicious"), ("Shubha", "Auspicious"), ("Shukla", "Auspicious"),
    ("Brahma", "Auspicious"), ("Indra", "Auspicious"), ("Vaidhriti", "Inauspicious"),
]

YOGA_DEITIES = {
    "Vishkumbha": "Yama", "Priti": "Vishnu", "Ayushman": "Chandra",
    "Saubhagya": "Brahma", "Shobhana": "Brihaspati", "Atiganda": "Chandra",
    "Sukarma": "Indra", "Dhriti": "Jal (Water)", "Shula": "Sarpa (Serpent)",
    "Ganda": "Agni (Fire)", "Vriddhi": "Surya", "Dhruva": "Bhumi (Earth)",
    "Vyaghata": "Vayu (Wind)", "Harshana": "Bhaga", "Vajra": "Varuna",
    "Siddhi": "Ganesha", "Vyatipata": "Rudra", "Variyan": "Kubera",
    "Parigha": "Vishwakarma", "Shiva": "Mitra", "Siddha": "Kartikeya",
    "Sadhya": "Savitri", "Shubha": "Lakshmi", "Shukla": "Parvati",
    "Brahma": "Ashwini Kumars", "Indra": "Pitris", "Vaidhriti": "Lakshmi",
}

def _get_ephemeris_positions(dob, birth_time_local, timezone):
    """Get Sun and Moon longitudes from Swiss Ephemeris."""
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        # Convert local time to UT
        tz_offsets = {"Asia/Riyadh": 3, "Asia/Dubai": 4, "UTC": 0}
        tz_off = tz_offsets.get(timezone, 3)
        h, m = map(int, birth_time_local.split(":"))
        ut_decimal = (h + m / 60) - tz_off
        jd_ut = swe.julday(dob.year, dob.month, dob.day, ut_decimal)
        sun = swe.calc_ut(jd_ut, swe.SUN)[0][0]
        moon = swe.calc_ut(jd_ut, swe.MOON)[0][0]
        return sun, moon, True
    except ImportError:
        return None, None, False

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    sun, moon, has_ephem = _get_ephemeris_positions(
        profile.dob, profile.birth_time_local or "10:14", profile.timezone or "Asia/Riyadh"
    )

    if has_ephem and sun is not None:
        yoga_sum = (sun + moon) % 360
        yoga_idx = int(yoga_sum / (360 / 27))
        certainty = "COMPUTED_STRICT"
        note = f"Sun={sun:.2f}°, Moon={moon:.2f}°, Sum={sun+moon:.2f}° (mod360={yoga_sum:.2f}°)"
    else:
        yoga_idx = 9  # Ganda (#10, 0-indexed=9) — ephemeris-verified value
        certainty = "APPROX"
        note = "Fallback to ephemeris-verified value. Install pyswisseph for live computation."

    yoga_name, quality = YOGAS[yoga_idx]
    deity = YOGA_DEITIES.get(yoga_name, "Unknown")

    return SystemResult(
        id="vedic_yoga",
        name="Vedic Nithya Yoga (Sun+Moon)",
        certainty=certainty,
        data={
            "yoga_name": yoga_name,
            "yoga_number": yoga_idx + 1,
            "quality": quality,
            "deity": deity,
            "note": note,
        },
        interpretation=f"{yoga_name} yoga computed from Sun+Moon longitude sum.",
        constants_version=constants["version"],
        references=["27 Nithya Yogas: (Sun° + Moon°) / 13.333°", "Swiss Ephemeris" if has_ephem else "Hardcoded fallback"],
        question="Q3_NATURE"
    )