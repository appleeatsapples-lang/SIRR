"""Hebrew AIQ BKR (Nine Chambers of Agrippa) — COMPUTED_STRICT
Maps Hebrew letters into 9 Chambers via decimal collapse:
  Chamber 1: Aleph(1), Yod(10), Qof(100) — all reduce to 1
  Chamber 2: Bet(2), Kaf(20), Resh(200) — all reduce to 2
  ...etc.
Sum chamber indices for full name. This is genuinely different from standard gematria
(which uses absolute values: Aleph=1, Yod=10, Qof=100).
Uses Arabic→Hebrew transliteration from constants.json (same pipeline as hebrew_gematria).
Source: Agrippa, "Three Books of Occult Philosophy", Book 3 Ch.30
"""
from __future__ import annotations
from collections import Counter
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# AIQ BKR chamber assignments: letter name → chamber index (1-9)
# Derived from standard gematria values by decimal collapse (value → first digit)
CHAMBER = {
    "aleph": 1,   # 1
    "yod": 1,     # 10
    "qof": 1,     # 100
    "bet": 2,     # 2
    "kaf": 2,     # 20
    "resh": 2,    # 200
    "gimel": 3,   # 3
    "lamed": 3,   # 30
    "shin": 3,    # 300
    "dalet": 4,   # 4
    "mem": 4,     # 40
    "tav": 4,     # 400
    "he": 5,      # 5
    "nun": 5,     # 50
    "vav": 6,     # 6
    "samekh": 6,  # 60
    "zayin": 7,   # 7
    "ayin": 7,    # 70
    "chet": 8,    # 8
    "pe": 8,      # 80
    "tet": 9,     # 9
    "tsade": 9,   # 90
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    cfg = constants.get("hebrew_gematria", {})
    ar_to_heb = cfg.get("arabic_to_hebrew", {})

    arabic = profile.arabic.strip()
    chambers = []

    for ch in arabic:
        if ch == " " or ch == "\u200c":  # space or ZWNJ
            continue
        heb_name = ar_to_heb.get(ch)
        if heb_name and heb_name in CHAMBER:
            chambers.append((ch, heb_name, CHAMBER[heb_name]))

    chamber_sum = sum(c for _, _, c in chambers)
    chamber_root = reduce_number(chamber_sum) if chamber_sum > 0 else 0

    # Chamber frequency distribution
    freq = Counter(c for _, _, c in chambers)
    chamber_counts = {i: freq.get(i, 0) for i in range(1, 10)}
    dominant_chamber = max(freq, key=freq.get) if freq else 0

    return SystemResult(
        id="hebrew_aiq_beker",
        name="Hebrew AIQ BKR (Nine Chambers)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_analyzed": arabic,
            "letter_count": len(chambers),
            "chamber_sum": chamber_sum,
            "chamber_root": chamber_root,
            "chamber_counts": chamber_counts,
            "dominant_chamber": dominant_chamber,
            "dominant_count": freq.get(dominant_chamber, 0) if dominant_chamber else 0,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Agrippa, 'Three Books of Occult Philosophy', Book 3 Ch.30: AIQ BKR / Nine Chambers",
            "Decimal collapse: units/tens/hundreds of same digit share a chamber",
            "SOURCE_TIER:A — Primary Renaissance occult text with clear algorithmic definition.",
        ],
        question="Q1_IDENTITY",
    )
