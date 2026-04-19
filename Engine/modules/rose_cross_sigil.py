"""Rose Cross Sigil — COMPUTED_STRICT
Traces a path on the Rose Cross lamen by mapping each letter of the name
to its position on the 22-petal rose (Hebrew letter correspondences).
The path shape reveals the sigil's geometric character.
Source: Golden Dawn Rose Cross ritual, Regardie's The Golden Dawn
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Rose Cross petal positions: Hebrew letters on 3 rings (3 mothers, 7 doubles, 12 simples)
# Latin → Hebrew phonetic mapping → petal position (angle in degrees)
PETAL_MAP = {
    'A':0,'B':16,'C':33,'D':49,'E':65,'F':82,'G':98,'H':114,
    'I':131,'J':131,'K':147,'L':163,'M':180,'N':196,'O':212,
    'P':229,'Q':245,'R':261,'S':278,'T':294,'U':310,'V':310,
    'W':327,'X':343,'Y':310,'Z':359,
}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.subject.upper()
    letters = [ch for ch in name if ch.isalpha()]

    path = []
    for ch in letters:
        angle = PETAL_MAP.get(ch, 0)
        path.append({"letter": ch, "petal_angle": angle})

    # Compute total angular travel
    total_travel = 0
    for i in range(1, len(path)):
        diff = abs(path[i]["petal_angle"] - path[i-1]["petal_angle"])
        if diff > 180:
            diff = 360 - diff
        total_travel += diff

    # Sigil spread (how much of the rose is covered)
    unique_angles = len(set(p["petal_angle"] for p in path))
    spread_pct = round(unique_angles / 26 * 100, 1)

    return SystemResult(
        id="rose_cross_sigil", name="Rose Cross Sigil",
        certainty="COMPUTED_STRICT",
        data={
            "name": profile.subject, "path_length": len(path),
            "total_angular_travel": total_travel,
            "unique_petals": unique_angles, "spread_pct": spread_pct,
            "path": path,
        },
        interpretation=None, constants_version=constants["version"],
        references=["Golden Dawn Rose Cross lamen: name letters traced on 22-petal rose"],
        question="Q1_IDENTITY"
    )
