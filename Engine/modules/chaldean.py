"""Chaldean-system Numerology (19th-c.) — COMPUTED_STRICT

Scholarship fidelity (§4.5 rule 1 — no borrowed classical name without context):
  "Chaldean numerology" is a 19th-century London occultist system
  (popularized by Cheiro, *Book of Numbers*, 1926) that marketed itself
  as ancient Babylonian. The Babylonian attribution is historically
  unsupported — the value table has no demonstrable lineage to ancient
  Chaldean/Babylonian mathematics. Similarly, "Pythagorean numerology"
  (A=1, B=2 → digit reduction) is Dow Balliett's 1900s system, not from
  the Pythagorean school (Nicomachus, Iamblichus never reduced personal
  names for character analysis).

  Both are MODERN_SYNTHESIS per the Scholarship Fidelity schema.

  Key difference between the two modern systems:
    - Chaldean-system: no letter maps to 9 (marketed as "sacred")
    - Balliett-system: all 26 letters map 1-9 in linear wrap
    - S=3, H=5, O=7 in Chaldean vs S=1, H=8, O=6 in Balliett

  Fields are dual-named: primary honest label (`balliett_*`) plus
  legacy alias (`pythagorean_*`) kept for API/test compatibility.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Chaldean letter-number table (verified against Cheiro's Book of Numbers, 1926)
# Key disputes confirmed: S=3, X=5, P=8, NO letter maps to 9.
CHALDEAN = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8,
}

# Balliett (Dow Balliett, 1900s) — also known in popular literature as
# "Pythagorean numerology" though Pythagoras and his school never reduced
# personal names. Kept both names for backward-compat; BALLIETT is primary.
BALLIETT = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

# Backward-compat alias — do not use in new code.
# Legacy tests and downstream consumers may reference PYTH directly.
PYTH = BALLIETT


def _reduce(n: int) -> int:
    """Reduce to single digit (Chaldean does NOT preserve master numbers)."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [c for c in name if c in CHALDEAN]

    chal_values = [CHALDEAN[c] for c in letters]
    ball_values = [BALLIETT[c] for c in letters if c in BALLIETT]

    chal_total = sum(chal_values)
    ball_total = sum(ball_values)
    chal_root = _reduce(chal_total)
    ball_root = _reduce(ball_total)

    # Legacy aliases — kept for API/test compatibility. New consumers should
    # read the `balliett_*` primaries.
    pyth_total = ball_total
    pyth_root = ball_root
    pyth_values = ball_values

    # Per-name breakdown
    name_parts = profile.subject.upper().split()
    part_details = []
    for part in name_parts:
        part_vals = [CHALDEAN[c] for c in part if c in CHALDEAN]
        part_sum = sum(part_vals)
        part_details.append({
            "name": part,
            "values": part_vals,
            "sum": part_sum,
            "root": _reduce(part_sum),
        })

    agrees_with_pythagorean = chal_root == pyth_root

    agrees_with_balliett = chal_root == ball_root
    return SystemResult(
        id="chaldean",
        name="Chaldean-system + Balliett-system Name Numerology (19th/20th c.)",
        certainty="COMPUTED_STRICT",
        data={
            "name_analyzed": profile.subject,
            "chaldean_total": chal_total,
            "chaldean_root": chal_root,
            # Honest primary labels — Dow Balliett 1900s, not Pythagorean
            "balliett_total": ball_total,
            "balliett_root": ball_root,
            "agrees_with_balliett": agrees_with_balliett,
            # Legacy aliases kept for API/test compatibility
            "pythagorean_total": pyth_total,
            "pythagorean_root": pyth_root,
            "agrees_with_pythagorean": agrees_with_pythagorean,
            "name_parts": part_details,
            "letter_count": len(letters),
            "note": ("Chaldean-system numerology is a 19th-c. London occultist creation "
                     "(Cheiro 1926); the Babylonian attribution is historically "
                     "unsupported. Balliett-system numerology (A=1...Z=8) is Dow "
                     "Balliett 1900s, not from the Pythagorean school. Both are "
                     "MODERN_SYNTHESIS per Scholarship Fidelity schema §4.1."),
                     # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
                     "scholarship_fidelity": "MODERN_SYNTHESIS",
                     "scholarship_note": '19th-century London occultist system (Cheiro 1926); Babylonian attribution historically unsupported.',
         },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Cheiro (Count Louis Hamon), Book of Numbers, 1926 — Chaldean-system origin",
            "Dow Balliett, The Philosophy of Numbers, 1908 — Balliett-system origin",
            "Florence Campbell, Your Days Are Numbered, 1931 — Balliett-system development",
            "SCHOLARSHIP NOTE: neither system has verifiable lineage to Chaldean/Babylonian "
            "or Pythagorean mathematics; both are modern occult constructions.",
        ],
        question="Q1_IDENTITY"
    )
