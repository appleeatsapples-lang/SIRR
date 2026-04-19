"""Karmic Debt Detection — COMPUTED_STRICT
Checks for 13, 14, 16, 19 in core numerological positions BEFORE reduction.
Canonical set per Hans Decoz (worldnumerology.com): 13/4, 14/5, 16/7, 19/1 ONLY.
22/4 and 11/2 are master numbers, NOT karmic debts.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Karmic debt set locked to 13/14/16/19 per Decoz. 11/22/33 are master numbers, not debts.
KARMIC_NUMBERS = {13, 14, 16, 19}

KARMIC_MEANINGS = {
    13: "Laziness in past life; must build discipline through hard work",
    14: "Abuse of freedom; must learn moderation and commitment",
    16: "Ego destruction; tower moments that rebuild on truth",
    19: "Abuse of power; must learn selflessness and independence",
}


def _raw_life_path(dob) -> int:
    """Return the pre-reduction sum for life path check."""
    m = reduce_number(dob.month)
    d = reduce_number(dob.day)
    y = reduce_number(sum(int(x) for x in str(dob.year)))
    return m + d + y


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    # Check each core position for karmic numbers BEFORE final reduction
    positions = {}

    # Life Path raw
    lp_raw = _raw_life_path(profile.dob)
    positions["life_path_raw"] = lp_raw

    # Birthday number raw (day of month — can be 13, 14, 16, 19 directly)
    positions["birthday_raw"] = profile.dob.day

    # Expression raw (if available from profile)
    # We check the final numbers for karmic presence
    checks = {
        "life_path": lp_raw,
        "birthday": profile.dob.day,
    }

    # If core numbers are provided, check their unreduced forms too
    if profile.expression:
        checks["expression"] = profile.expression
    if profile.soul_urge:
        checks["soul_urge"] = profile.soul_urge
    if profile.personality:
        checks["personality"] = profile.personality

    found = {}
    for pos, val in checks.items():
        if val in KARMIC_NUMBERS:
            found[pos] = {"number": val, "meaning": KARMIC_MEANINGS[val]}

    return SystemResult(
        id="karmic_debt",
        name="Karmic Debt Numbers",
        certainty="COMPUTED_STRICT",
        data={
            "positions_checked": list(checks.keys()),
            "raw_values": checks,
            "karmic_debts_found": found,
            "has_karmic_debt": len(found) > 0,
            "count": len(found),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Karmic Debt: 13, 14, 16, 19 appearing before reduction in core positions",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q3_GAPS"
    )
