"""Trithemius Steganographic Cipher — COMPUTED_STRICT
Johannes Trithemius's polyalphabetic substitution (Polygraphiae, 1518).
Each letter is shifted by its position: 1st letter +0, 2nd +1, 3rd +2...
The cipher text reveals hidden numeric signatures.
Source: Trithemius, Polygraphiae (1518) / Steganographia (1499)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [ch for ch in name if ch.isalpha()]

    cipher_letters = []
    cipher_values = []
    for i, ch in enumerate(letters):
        shifted = (ord(ch) - 65 + i) % 26
        cipher_ch = chr(shifted + 65)
        cipher_letters.append(cipher_ch)
        cipher_values.append(shifted + 1)  # 1-indexed value

    cipher_text = "".join(cipher_letters)
    cipher_sum = sum(cipher_values)
    cipher_root = reduce_number(cipher_sum, keep_masters=(11, 22, 33))

    return SystemResult(
        id="trithemius", name="Trithemius Steganographic Cipher",
        certainty="COMPUTED_STRICT",
        data={
            "name": profile.subject,
            "cipher_text": cipher_text,
            "cipher_sum": cipher_sum,
            "cipher_root": cipher_root,
            "letter_count": len(letters),
        },
        interpretation=None, constants_version=constants["version"],
        references=["Trithemius Polygraphiae (1518): positional shift cipher, letter N at position P → (N+P) mod 26"],
        question="Q1_IDENTITY"
    )
