"""Istikhara bil-Adad (Numerical Signatures) — COMPUTED_STRICT
Modular arithmetic divination: takes Abjad total and computes
remainder against 4, 7, 9, and 12 to classify the name across
independent categorical axes (element, planet, falak, sign).
Source: Taj al-Muluk and regional manuscripts (10th century onwards)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Modulo 4: Elements (Taba'i)
MOD4_ELEMENTS = {1: "Fire (نار)", 2: "Air (هواء)", 3: "Water (ماء)", 0: "Earth (تراب)"}

# Modulo 7: Planetary Days (Kawakib)
MOD7_PLANETS = {
    1: "Sun (الشمس)", 2: "Moon (القمر)", 3: "Mars (المريخ)",
    4: "Mercury (عطارد)", 5: "Jupiter (المشتري)",
    6: "Venus (الزهرة)", 0: "Saturn (زحل)"
}

# Modulo 9: Celestial Spheres (Aflak)
MOD9_FALAK = {
    1: "1st Sphere — Moon", 2: "2nd Sphere — Mercury",
    3: "3rd Sphere — Venus", 4: "4th Sphere — Sun",
    5: "5th Sphere — Mars", 6: "6th Sphere — Jupiter",
    7: "7th Sphere — Saturn", 8: "8th Sphere — Fixed Stars",
    0: "9th Sphere — Primum Mobile"
}

# Modulo 12: Zodiac Signs (Buruj)
MOD12_SIGNS = {
    1: "Aries (الحمل)", 2: "Taurus (الثور)", 3: "Gemini (الجوزاء)",
    4: "Cancer (السرطان)", 5: "Leo (الأسد)", 6: "Virgo (السنبلة)",
    7: "Libra (الميزان)", 8: "Scorpio (العقرب)", 9: "Sagittarius (القوس)",
    10: "Capricorn (الجدي)", 11: "Aquarius (الدلو)", 0: "Pisces (الحوت)"
}


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    name = profile.arabic.replace(" ", "")
    total = sum(abjad.get(ch, 0) for ch in name)

    m4 = total % 4
    m7 = total % 7
    m9 = total % 9
    m12 = total % 12

    return SystemResult(
        id="istikhara_adad",
        name="Istikhara bil-Adad (استخارة بالعدد — Numerical Signatures)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic,
            "abjad_total": total,
            "mod_4": {"remainder": m4, "element": MOD4_ELEMENTS[m4]},
            "mod_7": {"remainder": m7, "planet": MOD7_PLANETS[m7]},
            "mod_9": {"remainder": m9, "falak": MOD9_FALAK[m9]},
            "mod_12": {"remainder": m12, "sign": MOD12_SIGNS[m12]},
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Modular arithmetic classification from Abjad total.",
            "Source: Taj al-Muluk, regional Istikhara manuscripts.",
        ],
        question="Q1_IDENTITY"
    )
