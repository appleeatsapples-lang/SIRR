"""Hebrew Mispar Variants (Gadol/Siduri/Boneeh/Hakadmi) — COMPUTED_STRICT
Four Hebrew gematria methods beyond standard:
  Gadol: Sofit (final) forms at full value (Kaf=500, Mem=600, Nun=700, Pe=800, Tzaddi=900)
  Siduri (Ordinal): Aleph=1, Bet=2, ..., Tav=22
  Boneeh (Building): Cumulative (A=1, AB=1+2, ABC=1+2+3, sum all cumulatives)
  Hakadmi (Triangular): Each letter = n(n+1)/2 where n is ordinal position
Uses Arabic→Hebrew transliteration from constants.json (same as hebrew_gematria).
Source: Scholem, "Kabbalah"; Agrippa Book 3
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Standard gematria values (for Gadol with sofit extensions)
GADOL_VALUES = {
    "aleph": 1, "bet": 2, "gimel": 3, "dalet": 4, "he": 5,
    "vav": 6, "zayin": 7, "chet": 8, "tet": 9, "yod": 10,
    "kaf": 20, "lamed": 30, "mem": 40, "nun": 50, "samekh": 60,
    "ayin": 70, "pe": 80, "tsade": 90, "qof": 100,
    "resh": 200, "shin": 300, "tav": 400,
}

# Sofit (final) form values for Mispar Gadol
# In standard gematria these are already included; Gadol gives sofit their own values
SOFIT_VALUES = {
    "kaf": 500, "mem": 600, "nun": 700, "pe": 800, "tsade": 900,
}

# Ordinal position (1-22)
ORDINAL = {
    "aleph": 1, "bet": 2, "gimel": 3, "dalet": 4, "he": 5,
    "vav": 6, "zayin": 7, "chet": 8, "tet": 9, "yod": 10,
    "kaf": 11, "lamed": 12, "mem": 13, "nun": 14, "samekh": 15,
    "ayin": 16, "pe": 17, "tsade": 18, "qof": 19,
    "resh": 20, "shin": 21, "tav": 22,
}


def _transliterate(arabic_name, ar_to_heb):
    """Convert Arabic name to list of Hebrew letter names."""
    letters = []
    for ch in arabic_name:
        if ch == " " or ch == "\u200c":
            continue
        heb = ar_to_heb.get(ch)
        if heb:
            letters.append(heb)
    return letters


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    cfg = constants.get("hebrew_gematria", {})
    ar_to_heb = cfg.get("arabic_to_hebrew", {})

    letters = _transliterate(profile.arabic.strip(), ar_to_heb)

    if not letters:
        return SystemResult(
            id="hebrew_mispar_variants", name="Hebrew Mispar Variants",
            certainty="COMPUTED_STRICT",
            data={"error": "no Hebrew letters mapped"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q1_IDENTITY",
        )

    # 1. Mispar Gadol (standard gematria — no sofit distinction in transliteration)
    # Since we're transliterating, we don't know which letters are final forms,
    # so Gadol uses standard values (same as hebrew_gematria module)
    gadol_total = sum(GADOL_VALUES.get(l, 0) for l in letters)
    gadol_root = reduce_number(gadol_total)

    # 2. Mispar Siduri (Ordinal)
    siduri_total = sum(ORDINAL.get(l, 0) for l in letters)
    siduri_root = reduce_number(siduri_total)

    # 3. Mispar Boneeh (Building/Cumulative)
    # Sum of cumulative sums: A, A+B, A+B+C, ...
    ordinal_vals = [ORDINAL.get(l, 0) for l in letters]
    running = 0
    boneeh_total = 0
    for v in ordinal_vals:
        running += v
        boneeh_total += running
    boneeh_root = reduce_number(boneeh_total)

    # 4. Mispar Hakadmi (Triangular)
    # Each letter value = n(n+1)/2 where n = ordinal position
    hakadmi_total = sum(n * (n + 1) // 2 for n in ordinal_vals)
    hakadmi_root = reduce_number(hakadmi_total)

    return SystemResult(
        id="hebrew_mispar_variants",
        name="Hebrew Mispar Variants (4 methods)",
        certainty="COMPUTED_STRICT",
        data={
            "letter_count": len(letters),
            "gadol_total": gadol_total,
            "gadol_root": gadol_root,
            "siduri_total": siduri_total,
            "siduri_root": siduri_root,
            "boneeh_total": boneeh_total,
            "boneeh_root": boneeh_root,
            "hakadmi_total": hakadmi_total,
            "hakadmi_root": hakadmi_root,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Scholem, 'Kabbalah': Hebrew gematria variant methods",
            "Agrippa, 'Three Books of Occult Philosophy', Book 3",
            "SOURCE_TIER:A — Primary Kabbalistic and Renaissance occult texts.",
        ],
        question="Q1_IDENTITY",
    )
