"""Gene Keys — Contemplative overlay on Human Design gates.
Maps each of the 64 HD gates to a Shadow/Gift/Siddhi triad,
organized into an 11-sphere Hologenetic Profile.

Source: Richard Rudd, *The Gene Keys: Embracing Your Higher Purpose* (Watkins, 2009).
COMPUTED_STRICT when HD data available, NEEDS_INPUT otherwise.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# (Shadow, Gift, Siddhi)
GENE_KEYS = {
    1:  ("Entropy", "Freshness", "Beauty"),
    2:  ("Dislocation", "Orientation", "Unity"),
    3:  ("Chaos", "Innovation", "Innocence"),
    4:  ("Intolerance", "Understanding", "Forgiveness"),
    5:  ("Impatience", "Patience", "Timelessness"),
    6:  ("Conflict", "Diplomacy", "Peace"),
    7:  ("Division", "Guidance", "Virtue"),
    8:  ("Mediocrity", "Style", "Exquisiteness"),
    9:  ("Inertia", "Determination", "Invincibility"),
    10: ("Self-Obsession", "Naturalness", "Being"),
    11: ("Obscurity", "Idealism", "Light"),
    12: ("Vanity", "Discrimination", "Purity"),
    13: ("Discord", "Discernment", "Empathy"),
    14: ("Compromise", "Competence", "Bounteousness"),
    15: ("Dullness", "Magnetism", "Florescence"),
    16: ("Indifference", "Versatility", "Mastery"),
    17: ("Opinion", "Far-Sightedness", "Omniscience"),
    18: ("Judgement", "Integrity", "Perfection"),
    19: ("Co-Dependence", "Sensitivity", "Sacrifice"),
    20: ("Superficiality", "Self-Assurance", "Presence"),
    21: ("Control", "Authority", "Valour"),
    22: ("Dishonour", "Graciousness", "Grace"),
    23: ("Complexity", "Simplicity", "Quintessence"),
    24: ("Addiction", "Invention", "Silence"),
    25: ("Constriction", "Acceptance", "Universal Love"),
    26: ("Pride", "Artfulness", "Invisibility"),
    27: ("Selfishness", "Altruism", "Selflessness"),
    28: ("Purposelessness", "Totality", "Immortality"),
    29: ("Half-Heartedness", "Commitment", "Devotion"),
    30: ("Desire", "Lightness", "Rapture"),
    31: ("Arrogance", "Leadership", "Humility"),
    32: ("Failure", "Preservation", "Veneration"),
    33: ("Forgetting", "Mindfulness", "Revelation"),
    34: ("Force", "Strength", "Majesty"),
    35: ("Hunger", "Adventure", "Boundlessness"),
    36: ("Turbulence", "Humanity", "Compassion"),
    37: ("Weakness", "Equality", "Tenderness"),
    38: ("Struggle", "Perseverance", "Honour"),
    39: ("Provocation", "Dynamism", "Liberation"),
    40: ("Exhaustion", "Resolve", "Divine Will"),
    41: ("Fantasy", "Anticipation", "Emanation"),
    42: ("Expectation", "Detachment", "Celebration"),
    43: ("Deafness", "Insight", "Epiphany"),
    44: ("Interference", "Teamwork", "Synarchy"),
    45: ("Dominance", "Synergy", "Communion"),
    46: ("Seriousness", "Delight", "Ecstasy"),
    47: ("Oppression", "Transmutation", "Transfiguration"),
    48: ("Inadequacy", "Resourcefulness", "Wisdom"),
    49: ("Reaction", "Revolution", "Rebirth"),
    50: ("Corruption", "Equilibrium", "Harmony"),
    51: ("Agitation", "Initiative", "Awakening"),
    52: ("Stress", "Restraint", "Stillness"),
    53: ("Immaturity", "Expansion", "Superabundance"),
    54: ("Greed", "Aspiration", "Ascension"),
    55: ("Victimisation", "Freedom", "Freedom"),
    56: ("Distraction", "Enrichment", "Intoxication"),
    57: ("Unease", "Intuition", "Clarity"),
    58: ("Dissatisfaction", "Vitality", "Bliss"),
    59: ("Dishonesty", "Intimacy", "Transparency"),
    60: ("Limitation", "Realism", "Justice"),
    61: ("Psychosis", "Inspiration", "Sanctity"),
    62: ("Intellect", "Precision", "Impeccability"),
    63: ("Doubt", "Inquiry", "Truth"),
    64: ("Confusion", "Imagination", "Illumination"),
}

# 11-sphere Hologenetic Profile: sphere → (side, planet)
SPHERE_MAP = {
    "lifes_work": ("personality", "Sun"),
    "evolution":  ("personality", "Earth"),
    "radiance":   ("personality", "Moon"),
    "purpose":    ("design", "Sun"),
    "attraction": ("design", "Earth"),
    "iq":         ("personality", "Mercury"),
    "eq":         ("personality", "Venus"),
    "sq":         ("design", "Jupiter"),
    "vocation":   ("personality", "Jupiter"),
    "culture":    ("personality", "Mars"),
    "pearl":      ("design", "Saturn"),
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    hd_data = kwargs.get("human_design_data")

    if hd_data is None or "error" in hd_data:
        return SystemResult(
            id="gene_keys",
            name="Gene Keys",
            certainty="NEEDS_INPUT",
            data={"error": "Requires human_design_data (run human_design first)"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    spheres = {}
    for sphere_name, (side, planet) in SPHERE_MAP.items():
        planet_data = hd_data[side][planet]
        gate = planet_data["gate"]
        line = planet_data["line"]
        shadow, gift, siddhi = GENE_KEYS[gate]
        spheres[sphere_name] = {
            "gate": gate,
            "line": line,
            "shadow": shadow,
            "gift": gift,
            "siddhi": siddhi,
        }

    # Activation Sequence (Golden Path part 1)
    activation_sequence = [
        spheres["lifes_work"]["gate"],
        spheres["evolution"]["gate"],
        spheres["radiance"]["gate"],
        spheres["purpose"]["gate"],
    ]

    # Venus Sequence (Golden Path part 2)
    venus_sequence = [
        spheres["eq"]["gate"],
        spheres["iq"]["gate"],
        spheres["attraction"]["gate"],
        spheres["sq"]["gate"],
    ]

    # Pearl Sequence (Golden Path part 3)
    pearl_sequence = [
        spheres["vocation"]["gate"],
        spheres["culture"]["gate"],
        spheres["pearl"]["gate"],
    ]

    lw = spheres["lifes_work"]
    evo = spheres["evolution"]
    purpose = spheres["purpose"]

    interpretation = (
        f"Your Life's Work (Gate {lw['gate']}) structures around the spectrum: "
        f"Shadow {lw['shadow']} → Gift {lw['gift']} → Siddhi {lw['siddhi']}. "
        f"Evolution sphere (Gate {evo['gate']}): from {evo['shadow']} toward {evo['gift']}. "
        f"Purpose sphere (Gate {purpose['gate']}): from {purpose['shadow']} toward {purpose['gift']}. "
        f"Activation Sequence (identity path): gates {', '.join(str(g) for g in activation_sequence)}. "
        f"Venus Sequence (relational path): gates {', '.join(str(g) for g in venus_sequence)}. "
        f"Pearl Sequence (material/vocation path): gates {', '.join(str(g) for g in pearl_sequence)}. "
        f"The Gene Keys framework treats these 64 gates as frequency spectra, not fixed traits. "
        f"Shadow patterns are not flaws to fix but densities to metabolize into their gift frequencies. "
        f"Contemplative engagement with the material — not mental analysis — is the recommended practice."
    )

    data = {
        "spheres": spheres,
        "activation_sequence": activation_sequence,
        "venus_sequence": venus_sequence,
        "pearl_sequence": pearl_sequence,
        "primary_shadow": lw["shadow"],
        "primary_gift": lw["gift"],
        "primary_siddhi": lw["siddhi"],
    }

    return SystemResult(
        id="gene_keys",
        name="Gene Keys",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interpretation,
        constants_version=constants["version"],
        references=[
            "Rudd, Richard — The Gene Keys: Embracing Your Higher Purpose (Watkins, 2009)",
            "Gene Keys Golden Path (Activation → Venus → Pearl sequences)",
            "SOURCE_TIER:C — Invented 2000s by Richard Rudd. Derived from Human Design. No classical lineage.",
        ],
        question="Q1_IDENTITY",
    )
