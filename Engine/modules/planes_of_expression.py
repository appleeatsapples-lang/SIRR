"""Planes of Expression — COMPUTED_STRICT
Assigns each letter to one of 4 planes (Physical/Mental/Emotional/Intuitive).
For each plane: count letters, sum Pythagorean values, reduce.
Source: Hans Decoz, Planes of Expression article/book
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

PYTH = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

# Decoz letter-to-plane assignments (ChatGPT R2 recovery, verified)
PLANE_MAP = {
    'D': 'physical', 'E': 'physical', 'M': 'physical', 'W': 'physical',
    'A': 'mental', 'G': 'mental', 'H': 'mental', 'J': 'mental',
    'L': 'mental', 'N': 'mental', 'P': 'mental',
    'B': 'emotional', 'I': 'emotional', 'O': 'emotional', 'R': 'emotional',
    'S': 'emotional', 'T': 'emotional', 'X': 'emotional', 'Z': 'emotional',
    'C': 'intuitive', 'F': 'intuitive', 'K': 'intuitive', 'Q': 'intuitive',
    'U': 'intuitive', 'V': 'intuitive', 'Y': 'intuitive',
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    name = profile.subject.upper().replace(" ", "")

    planes = {
        "physical": {"count": 0, "sum": 0, "letters": []},
        "mental": {"count": 0, "sum": 0, "letters": []},
        "emotional": {"count": 0, "sum": 0, "letters": []},
        "intuitive": {"count": 0, "sum": 0, "letters": []},
    }

    for ch in name:
        plane = PLANE_MAP.get(ch)
        if plane and ch in PYTH:
            planes[plane]["count"] += 1
            planes[plane]["sum"] += PYTH[ch]
            planes[plane]["letters"].append(ch)

    total_letters = sum(p["count"] for p in planes.values())

    data = {"name_analyzed": profile.subject, "total_letters": total_letters}

    for plane_name in ("physical", "mental", "emotional", "intuitive"):
        p = planes[plane_name]
        root = reduce_number(p["sum"]) if p["sum"] > 0 else 0
        pct = round(p["count"] / total_letters * 100, 1) if total_letters > 0 else 0
        data[f"{plane_name}_count"] = p["count"]
        data[f"{plane_name}_sum"] = p["sum"]
        data[f"{plane_name}_root"] = root
        data[f"{plane_name}_pct"] = pct

    # Dominant plane
    counts = {pn: planes[pn]["count"] for pn in planes}
    dominant = max(counts, key=counts.get)
    data["dominant_plane"] = dominant

    return SystemResult(
        id="planes_of_expression",
        name="Planes of Expression",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Hans Decoz: Planes of Expression (Physical/Mental/Emotional/Intuitive)",
            "Letter assignments: Physical=D,E,M,W; Mental=A,G,H,J,L,N,P; Emotional=B,I,O,R,S,T,X,Z; Intuitive=C,F,K,Q,U,V,Y",
            "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.).",
        ],
        question="Q1_IDENTITY",
    )
