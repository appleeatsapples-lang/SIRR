"""Bridge Numbers — COMPUTED_STRICT"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    lp = profile.life_path
    expr = profile.expression
    su = profile.soul_urge
    pers = profile.personality

    if not all([lp, expr, su, pers]):
        return SystemResult(
            id="bridges", name="Bridge Numbers",
            certainty="NEEDS_INPUT",
            data={"error": "Requires life_path, expression, soul_urge, personality in profile"},
            interpretation=None, constants_version=constants["version"],
            references=[], question="Q6_GROWTH"
        )

    # For bridge calculation, use root of expression (not master)
    expr_root = expr
    while expr_root > 9:
        expr_root = sum(int(d) for d in str(expr_root))

    bridges = {
        "lp_su": abs(lp - su),
        "lp_expr": abs(lp - expr_root),
        "lp_pers": abs(lp - pers),
        "expr_su": abs(expr_root - su),
        "expr_pers": abs(expr_root - pers),
        "su_pers": abs(su - pers),
    }

    # Find perfect alignments and maximum tensions
    perfect = [k for k, v in bridges.items() if v == 0]
    max_tension = max(bridges.values())
    tension_points = [k for k, v in bridges.items() if v == max_tension]

    return SystemResult(
        id="bridges",
        name="Bridge Numbers",
        certainty="COMPUTED_STRICT",
        data={
            "bridges": bridges,
            "perfect_alignments": perfect,
            "max_tension": max_tension,
            "tension_points": tension_points,
            "inputs_used": f"LP={lp}, Expr={expr}(root {expr_root}), SU={su}, Pers={pers}"
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Bridge = absolute difference between core numbers",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q6_GROWTH"
    )
