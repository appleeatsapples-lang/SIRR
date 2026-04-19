"""Ars Magna / Lullian Wheels — COMPUTED_STRICT
Ramon Llull's combinatorial method: maps name letters to 9 Dignities
(Bonitas, Magnitudo, Aeternitas, Potestas, Sapientia, Voluntas,
Virtus, Veritas, Gloria) and generates binary combinations.
Source: Ramon Llull, Ars Magna (1305)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

DIGNITIES = ["Bonitas","Magnitudo","Aeternitas","Potestas","Sapientia",
             "Voluntas","Virtus","Veritas","Gloria"]

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [ch for ch in name if ch.isalpha()]

    # Map each letter to one of 9 dignities (A-I → 0-8, J-R → 0-8, S-Z → 0-7)
    mapped = []
    for ch in letters:
        idx = (ord(ch) - 65) % 9
        mapped.append({"letter": ch, "dignity": DIGNITIES[idx]})

    # Count dignity frequencies
    freq = {}
    for m in mapped:
        d = m["dignity"]
        freq[d] = freq.get(d, 0) + 1

    dominant = max(freq, key=freq.get) if freq else "?"

    # Generate primary binary combinations from first 4 unique dignities
    unique = list(dict.fromkeys(m["dignity"] for m in mapped))[:4]
    combos = []
    for i in range(len(unique)):
        for j in range(i+1, len(unique)):
            combos.append(f"{unique[i]}-{unique[j]}")

    return SystemResult(
        id="ars_magna", name="Ars Magna (Lullian Wheels)",
        certainty="COMPUTED_STRICT",
        data={
            "name": profile.subject, "dominant_dignity": dominant,
            "dignity_frequencies": freq,
            "primary_combinations": combos,
            "letter_count": len(letters),
        },
        interpretation=None, constants_version=constants["version"],
        references=["Ramon Llull, Ars Magna (1305): 9 Divine Dignities combinatorial system"],
        question="Q1_IDENTITY"
    )
