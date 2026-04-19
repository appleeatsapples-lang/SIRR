"""Egyptian 36 Decans — COMPUTED_STRICT (Ptolemaic) + LOOKUP_FIXED (T-list)

Layer 1 — Ptolemaic Decan Assignment (STRICT):
  Each decan = 10° of the ecliptic. Birth date → solar longitude → decan 1-36.
  Planetary ruler assigned via Chaldean decan rulership order (well-defined, not disputed).

Layer 2 — Egyptian Star-Decan Names (scholarly reconstruction):
  The 36 Egyptian decans from diagonal star tables (T-list / AEA McMaster).
  Mapped to Ptolemaic decan numbers as cultural enrichment.
  NOTE: The 1:1 mapping of Egyptian star-decan names to zodiac degrees is
  academically disputed. This is a scholarly reconstruction, not strict computation.

Source: AEA McMaster (aea.physics.mcmaster.ca), Ainsworth thesis.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Chaldean decan rulership order (Ptolemaic — well-defined, not disputed)
# Cycles: Mars→Sun→Venus→Mercury→Moon→Saturn→Jupiter, starting from Aries decan 1
_CHALDEAN_ORDER = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]
DECAN_RULERS = [_CHALDEAN_ORDER[i % 7] for i in range(36)]

# 36 Egyptian Decans — T-list star/deity associations (scholarly reconstruction)
# Ordered by ecliptic longitude (0° Aries = Vernal Equinox)
# WARNING: The mapping of these Egyptian names to zodiac degrees is disputed.
# Treat as cultural enrichment, not strict astronomical fact.
DECANS_36 = [
    # Aries (0-30°)
    {"decan": 1, "sign": "Aries", "degrees": "0-10°", "star": "Khentet-Hert", "deity": "Khnum",
     "quality": "Cardinal Fire I", "theme": "Initiation by force"},
    {"decan": 2, "sign": "Aries", "degrees": "10-20°", "star": "Khentet-Khert", "deity": "Anubis",
     "quality": "Cardinal Fire II", "theme": "The guide between worlds"},
    {"decan": 3, "sign": "Aries", "degrees": "20-30°", "star": "Khent-Hru", "deity": "Horus",
     "quality": "Cardinal Fire III", "theme": "Victory through combat"},
    # Taurus (30-60°)
    {"decan": 4, "sign": "Taurus", "degrees": "0-10°", "star": "Ast", "deity": "Isis",
     "quality": "Fixed Earth I", "theme": "Receptive power"},
    {"decan": 5, "sign": "Taurus", "degrees": "10-20°", "star": "Aart", "deity": "Hathor",
     "quality": "Fixed Earth II", "theme": "Pleasure and abundance"},
    {"decan": 6, "sign": "Taurus", "degrees": "20-30°", "star": "Remn-Heru-An", "deity": "Ptah",
     "quality": "Fixed Earth III", "theme": "Craftsmanship and form"},
    # Gemini (60-90°)
    {"decan": 7, "sign": "Gemini", "degrees": "0-10°", "star": "Themat-Hert", "deity": "Thoth",
     "quality": "Mutable Air I", "theme": "Sacred writing and speech"},
    {"decan": 8, "sign": "Gemini", "degrees": "10-20°", "star": "Themat-Khert", "deity": "Seshat",
     "quality": "Mutable Air II", "theme": "Measurement and record"},
    {"decan": 9, "sign": "Gemini", "degrees": "20-30°", "star": "Ustha", "deity": "Shu",
     "quality": "Mutable Air III", "theme": "Separation and clarity"},
    # Cancer (90-120°)
    {"decan": 10, "sign": "Cancer", "degrees": "0-10°", "star": "Seshmu", "deity": "Khepri",
     "quality": "Cardinal Water I", "theme": "Emergence from darkness"},
    {"decan": 11, "sign": "Cancer", "degrees": "10-20°", "star": "Kenmet", "deity": "Selket",
     "quality": "Cardinal Water II", "theme": "Protection through poison"},
    {"decan": 12, "sign": "Cancer", "degrees": "20-30°", "star": "Semed", "deity": "Bastet",
     "quality": "Cardinal Water III", "theme": "Domestic sovereignty"},
    # Leo (120-150°)
    {"decan": 13, "sign": "Leo", "degrees": "0-10°", "star": "Sert", "deity": "Ra",
     "quality": "Fixed Fire I", "theme": "Solar kingship"},
    {"decan": 14, "sign": "Leo", "degrees": "10-20°", "star": "Sa-Sert", "deity": "Sekhmet",
     "quality": "Fixed Fire II", "theme": "Destructive healing"},
    {"decan": 15, "sign": "Leo", "degrees": "20-30°", "star": "Akhui", "deity": "Atum",
     "quality": "Fixed Fire III", "theme": "Completion and return"},
    # Virgo (150-180°)
    {"decan": 16, "sign": "Virgo", "degrees": "0-10°", "star": "Beka", "deity": "Renenutet",
     "quality": "Mutable Earth I", "theme": "Harvest and nourishment"},
    {"decan": 17, "sign": "Virgo", "degrees": "10-20°", "star": "Tpa-Khent-Heru", "deity": "Maat",
     "quality": "Mutable Earth II", "theme": "Cosmic order and truth"},
    {"decan": 18, "sign": "Virgo", "degrees": "20-30°", "star": "Khentu-Heru", "deity": "Nephthys",
     "quality": "Mutable Earth III", "theme": "Hidden service"},
    # Libra (180-210°)
    {"decan": 19, "sign": "Libra", "degrees": "0-10°", "star": "Spt-Khnt", "deity": "Maat",
     "quality": "Cardinal Air I", "theme": "The weighing of the heart"},
    {"decan": 20, "sign": "Libra", "degrees": "10-20°", "star": "Hry-Ib-Wia", "deity": "Osiris",
     "quality": "Cardinal Air II", "theme": "Judgment and resurrection"},
    {"decan": 21, "sign": "Libra", "degrees": "20-30°", "star": "Sesme", "deity": "Tefnut",
     "quality": "Cardinal Air III", "theme": "Moisture and balance"},
    # Scorpio (210-240°)
    {"decan": 22, "sign": "Scorpio", "degrees": "0-10°", "star": "Kenmu", "deity": "Set",
     "quality": "Fixed Water I", "theme": "Storm and disruption"},
    {"decan": 23, "sign": "Scorpio", "degrees": "10-20°", "star": "Smat", "deity": "Serqet",
     "quality": "Fixed Water II", "theme": "Scorpion medicine"},
    {"decan": 24, "sign": "Scorpio", "degrees": "20-30°", "star": "Srt", "deity": "Anubis",
     "quality": "Fixed Water III", "theme": "Death rites and passage"},
    # Sagittarius (240-270°)
    {"decan": 25, "sign": "Sagittarius", "degrees": "0-10°", "star": "Sa-Srt", "deity": "Neith",
     "quality": "Mutable Fire I", "theme": "The huntress"},
    {"decan": 26, "sign": "Sagittarius", "degrees": "10-20°", "star": "Tp-a-Khentet", "deity": "Montu",
     "quality": "Mutable Fire II", "theme": "War god's precision"},
    {"decan": 27, "sign": "Sagittarius", "degrees": "20-30°", "star": "Khentet-Hert", "deity": "Amun",
     "quality": "Mutable Fire III", "theme": "Hidden wind"},
    # Capricorn (270-300°)
    {"decan": 28, "sign": "Capricorn", "degrees": "0-10°", "star": "Khentet-Khert", "deity": "Geb",
     "quality": "Cardinal Earth I", "theme": "Foundation of earth"},
    {"decan": 29, "sign": "Capricorn", "degrees": "10-20°", "star": "Shesmu", "deity": "Sobek",
     "quality": "Cardinal Earth II", "theme": "Crocodile patience"},
    {"decan": 30, "sign": "Capricorn", "degrees": "20-30°", "star": "Kenmet", "deity": "Min",
     "quality": "Cardinal Earth III", "theme": "Fertility and ambition"},
    # Aquarius (300-330°)
    {"decan": 31, "sign": "Aquarius", "degrees": "0-10°", "star": "Semed", "deity": "Nut",
     "quality": "Fixed Air I", "theme": "Sky vault"},
    {"decan": 32, "sign": "Aquarius", "degrees": "10-20°", "star": "Sert", "deity": "Hapy",
     "quality": "Fixed Air II", "theme": "The inundation"},
    {"decan": 33, "sign": "Aquarius", "degrees": "20-30°", "star": "Sa-Sert", "deity": "Wadjet",
     "quality": "Fixed Air III", "theme": "The cobra's eye"},
    # Pisces (330-360°)
    {"decan": 34, "sign": "Pisces", "degrees": "0-10°", "star": "Akhui", "deity": "Khonsu",
     "quality": "Mutable Water I", "theme": "Moon traveler"},
    {"decan": 35, "sign": "Pisces", "degrees": "10-20°", "star": "Beka", "deity": "Bes",
     "quality": "Mutable Water II", "theme": "Protection of the vulnerable"},
    {"decan": 36, "sign": "Pisces", "degrees": "20-30°", "star": "Tpa-Khent-Heru", "deity": "Nun",
     "quality": "Mutable Water III", "theme": "Primordial waters"},
]


def _get_sun_longitude(dob, birth_time_local, timezone):
    """Get Sun longitude from Swiss Ephemeris if available."""
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        tz_offsets = {"Asia/Riyadh": 3, "Asia/Dubai": 4, "UTC": 0}
        tz_off = tz_offsets.get(timezone, 3)
        h, m = map(int, birth_time_local.split(":"))
        ut_decimal = (h + m / 60) - tz_off
        jd_ut = swe.julday(dob.year, dob.month, dob.day, ut_decimal)
        sun = swe.calc_ut(jd_ut, swe.SUN)[0][0]
        return sun, True
    except ImportError:
        return None, False


def _approx_sun_longitude(dob) -> float:
    """Approximate sun longitude from date (fallback)."""
    from datetime import date
    vernal = date(dob.year, 3, 20)
    days_from_equinox = (dob - vernal).days
    return (days_from_equinox * (360 / 365.25)) % 360


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    sun_lon, has_ephem = _get_sun_longitude(
        profile.dob,
        profile.birth_time_local or "12:00",
        profile.timezone or "Asia/Riyadh"
    )

    if not has_ephem or sun_lon is None:
        sun_lon = _approx_sun_longitude(profile.dob)
        certainty = "APPROX"
        note = "Fallback to approximate solar longitude"
    else:
        certainty = "COMPUTED_STRICT"
        note = f"Sun longitude {sun_lon:.4f}° from Swiss Ephemeris"

    # Layer 1: Ptolemaic decan assignment (STRICT math)
    decan_index = int(sun_lon / 10)  # 0-35
    if decan_index >= 36:
        decan_index = 35

    decan = DECANS_36[decan_index]
    ruler = DECAN_RULERS[decan_index]

    # Element from quality string
    quality = decan["quality"]
    element = "Unknown"
    for e in ["Fire", "Earth", "Air", "Water"]:
        if e in quality:
            element = e
            break

    return SystemResult(
        id="egyptian_decan",
        name="Egyptian 36 Decans",
        certainty=certainty,
        data={
            "sun_longitude": round(sun_lon, 4),
            # Layer 1: Ptolemaic decan (strict)
            "ptolemaic_decan": decan["decan"],
            "decan_number": decan["decan"],
            "decan_sign": decan["sign"],
            "decan_degrees": decan["degrees"],
            "planetary_ruler": ruler,
            "quality": quality,
            "element": element,
            # Layer 2: Egyptian T-list names (scholarly reconstruction)
            "egyptian_name": decan["star"],
            "star": decan["star"],
            "deity": decan["deity"],
            "theme": decan["theme"],
            "certainty_note": (
                "Ptolemaic decan assignment is strict. "
                "Egyptian star-decan correlation is scholarly reconstruction."
            ),
            "note": note,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "36 Egyptian Decans: each = 10° of ecliptic, 3 per zodiac sign",
            "Ptolemaic decan rulers: Chaldean order (Mars→Sun→Venus→Mercury→Moon→Saturn→Jupiter)",
            "Egyptian T-list star names: AEA McMaster / Ainsworth reconstruction",
        ],
        question="Q1_IDENTITY"
    )
