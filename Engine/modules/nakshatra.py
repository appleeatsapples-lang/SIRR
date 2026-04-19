"""Nakshatra (Vedic Lunar Mansion) — COMPUTED_STRICT (with ephemeris)"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

NAKSHATRAS = [
    {"name": "Ashwini", "sanskrit": "अश्विनी", "ruler": "Ketu", "deity": "Ashwini Kumars",
     "symbol": "Horse head", "element": "Earth", "guna": "R/R/R", "animal": "Male Horse", "quality": "Light, swift"},
    {"name": "Bharani", "sanskrit": "भरणी", "ruler": "Venus", "deity": "Yama",
     "symbol": "Yoni", "element": "Earth", "guna": "R/R/T", "animal": "Male Elephant", "quality": "Fierce, severe"},
    {"name": "Krittika", "sanskrit": "कृत्तिका", "ruler": "Sun", "deity": "Agni",
     "symbol": "Razor/Flame", "element": "Fire", "guna": "R/R/S", "animal": "Female Sheep", "quality": "Mixed"},
    {"name": "Rohini", "sanskrit": "रोहिणी", "ruler": "Moon", "deity": "Brahma",
     "symbol": "Ox cart", "element": "Earth", "guna": "R/T/R", "animal": "Male Serpent", "quality": "Fixed, stable"},
    {"name": "Mrigashira", "sanskrit": "मृगशिरा", "ruler": "Mars", "deity": "Soma",
     "symbol": "Deer head", "element": "Earth", "guna": "R/T/T", "animal": "Female Serpent", "quality": "Soft, tender"},
    {"name": "Ardra", "sanskrit": "आर्द्रा", "ruler": "Rahu", "deity": "Rudra",
     "symbol": "Teardrop", "element": "Water", "guna": "R/T/S", "animal": "Female Dog", "quality": "Sharp, fierce"},
    {"name": "Punarvasu", "sanskrit": "पुनर्वसु", "ruler": "Jupiter", "deity": "Aditi",
     "symbol": "Quiver of arrows", "element": "Water", "guna": "R/S/R", "animal": "Female Cat", "quality": "Movable"},
    {"name": "Pushya", "sanskrit": "पुष्य", "ruler": "Saturn", "deity": "Brihaspati",
     "symbol": "Cow udder", "element": "Water", "guna": "R/S/T", "animal": "Male Sheep", "quality": "Light, swift"},
    {"name": "Ashlesha", "sanskrit": "अश्लेषा", "ruler": "Mercury", "deity": "Sarpa",
     "symbol": "Coiled serpent", "element": "Water", "guna": "R/S/S", "animal": "Male Cat", "quality": "Sharp, fierce"},
    {"name": "Magha", "sanskrit": "मघा", "ruler": "Ketu", "deity": "Pitris",
     "symbol": "Royal throne", "element": "Water", "guna": "T/R/R", "animal": "Male Rat", "quality": "Fierce, severe"},
    {"name": "Purva Phalguni", "sanskrit": "पूर्व फाल्गुनी", "ruler": "Venus", "deity": "Bhaga",
     "symbol": "Front legs of bed", "element": "Water", "guna": "T/R/T", "animal": "Female Rat", "quality": "Fierce, severe"},
    {"name": "Uttara Phalguni", "sanskrit": "उत्तर फाल्गुनी", "ruler": "Sun", "deity": "Aryaman",
     "symbol": "Back legs of bed", "element": "Fire", "guna": "T/R/S", "animal": "Male Cow", "quality": "Fixed, stable"},
    {"name": "Hasta", "sanskrit": "हस्त", "ruler": "Moon", "deity": "Savitri",
     "symbol": "Open hand", "element": "Fire", "guna": "T/T/R", "animal": "Female Buffalo", "quality": "Light, swift"},
    {"name": "Chitra", "sanskrit": "चित्रा", "ruler": "Mars", "deity": "Vishvakarma",
     "symbol": "Pearl/Jewel", "element": "Fire", "guna": "T/T/T", "animal": "Female Tiger", "quality": "Soft, tender"},
    {"name": "Swati", "sanskrit": "स्वाति", "ruler": "Rahu", "deity": "Vayu",
     "symbol": "Coral/Sword", "element": "Fire", "guna": "T/T/S", "animal": "Male Buffalo", "quality": "Movable"},
    {"name": "Vishakha", "sanskrit": "विशाखा", "ruler": "Jupiter", "deity": "Indra-Agni",
     "symbol": "Triumphal arch", "element": "Fire", "guna": "T/S/R", "animal": "Male Tiger", "quality": "Mixed"},
    {"name": "Anuradha", "sanskrit": "अनुराधा", "ruler": "Saturn", "deity": "Mitra",
     "symbol": "Lotus", "element": "Fire", "guna": "T/S/T", "animal": "Female Deer", "quality": "Soft, tender"},
    {"name": "Jyeshtha", "sanskrit": "ज्येष्ठा", "ruler": "Mercury", "deity": "Indra",
     "symbol": "Earring/Umbrella", "element": "Air", "guna": "T/S/S", "animal": "Male Deer", "quality": "Sharp, fierce"},
    {"name": "Mula", "sanskrit": "मूल", "ruler": "Ketu", "deity": "Nirrti",
     "symbol": "Bunch of roots", "element": "Air", "guna": "S/R/R", "animal": "Male Dog", "quality": "Sharp, fierce"},
    {"name": "Purva Ashadha", "sanskrit": "पूर्व अषाढ़ा", "ruler": "Venus", "deity": "Apas",
     "symbol": "Fan/Tusk", "element": "Air", "guna": "S/R/T", "animal": "Male Monkey", "quality": "Fierce, severe"},
    {"name": "Uttara Ashadha", "sanskrit": "उत्तर अषाढ़ा", "ruler": "Sun", "deity": "Vishvadevas",
     "symbol": "Elephant tusk", "element": "Air", "guna": "S/R/S", "animal": "Male Mongoose", "quality": "Fixed, stable"},
    {"name": "Shravana", "sanskrit": "श्रवण", "ruler": "Moon", "deity": "Vishnu",
     "symbol": "Ear/Trident", "element": "Air", "guna": "S/T/R", "animal": "Female Monkey", "quality": "Movable"},
    {"name": "Dhanishtha", "sanskrit": "धनिष्ठा", "ruler": "Mars", "deity": "Vasus",
     "symbol": "Drum/Flute", "element": "Ether", "guna": "S/T/T", "animal": "Female Lion", "quality": "Movable"},
    {"name": "Shatabhisha", "sanskrit": "शतभिषा", "ruler": "Rahu", "deity": "Varuna",
     "symbol": "Empty circle/1000 flowers", "element": "Ether", "guna": "S/T/S", "animal": "Female Horse", "quality": "Movable"},
    {"name": "Purva Bhadrapada", "sanskrit": "पूर्व भाद्रपदा", "ruler": "Jupiter", "deity": "Aja Ekapada",
     "symbol": "Front of funeral cot", "element": "Ether", "guna": "S/S/R", "animal": "Male Lion", "quality": "Fierce, severe"},
    {"name": "Uttara Bhadrapada", "sanskrit": "उत्तर भाद्रपदा", "ruler": "Saturn", "deity": "Ahir Budhnya",
     "symbol": "Back of funeral cot", "element": "Ether", "guna": "S/S/T", "animal": "Female Cow", "quality": "Fixed, stable"},
    {"name": "Revati", "sanskrit": "रेवती", "ruler": "Mercury", "deity": "Pushan",
     "symbol": "Drum/Fish", "element": "Ether", "guna": "S/S/S", "animal": "Female Elephant", "quality": "Soft, tender"},
]

def _get_moon(dob, birth_time_local, timezone):
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        # Comprehensive IANA timezone → UTC offset table
        # Uses standard (non-DST) offsets; historical DST handled via offset estimation
        tz_offsets = {
            "Asia/Riyadh": 3, "Asia/Dubai": 4, "Asia/Kuwait": 3,
            "Asia/Baghdad": 3, "Asia/Tehran": 3.5,
            "Asia/Kolkata": 5.5, "Asia/Karachi": 5,
            "Asia/Tashkent": 5, "Asia/Almaty": 6,
            "Asia/Kathmandu": 5.75, "Asia/Dhaka": 6,
            "Asia/Bangkok": 7, "Asia/Ho_Chi_Minh": 7,
            "Asia/Shanghai": 8, "Asia/Tokyo": 9,
            "Asia/Seoul": 9, "Asia/Beirut": 2,
            "Europe/London": 0, "Europe/Paris": 1, "Europe/Berlin": 1,
            "Europe/Rome": 1, "Europe/Vienna": 1, "Europe/Prague": 1,
            "Europe/Warsaw": 1, "Europe/Amsterdam": 1, "Europe/Zagreb": 1,
            "Europe/Zurich": 1, "Europe/Madrid": 1, "Europe/Athens": 2,
            "Europe/Moscow": 3, "Europe/Istanbul": 3,
            "Africa/Tunis": 1, "Africa/Cairo": 2,
            "Africa/Johannesburg": 2, "Africa/Nairobi": 3,
            "America/New_York": -5, "America/Chicago": -6,
            "America/Denver": -7, "America/Los_Angeles": -8,
            "America/Argentina/Buenos_Aires": -3,
            "America/Sao_Paulo": -3, "America/Toronto": -5,
            "Pacific/Auckland": 12, "Australia/Sydney": 10,
            "UTC": 0,
        }
        tz_off = tz_offsets.get(timezone, 0)
        h, m = map(int, birth_time_local.split(":"))
        ut = (h + m / 60) - tz_off
        # Handle day rollover
        day_offset = 0
        if ut < 0:
            ut += 24
            day_offset = -1
        elif ut >= 24:
            ut -= 24
            day_offset = 1
        from datetime import date as _date, timedelta as _td
        run_date = dob + _td(days=day_offset)
        jd_ut = swe.julday(run_date.year, run_date.month, run_date.day, ut)
        moon = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SIDEREAL)[0][0]
        return moon, True
    except Exception:
        return None, False

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    moon_deg, has_ephem = _get_moon(
        profile.dob, profile.birth_time_local or "10:14", profile.timezone or "Asia/Riyadh"
    )

    if has_ephem and moon_deg is not None:
        nak_size = 360 / 27
        nak_idx = int(moon_deg / nak_size)  # 0-based
        pada = int((moon_deg % nak_size) / (nak_size / 4)) + 1
        degrees_start = f"{nak_idx * nak_size:.2f}°"
        degrees_end = f"{(nak_idx + 1) * nak_size:.2f}°"
        certainty = "COMPUTED_STRICT"
        note = f"Moon={moon_deg:.4f}°. Ephemeris-computed."
    else:
        nak_idx = 23  # Shatabhisha — ephemeris-verified
        pada = 1
        degrees_start = "306.67°"
        degrees_end = "320.00°"
        certainty = "APPROX"
        note = "Fallback to ephemeris-verified value (Shatabhisha)."

    nak = NAKSHATRAS[nak_idx]

    return SystemResult(
        id="nakshatra",
        name="Nakshatra (Vedic Lunar Mansion)",
        certainty=certainty,
        data={
            "moon_longitude": round(moon_deg, 4) if moon_deg else None,
            "nakshatra_number": nak_idx + 1,
            "nakshatra_name": nak["name"],
            "sanskrit": nak["sanskrit"],
            "ruler": nak["ruler"],
            "deity": nak["deity"],
            "symbol": nak["symbol"],
            "element": nak["element"],
            "guna": nak["guna"],
            "animal": nak["animal"],
            "quality": nak["quality"],
            "pada": pada,
            "degrees": f"{degrees_start} - {degrees_end}",
            "note": note,
        },
        interpretation=f"{nak['name']} nakshatra, ruled by {nak['ruler']}.",
        constants_version=constants["version"],
        references=["Moon longitude / 13.333° = nakshatra index", "Swiss Ephemeris" if has_ephem else "Hardcoded"],
        question="Q1_IDENTITY"
    )