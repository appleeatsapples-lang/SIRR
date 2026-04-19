"""Thelemic Qabalah Gematria — COMPUTED_STRICT
Aleister Crowley's English Qabalah (EQ) and ALW cipher.
ALW cipher: A=1,L=2,W=3,H=4,S=5,D=6... (spiral through alphabet by 11s).
Source: Liber AL vel Legis / English Qabalah tradition
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# ALW Cipher: start at A, advance by 11 positions cyclically
_ORDER = "ALWHMXDINTYEJPUFKQVBGLRCWMSXHNTIOEUJPFVKAQ"
ALW_MAP = {}
for i in range(26):
    letter = chr(65 + ((i * 11) % 26))
    ALW_MAP[letter] = i + 1
# Ensure all 26 letters mapped
for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    if ch not in ALW_MAP:
        ALW_MAP[ch] = ((ord(ch) - 65) * 11 % 26) + 1

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [(ch, ALW_MAP.get(ch, 0)) for ch in name if ch.isalpha()]
    total = sum(v for _, v in letters)
    root = reduce_number(total, keep_masters=(11, 22, 33))

    # Key Thelemic numbers
    is_93 = total == 93 or root == 3  # Thelema = 93
    is_418 = total == 418  # Abrahadabra = 418
    is_666 = total == 666  # To Mega Therion

    return SystemResult(
        id="thelemic_gematria", name="Thelemic Qabalah (ALW Cipher)",
        certainty="COMPUTED_STRICT",
        data={"name": profile.subject, "total": total, "root": root,
              "letter_count": len(letters),
              "thelemic_resonances": {
                  "93_thelema": is_93, "418_abrahadabra": is_418, "666_therion": is_666
              }},
        interpretation=None, constants_version=constants["version"],
        references=["ALW Cipher (English Qabalah): A=1, L=2, W=3... advance by 11"],
        question="Q1_IDENTITY"
    )
