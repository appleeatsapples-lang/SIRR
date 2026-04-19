"""Tree of Life Path — LOOKUP_FIXED
Maps Life Path number to corresponding Sephirah on the Kabbalistic Tree of Life.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    cfg = constants["tree_of_life"]
    paths = cfg["paths"]

    life_path = profile.life_path
    lp_str = str(life_path)

    if lp_str in paths:
        sephirah_data = paths[lp_str]
    else:
        # Reduce to single digit for non-master numbers
        reduced = life_path
        while reduced > 9 and reduced not in (11, 22, 33):
            reduced = sum(int(d) for d in str(reduced))
        sephirah_data = paths.get(str(reduced), paths["9"])

    # Also map Expression number for secondary path
    expression = profile.expression
    expr_str = str(expression)
    if expr_str in paths:
        expr_sephirah = paths[expr_str]
    else:
        reduced_e = expression
        while reduced_e > 9 and reduced_e not in (11, 22, 33):
            reduced_e = sum(int(d) for d in str(reduced_e))
        expr_sephirah = paths.get(str(reduced_e), paths["9"])

    return SystemResult(
        id="tree_of_life",
        name="Tree of Life Path (Kabbalistic Sephirot)",
        certainty="LOOKUP_FIXED",
        data={
            "life_path_number": life_path,
            "primary_sephirah": sephirah_data["sephirah"],
            "primary_hebrew": sephirah_data["hebrew"],
            "primary_meaning": sephirah_data["meaning"],
            "primary_world": sephirah_data["world"],
            "expression_number": expression,
            "secondary_sephirah": expr_sephirah["sephirah"],
            "secondary_hebrew": expr_sephirah["hebrew"],
            "secondary_meaning": expr_sephirah["meaning"],
            "secondary_world": expr_sephirah["world"],
            "note": "Primary path from Life Path, secondary from Expression. Together they show the soul's journey on the Tree."
        },
        interpretation=f"Primary: {sephirah_data['sephirah']} ({sephirah_data['hebrew']}). Secondary: {expr_sephirah['sephirah']}.",
        constants_version=constants["version"],
        references=["Kabbalistic Tree of Life", "Sephirotic correspondences"],
        question="Q1_IDENTITY"
    )
