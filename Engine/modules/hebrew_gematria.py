"""Arabic→Hebrew Cognate Sum — COMPUTED_STRICT

Scholarship fidelity (§4.5 rule 2 — cognate-mapping surfaced):
  This module routes Arabic letters through an Arabic-to-Hebrew cognate
  table and sums the resulting values using Standard Mispar Gadol values.
  Identity with Abjad Kabir totals is BY CONSTRUCTION (same Arabic input,
  equivalent-position letters), NOT cross-tradition convergence.

  Native Hebrew gematria applies Mispar Gadol to Hebrew-script text, not
  to transliterated Arabic. Claiming a numerical match across Arabic,
  Mandaean-cognate, and Hebrew-cognate totals reflects historical
  agreement would be false. It reflects the mapping.

  The module kept its internal id `hebrew_gematria` for engine-key
  stability; the public `name` field names it honestly.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def _transliterate(arabic_name: str, mapping: dict) -> list[tuple[str, str]]:
    """Convert Arabic characters to Hebrew letter names, skipping spaces/unmapped."""
    result = []
    for char in arabic_name:
        if char in mapping:
            result.append((char, mapping[char]))
    return result


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    cfg = constants["hebrew_gematria"]
    values = cfg["values"]
    a2h = cfg["arabic_to_hebrew"]

    arabic_name = profile.arabic
    letters = _transliterate(arabic_name, a2h)

    letter_values = [(ar, heb, values[heb]) for ar, heb in letters]
    total = sum(v for _, _, v in letter_values)
    root = reduce_number(total, keep_masters=(11, 22, 33))

    # Per-word breakdown
    words = arabic_name.split()
    word_sums = []
    for word in words:
        w_letters = _transliterate(word, a2h)
        w_total = sum(values[heb] for _, heb in w_letters)
        word_sums.append({"word": word, "gematria": w_total, "root": reduce_number(w_total, keep_masters=(11, 22, 33))})

    return SystemResult(
        id="hebrew_gematria",
        name="Arabic-to-Hebrew Cognate Sum (Mispar Gadol values)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_input": arabic_name,
            "transliterated_letters": letter_values,
            "total_gematria": total,
            "gematria_root": root,
            "word_breakdown": word_sums,
            "letter_count": len(letters),
            "note": "Arabic→Hebrew cognate letter mapping with Standard Mispar Gadol values. Identity with Abjad Kabir totals is by construction, not cross-tradition convergence. Native Hebrew gematria applies to Hebrew-script text directly.",
            # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
            "scholarship_fidelity": "MODERN_SYNTHESIS",
            "scholarship_note": 'Cognate-mapping using Mispar Gadol values; not native Hebrew gematria on Hebrew-script text.',
},
        interpretation=f"Arabic-to-Hebrew cognate sum = {total} (root {root}). Not native Hebrew gematria; identity with Abjad Kabir is by construction.",
        constants_version=constants["version"],
        references=["Standard Hebrew Mispar Gadol (for value table, not for the algorithm — this routes Arabic through cognates)", "Arabic-to-Hebrew cognate letter mapping (the actual algorithm used here)"],
        question="Q1_IDENTITY"
    )
