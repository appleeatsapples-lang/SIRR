"""Psychological Translation Layer — maps SIRR semantic patterns to
psychological vocabulary.  Additive only: never modifies engine output.

Called from runner.py after the semantic reading pipeline.  Reads
output["semantic_reading"] and injects output["psychological_mirror"].
"""


# ── Static Maps ─────────────────────────────────────────────────────────

PATTERN_MAP = {
    "split_crown": {
        "domain": "Identity Structure",
        "domain_ar": "هيكل الهوية",
        "classical_root": "Talawwun (Ibn Arabi, Al-Futuhat al-Makkiyya Ch.73 / Fusus al-Hikam, Chapter on Shu'ayb)",
        "classical_tooltip": (
            "In classical Sufi psychology, Talawwun is the dynamic fluctuation of the inner self, "
            "contrasted with Tamkin (fixed stability). While often initially experienced as instability, "
            "advanced frameworks recognize this active negotiation as a highly adaptive, complex identity "
            "structure reflecting a universe in constant motion."
        ),
        "secular_framing": (
            "Identity fluidity — holding competing self-concepts as an architectural feature, "
            "not a psychological deficiency. Comparable to Internal Family Systems multiplicity."
        ),
        "descriptor": (
            "Two self-concepts in active negotiation — high internal "
            "complexity, difficulty with singular identity labels."
        ),
        "descriptor_ar": (
            "مفهومان للذات في تفاوض مستمر — تعقيد داخلي عالٍ، "
            "وصعوبة في تبنّي هوية واحدة."
        ),
        "keywords": [
            "identity tension",
            "self-multiplicity",
            "contextual self",
            "unresolved integration",
        ],
    },
    "outlier_witness": {
        "domain": "Metacognitive Orientation",
        "domain_ar": "التوجه ما وراء المعرفي",
        "classical_root": "Sakshi-bhava (Vedic Witness Consciousness) / Purusha observing Prakriti (Samkhya)",
        "descriptor": (
            "Strong pattern-recognition orientation — the mind that "
            "stands outside a system to observe it."
        ),
        "descriptor_ar": (
            "ميل قوي نحو التعرّف على الأنماط — العقل الذي يقف "
            "خارج النظام ليراقبه."
        ),
        "keywords": [
            "metacognition",
            "systems thinking",
            "observer stance",
            "analytical distance",
        ],
    },
    "triple_gate": {
        "domain": "Systemic Concordance",
        "domain_ar": "التوافق المنظومي",
        "classical_root": "Tawafuq (Al-Buni, Ilm al-Huruf) / Samvada (Vedic cosmology)",
        "descriptor": (
            "Three independent value-frames converge — unusually coherent "
            "underlying structure across unrelated systems."
        ),
        "descriptor_ar": (
            "ثلاثة أُطر قيمية مستقلة تتقاطع — بنية داخلية متسقة "
            "بشكل غير معتاد عبر أنظمة غير مترابطة."
        ),
        "keywords": [
            "cross-system coherence",
            "structural integrity",
            "deep consistency",
        ],
    },
    "threshold_birth": {
        "domain": "Liminal Identity",
        "domain_ar": "الهوية العتبية",
        "classical_root": "Barzakh (Ibn Arabi, Al-Futuhat al-Makkiyya) / Sandhi/Sandhya (Vedic Jyotish)",
        "descriptor": (
            "Strong sensitivity to transitions and liminal periods — "
            "identity formation tied to threshold moments."
        ),
        "descriptor_ar": (
            "حساسية عالية تجاه مراحل الانتقال — تشكّل الهوية "
            "مرتبط بلحظات العتبة."
        ),
        "keywords": [
            "transition sensitivity",
            "liminal awareness",
            "change as identity marker",
        ],
    },
    "bifurcated_roots": {
        "domain": "Structural Foundation",
        "domain_ar": "الأساس الهيكلي",
        "classical_root": "Split_crown extension — name/birth axis divergence; no single classical term",
        "descriptor": (
            "Name-derived and birth-derived axes point to divergent organizing roots — "
            "foundational pull between linguistic and temporal structures."
        ),
        "descriptor_ar": (
            "المحاور المشتقة من الاسم والمولد تشير إلى جذور تنظيمية متباينة — "
            "شد أساسي بين البنى اللغوية والزمنية."
        ),
        "keywords": [
            "axis dissonance",
            "foundational tension",
            "cross-origin negotiation",
        ],
    },
    "echoed_name": {
        "domain": "Onomantic Resonance",
        "domain_ar": "الرنين الاسمي",
        "classical_root": "Tawafuq al-Huruf (Ilm al-Huruf) / Pythagorean Onomancy",
        "descriptor": (
            "Name structure repeats across independent systems — linguistic "
            "identity carries unusual signal density."
        ),
        "descriptor_ar": (
            "بنية الاسم تتكرر عبر أنظمة مستقلة — الهوية اللغوية "
            "تحمل كثافة إشارة غير معتادة."
        ),
        "keywords": [
            "expressive coherence",
            "verbal identity",
            "name-as-structure",
        ],
    },
    "dominant_current": {
        "domain": "Structural Concentration",
        "domain_ar": "التمركز البنيوي",
        "classical_root": "Wahda / Tawhid (Ibn Arabi, Al-Futuhat al-Makkiyya Ch.198) / Al-Buni (Shams al-Ma'arif)",
        "descriptor": (
            "When a single root number dominates five or more of the eight semantic axes, "
            "the reading shows unusual internal concentration around one organizing theme. "
            "The chart is less distributed and more unified: one pattern keeps returning "
            "across different parts of the profile."
        ),
        "descriptor_ar": (
            "عندما يهيمن رقم جذر واحد على خمسة أو أكثر من المحاور الدلالية الثمانية، "
            "فإن القراءة تُظهر تمركزًا داخليًا غير مألوف حول موضوع منظِّم واحد. "
            "تكون البنية هنا أقلّ تشتتًا وأكثر توحّدًا: إذ يستمر نمط واحد في الظهور "
            "عبر أجزاء مختلفة من الملف."
        ),
        "keywords": [
            "monothematic signal",
            "structural unity",
            "concentrated organizing principle",
            "axis dominance",
        ],
    },
}

ROOT_MAP = {
    1: {
        "domain": "Will & Individuation",
        "domain_ar": "الإرادة والتفرّد",
        "descriptor": (
            "Primary organizing axis: independent structure, self-directed "
            "initiation, singular focus under pressure."
        ),
        "descriptor_ar": (
            "المحور التنظيمي الأساسي: هيكل مستقل، انطلاق ذاتي التوجيه، "
            "تركيز منفرد تحت الضغط."
        ),
        "keywords": [
            "autonomy",
            "self-direction",
            "initiation",
            "structural independence",
        ],
    },
    3: {
        "domain": "Expression & Synthesis",
        "domain_ar": "التعبير والتوليف",
        "descriptor": (
            "Primary organizing axis: meaning-making through language, "
            "relational synthesis, expressive processing."
        ),
        "descriptor_ar": (
            "المحور التنظيمي الأساسي: صناعة المعنى من خلال اللغة، "
            "التوليف العلائقي، المعالجة التعبيرية."
        ),
        "keywords": [
            "expressive cognition",
            "relational meaning",
            "synthesis orientation",
            "communication-primary",
        ],
    },
}

CYCLIC_MAP = {
    "DORMANT": {
        "domain": "Temporal Orientation",
        "domain_ar": "التوجه الزمني",
        "descriptor": (
            "Current structural phase: internal consolidation — processing "
            "over output, depth over breadth."
        ),
        "descriptor_ar": (
            "المرحلة الهيكلية الحالية: تكثيف داخلي — المعالجة تسبق "
            "الإخراج، العمق يتقدم على الاتساع."
        ),
        "keywords": [
            "consolidation",
            "internalized processing",
            "integration phase",
        ],
    },
    "ACTIVE": {
        "domain": "Temporal Orientation",
        "domain_ar": "التوجه الزمني",
        "descriptor": (
            "Current structural phase: outward expression — high output "
            "readiness, external engagement dominant."
        ),
        "descriptor_ar": (
            "المرحلة الهيكلية الحالية: تعبير خارجي — استعداد عالٍ "
            "للإخراج، الانخراط الخارجي هو الغالب."
        ),
        "keywords": [
            "expression phase",
            "outward orientation",
            "high output",
        ],
    },
    "TRANSITIONAL": {
        "domain": "Temporal Orientation",
        "domain_ar": "التوجه الزمني",
        "descriptor": (
            "Current structural phase: in motion between consolidation and "
            "expression — instability as growth signal."
        ),
        "descriptor_ar": (
            "المرحلة الهيكلية الحالية: في حالة حركة بين التكثيف "
            "والتعبير — عدم الاستقرار إشارة نمو."
        ),
        "keywords": [
            "phase transition",
            "structural shift",
            "liminal timing",
        ],
    },
}


# ── Combination Rules ───────────────────────────────────────────────────

COMBINATION_RULES = [
    # ── 5-pattern: all fire (most specific — must be first) ────────────────
    {
        "requires": {
            "split_crown", "outlier_witness", "triple_gate",
            "threshold_birth", "echoed_name",
        },
        "reading": (
            "Every structural axis fires simultaneously: the name, birth geometry, "
            "and cognitive style converge on a coherent underlying architecture "
            "containing active internal multiplicity. The configuration presents "
            "cross-system alignment alongside unresolved integration of that alignment."
        ),
    },
    # ── 3-pattern combinations ─────────────────────────────────────────────
    {
        "requires": {"split_crown", "echoed_name", "threshold_birth"},
        "reading": (
            "A divided crown, born at the threshold, whose name echoes "
            "the fracture: identity tension is written into the name "
            "structure itself and activated most acutely at transition "
            "points. The split is not accidental — it is the signature."
        ),
    },
    {
        "requires": {"split_crown", "outlier_witness", "triple_gate"},
        "reading": (
            "A coherent structure observed from the outside by the one "
            "living it: deep cross-system consistency coexists with "
            "unresolved internal division. The architecture is sound. "
            "The resident is still negotiating which room is home."
        ),
    },
    # ── 2-pattern combinations ─────────────────────────────────────────────
    {
        "requires": {"split_crown", "outlier_witness"},
        "reading": (
            "The observer who watches their own division: a cognitive "
            "structure that maintains analytical distance from its own "
            "unresolved identity tension. High self-awareness does not "
            "resolve the split — it witnesses it."
        ),
    },
    {
        "requires": {"split_crown", "threshold_birth"},
        "reading": (
            "Identity division anchored in transition sensitivity: the "
            "split is not random but structurally tied to liminal moments. "
            "Change events are where the two self-concepts surface most "
            "visibly."
        ),
    },
    {
        "requires": {"split_crown", "triple_gate"},
        "reading": (
            "Internal division within an externally coherent structure: "
            "three independent frameworks converge on the same signal, "
            "yet the self that carries that signal remains split. "
            "Structural coherence and personal integration are separate "
            "projects — the first is already complete; the second is the "
            "ongoing work."
        ),
    },
    {
        "requires": {"outlier_witness", "triple_gate"},
        "reading": (
            "Pattern-recognition operating across a coherent structural "
            "field: the observer stance is not imposed on chaos — it is "
            "applied to an unusually consistent underlying architecture."
        ),
    },
    {
        "requires": {"echoed_name", "triple_gate"},
        "reading": (
            "Linguistic and structural coherence reinforce each other: "
            "name carries the same signal as birth-derived axes. Expression "
            "is not separate from structure — it is the structure made "
            "audible."
        ),
    },
    {
        "requires": {"threshold_birth", "echoed_name"},
        "reading": (
            "Born at the threshold, the name echoes across boundaries: "
            "linguistic identity and temporal sensitivity are structurally "
            "linked. The name is not just a label — it is a record of "
            "the liminal moment it was given into."
        ),
    },
    {
        "requires": {"outlier_witness", "echoed_name"},
        "reading": (
            "The witness from the outside hears their own name echoed "
            "back: pattern-recognition turns inward and finds the self "
            "as a recurring signal. The observer and the observed share "
            "the same frequency."
        ),
    },
]

FALLBACK_LINK = (
    "Together, these patterns describe complementary axes "
    "of the same structural picture."
)

CONSTITUTIONAL_NOTE = (
    "This translation does not replace the esoteric output. It offers "
    "a second vocabulary for the same structural facts. The engine "
    "computes. The mirror reflects. Interpretation belongs to the subject. "
    "This is one structural vocabulary layer only. It contains no clinical, "
    "predictive, or experiential claims. Interpretation and application "
    "remain solely with the subject."
)
CONSTITUTIONAL_NOTE_AR = (
    "المحرّك يحسب. والمرآةُ تعكس. أمّا التأويلُ فمردّه إلى صاحبِه. "
    "هذا طبقة هيكلية واحدة فقط. لا يحتوي على أي ادعاءات تشخيصية أو تنبؤية أو تجريبية."
)


# ── Core Logic ──────────────────────────────────────────────────────────

def _extract_cyclic_state(semantic_reading: dict) -> str:
    """Pull cyclic activation_state from sections list."""
    for section in semantic_reading.get("sections", []):
        if section.get("axis") == "cyclic":
            return section.get("activation_state") or "TRANSITIONAL"
    return "TRANSITIONAL"


def _compute_convergence_reading(fired_ids: set) -> str:
    """Find best-matching combination rule (most-specific first)."""
    # Rules are ordered most-specific first in COMBINATION_RULES
    for rule in COMBINATION_RULES:
        if rule["requires"].issubset(fired_ids):
            return rule["reading"]

    # Fallback: concatenate individual descriptors
    parts = []
    for pid in sorted(fired_ids):
        entry = PATTERN_MAP.get(pid)
        if entry:
            parts.append(entry["descriptor"])
    if parts:
        return " ".join(parts) + " " + FALLBACK_LINK
    return FALLBACK_LINK


def build_psychological_mirror(semantic_reading: dict) -> dict:
    """Build the psychological_mirror dict from semantic_reading data."""
    # 1. Fired patterns
    fired_raw = semantic_reading.get("meta_patterns_fired", [])
    fired_ids = {p["pattern_id"] for p in fired_raw if p.get("fired")}

    fired_patterns = []
    for p in fired_raw:
        pid = p.get("pattern_id", "")
        if not p.get("fired") or pid not in PATTERN_MAP:
            continue
        entry = PATTERN_MAP[pid]
        fired_patterns.append({
            "pattern_id": pid,
            "domain": entry["domain"],
            "domain_ar": entry.get("domain_ar", ""),
            "classical_root": entry.get("classical_root", ""),
            "descriptor": entry["descriptor"],
            "descriptor_ar": entry.get("descriptor_ar", ""),
            "keywords": entry["keywords"],
        })

    # 1b. Auto-detect bifurcated_roots: fires when name/digit axes use a different root
    # than the sky/elemental axes — the classic split_crown root-origin signal.
    sections = semantic_reading.get("sections", [])
    name_digit_roots = {
        s["dominant_root"] for s in sections
        if s.get("axis") in ("digit", "derived") and s.get("dominant_root")
    }
    sky_elemental_roots = {
        s["dominant_root"] for s in sections
        if s.get("axis") in ("sky", "elemental", "archetypal") and s.get("dominant_root")
    }
    roots_diverge = bool(name_digit_roots and sky_elemental_roots and
                         not name_digit_roots.intersection(sky_elemental_roots))
    if roots_diverge and "bifurcated_roots" not in fired_ids:
        entry = PATTERN_MAP["bifurcated_roots"]
        fired_ids.add("bifurcated_roots")
        fired_patterns.append({
            "pattern_id": "bifurcated_roots",
            "domain": entry["domain"],
            "domain_ar": entry.get("domain_ar", ""),
            "classical_root": entry.get("classical_root", ""),
            "descriptor": entry["descriptor"],
            "descriptor_ar": entry.get("descriptor_ar", ""),
            "keywords": entry["keywords"],
        })

    # 2. Dominant root
    root = semantic_reading.get("dominant_cross_root")
    root_entry = ROOT_MAP.get(root, ROOT_MAP.get(1))  # default to 1
    dominant_root_translation = {
        "root": root if root in ROOT_MAP else 1,
        "domain": root_entry["domain"],
        "domain_ar": root_entry.get("domain_ar", ""),
        "descriptor": root_entry["descriptor"],
        "descriptor_ar": root_entry.get("descriptor_ar", ""),
        "keywords": root_entry["keywords"],
    }

    # 3. Cyclic state
    cyclic_state = _extract_cyclic_state(semantic_reading)
    cyclic_entry = CYCLIC_MAP.get(cyclic_state, CYCLIC_MAP["TRANSITIONAL"])
    cyclic_translation = {
        "state": cyclic_state,
        "domain": cyclic_entry["domain"],
        "domain_ar": cyclic_entry.get("domain_ar", ""),
        "descriptor": cyclic_entry["descriptor"],
        "descriptor_ar": cyclic_entry.get("descriptor_ar", ""),
        "keywords": cyclic_entry["keywords"],
    }

    # 4. Convergence reading (combination logic)
    convergence_reading = _compute_convergence_reading(fired_ids)

    return {
        "fired_patterns": fired_patterns,
        "dominant_root_translation": dominant_root_translation,
        "cyclic_translation": cyclic_translation,
        "convergence_reading": convergence_reading,
        "constitutional_note": CONSTITUTIONAL_NOTE,
        "constitutional_note_ar": CONSTITUTIONAL_NOTE_AR,
    }


def inject_psychological_mirror(output: dict) -> dict:
    """Top-level entry point: reads output, injects psychological_mirror key.

    READ-ONLY against all existing output keys.  Only adds a new top-level key.
    """
    semantic = output.get("semantic_reading")
    if not semantic or "error" in semantic:
        output["psychological_mirror"] = {
            "error": "semantic_reading unavailable — skipping translation"
        }
        return output

    output["psychological_mirror"] = build_psychological_mirror(semantic)
    return output
