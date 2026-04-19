"""Arabic→Mandaean Cognate Sum — COMPUTED_STRICT

Scholarship fidelity (§4.5 rule 2 — cognate-mapping surfaced):
  This module routes Arabic letters through an Arabic-to-Mandaean cognate
  table and sums the resulting values. Identity with Abjad Kabir totals
  is BY CONSTRUCTION (same Arabic input, equivalent-position letters),
  NOT cross-tradition convergence.

  Mandaic native numerology uses a distinct duodecimal system tied to
  Mandaean cosmology (World of Light) and does NOT produce values
  equivalent to Arabic abjad. Claiming otherwise would be false
  scholarship. See Häberl, *The Mandaean Book of John*.

  The module kept its internal id `mandaean_gematria` for engine-key
  stability; the public `name` field names it honestly.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def _transliterate(arabic_name: str, mapping: dict) -> list[tuple[str, str]]:
    """Convert Arabic characters to Mandaean letter names, skipping spaces/unmapped."""
    result = []
    for char in arabic_name:
        if char in mapping:
            result.append((char, mapping[char]))
    return result


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    cfg = constants["mandaean_gematria"]
    values = cfg["values"]
    a2m = cfg["arabic_to_mandaean"]

    arabic_name = profile.arabic
    letters = _transliterate(arabic_name, a2m)

    letter_values = [(ar, mand, values[mand]) for ar, mand in letters]
    total = sum(v for _, _, v in letter_values)
    root = reduce_number(total, keep_masters=(11, 22, 33))

    # Per-word breakdown
    words = arabic_name.split()
    word_sums = []
    for word in words:
        w_letters = _transliterate(word, a2m)
        w_total = sum(values[mand] for _, mand in w_letters)
        word_sums.append({"word": word, "gematria": w_total, "root": reduce_number(w_total, keep_masters=(11, 22, 33))})

    return SystemResult(
        id="mandaean_gematria",
        name="Arabic-to-Mandaean Cognate Sum",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_input": arabic_name,
            "transliterated_letters": letter_values,
            "total_gematria": total,
            "gematria_root": root,
            "word_breakdown": word_sums,
            "letter_count": len(letters),
            "note": "Arabic→Mandaean cognate letter mapping. Identity with Abjad Kabir totals is by construction, not cross-tradition convergence. Mandaic native numerology uses distinct duodecimal system (Häberl, Mandaean Book of John).",
            # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
            "scholarship_fidelity": "MODERN_SYNTHESIS",
            "scholarship_note": 'Cognate-mapping identity-by-construction with Abjad Kabir; not native Mandaic duodecimal numerology (Häberl).',
},
        interpretation=f"Arabic-to-Mandaean cognate sum = {total} (root {root}). Not native Mandaic numerology; identity with Abjad Kabir is by construction.",
        constants_version=constants["version"],
        references=["Ginza Rabba (for Mandaean cosmological context)", "Häberl, The Mandaean Book of John (Mandaic duodecimal numerology is distinct)", "Arabic-Mandaean cognate letter mapping (the actual algorithm)"],
        question="Q1_IDENTITY"
    )
