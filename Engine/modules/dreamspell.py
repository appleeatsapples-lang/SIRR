"""Dreamspell / Galactic Signature — COMPUTED_STRICT
José Argüelles' modern 260-day count (NOT the traditional Tzolkin).
Uses a fixed correlation where July 26 = start of Dreamspell year.
Kin = ((JDN - epoch) mod 260) + 1. Kin → Seal (1-20) + Tone (1-13).
Source: José Argüelles, The Mayan Factor (1987)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

SEALS = [
    "Red Dragon","White Wind","Blue Night","Yellow Seed","Red Serpent",
    "White Worldbridger","Blue Hand","Yellow Star","Red Moon","White Dog",
    "Blue Monkey","Yellow Human","Red Skywalker","White Wizard","Blue Eagle",
    "Yellow Warrior","Red Earth","White Mirror","Blue Storm","Yellow Sun",
]
TONES = [
    "Magnetic","Lunar","Electric","Self-Existing","Overtone",
    "Rhythmic","Resonant","Galactic","Solar","Planetary",
    "Spectral","Crystal","Cosmic",
]

# Dreamspell epoch: JDN where Kin 260 falls (Kin 1 = EPOCH+1)
# Source: Foundation for the Law of Time; Argüelles Dreamspell (1990)
# Anchor: Dec 21, 2012 = JDN 2456283 = Kin 207
# Formula: (2456283 - EPOCH) % 260 = 207 → EPOCH = 2456076
# Verified: (2456283 - 2456076) % 260 = 207 ✓
# Note: Gemini suggested 2456077 but that gives Kin 206. REVERTED.
EPOCH_JDN = 2456076

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    y, m, d = profile.dob.year, profile.dob.month, profile.dob.day
    a = (14 - m) // 12
    jy = y + 4800 - a
    jm = m + 12 * a - 3
    jdn = d + (153 * jm + 2) // 5 + 365 * jy + jy // 4 - jy // 100 + jy // 400 - 32045

    kin = ((jdn - EPOCH_JDN) % 260)
    if kin <= 0:
        kin += 260

    seal_idx = (kin - 1) % 20
    tone_idx = (kin - 1) % 13

    seal = SEALS[seal_idx]
    tone = TONES[tone_idx]
    signature = f"{tone} {seal}"

    return SystemResult(
        id="dreamspell", name="Dreamspell / Galactic Signature",
        certainty="COMPUTED_STRICT",
        data={
            "kin": kin, "seal": seal, "seal_number": seal_idx + 1,
            "tone": tone, "tone_number": tone_idx + 1,
            "galactic_signature": signature,
        },
        interpretation=None, constants_version=constants["version"],
        references=["José Argüelles, Dreamspell (1987). NOT traditional Tzolkin.",
                    "SOURCE_TIER:C — Invented 1987-1990 by José Argüelles. Diverges from classical Maya Tzolk'in."],
        question="Q1_IDENTITY"
    )
