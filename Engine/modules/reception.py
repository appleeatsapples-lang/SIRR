"""Mutual Reception — COMPUTED_STRICT
Detects when two planets occupy each other's dignities, creating a
cooperative exchange that strengthens both.

Types of reception:
1. Domicile-Domicile: Planet A in B's sign AND B in A's sign (strongest)
2. Exaltation-Exaltation: Planet A in B's exaltation AND B in A's exaltation
3. Mixed: Domicile/Exaltation cross-reception

Also detects one-way "generosity" — where Planet A receives Planet B
but the reception is not mutual.

Sources: Bonatti (Liber Astronomiae), Lilly (Christian Astrology),
Al-Biruni (The Book of Instruction)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

DOMICILE = {
    "Sun": ["Leo"], "Moon": ["Cancer"],
    "Mercury": ["Gemini", "Virgo"], "Venus": ["Taurus", "Libra"],
    "Mars": ["Aries", "Scorpio"], "Jupiter": ["Sagittarius", "Pisces"],
    "Saturn": ["Capricorn", "Aquarius"],
}

EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo",
    "Venus": "Pisces", "Mars": "Capricorn", "Jupiter": "Cancer",
    "Saturn": "Libra",
}

TRADITIONAL = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def _planet_rules_sign(planet: str, sign: str) -> bool:
    return sign in DOMICILE.get(planet, [])


def _planet_exalted_in(planet: str, sign: str) -> bool:
    return EXALTATION.get(planet) == sign


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None, **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="reception", name="Mutual Reception",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q3_NATURE",
        )

    planets = natal_chart_data.get("planets", {})
    mutual_receptions = []
    generosities = []

    for i, pa in enumerate(TRADITIONAL):
        if pa not in planets:
            continue
        sign_a = planets[pa]["sign"]
        for pb in TRADITIONAL[i + 1:]:
            if pb not in planets:
                continue
            sign_b = planets[pb]["sign"]

            # Domicile mutual reception
            a_in_b_dom = _planet_rules_sign(pb, sign_a)
            b_in_a_dom = _planet_rules_sign(pa, sign_b)
            if a_in_b_dom and b_in_a_dom:
                mutual_receptions.append({
                    "pair": [pa, pb],
                    "type": "domicile",
                    "strength": "major",
                    "detail": f"{pa} in {sign_a} ({pb}'s sign), {pb} in {sign_b} ({pa}'s sign)",
                })
                continue

            # Exaltation mutual reception
            a_in_b_exalt = _planet_exalted_in(pb, sign_a)
            b_in_a_exalt = _planet_exalted_in(pa, sign_b)
            if a_in_b_exalt and b_in_a_exalt:
                mutual_receptions.append({
                    "pair": [pa, pb],
                    "type": "exaltation",
                    "strength": "moderate",
                    "detail": f"{pa} in {sign_a} ({pb}'s exaltation), {pb} in {sign_b} ({pa}'s exaltation)",
                })
                continue

            # Mixed reception (domicile + exaltation)
            if (a_in_b_dom and b_in_a_exalt) or (a_in_b_exalt and b_in_a_dom):
                rtype = "mixed_domicile_exaltation"
                mutual_receptions.append({
                    "pair": [pa, pb],
                    "type": rtype,
                    "strength": "moderate",
                    "detail": f"{pa} in {sign_a}, {pb} in {sign_b} — cross domicile/exaltation",
                })
                continue

            # One-way generosity (not mutual, but one planet receives the other)
            if a_in_b_dom or a_in_b_exalt:
                gtype = "domicile" if a_in_b_dom else "exaltation"
                generosities.append({
                    "receiver": pa,
                    "host": pb,
                    "type": gtype,
                    "detail": f"{pa} in {sign_a} — received by {pb} ({gtype})",
                })
            if b_in_a_dom or b_in_a_exalt:
                gtype = "domicile" if b_in_a_dom else "exaltation"
                generosities.append({
                    "receiver": pb,
                    "host": pa,
                    "type": gtype,
                    "detail": f"{pb} in {sign_b} — received by {pa} ({gtype})",
                })

    data = {
        "mutual_reception_count": len(mutual_receptions),
        "mutual_receptions": mutual_receptions,
        "generosity_count": len(generosities),
        "generosities": generosities,
    }

    return SystemResult(
        id="reception",
        name="Mutual Reception",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Bonatti, Liber Astronomiae — mutual reception types",
            "Lilly, Christian Astrology — reception and generosity",
        ],
        question="Q3_NATURE",
    )
