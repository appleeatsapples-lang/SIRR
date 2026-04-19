"""Psychological Construct Layer — maps SIRR engine output to
research-backed psychological dimensions.

Additive only: never modifies engine output.  Reads output["results"],
output["semantic_reading"], output["synthesis"], and injects
output["psychological_profile"].

Maps to 28 constructs:
  v1 (1-8): Big Five, SPS, Sensation Seeking, Psychological Flexibility,
            Rumination, Cognitive Style, Stress Response, Attachment
  v2 (9-28): Defense Mechanisms, Emotional Regulation, Self-Determination,
             Shadow Profile, Interpersonal Circumplex, Perfectionism,
             Locus of Control, Time Perspective, Moral Foundations,
             Flow State, Communication Style, Resilience, Creativity,
             Motivation, Procrastination, Conflict Style, Learning Style,
             Moral Identity, Maslow Needs, Impostor Profile

All mappings are STRUCTURAL TENDENCIES derived from cross-tradition
pattern agreement — not psychometric measurements.  No clinical
diagnoses are made or implied.

References for each construct cite the foundational research paper
so the mapping rationale is transparent.

Called from runner.py after the psychological_mirror layer.
"""
from __future__ import annotations


# ── Constitutional Disclaimer ──────────────────────────────────────────

DISCLAIMER = (
    "STRUCTURAL TENDENCY PROFILE — NOT A CLINICAL ASSESSMENT. "
    "These mappings translate cross-tradition structural patterns into "
    "research-backed psychological vocabulary.  They are NOT psychometric "
    "measurements, clinical diagnoses, or personality test results.  "
    "No SIRR output should be used for clinical, diagnostic, employment, "
    "or legal purposes.  The engine computes structural reflections.  "
    "Interpretation and application belong solely to the subject.  "
    "For psychological assessment, consult a licensed professional."
)
DISCLAIMER_AR = (
    "ملف الميول البنيوية — ليس تقييمًا سريريًا. "
    "هذه التعيينات تترجم الأنماط البنيوية عبر التقاليد إلى مفردات نفسية "
    "مستندة إلى البحث العلمي. وهي ليست قياسات نفسية أو تشخيصات سريرية أو "
    "نتائج اختبارات شخصية. لا ينبغي استخدام أي مخرج من محرك سر لأغراض "
    "سريرية أو تشخيصية أو وظيفية أو قانونية. التأويل والتطبيق ملك للشخص وحده."
)


# ── Helper: safe extraction from results list ──────────────────────────

def _find_result(results: list[dict], module_id: str) -> dict | None:
    """Find a module result by id in the results array."""
    for r in results:
        if r.get("id") == module_id:
            return r.get("data", {})
    return None


def _clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, val))


# ── Big Five Mapping ───────────────────────────────────────────────────

def _map_big_five(results: list[dict], semantic: dict, synthesis: dict) -> dict:
    """Map SIRR structural patterns to Big Five tendency indicators.

    Each trait is scored 0.0–1.0 (low–high tendency).
    Mapping rationale documented per trait.
    """
    scores = {}

    # ── Openness to Experience ──
    # High when: many convergences (cross-system pattern recognition),
    # dominant_current fires (monothematic = deep focus on one domain),
    # void_matrix has high torque (asymmetric void = unconventional structure),
    # inclusion_table has few missing digits (broad expressive range).
    openness_signals = []

    vm = _find_result(results, "void_matrix")
    if vm:
        torque = vm.get("torque", 0)
        openness_signals.append(_clamp(torque / 8.0))  # torque 0-8 → 0-1

    incl = _find_result(results, "inclusion_table")
    if incl:
        missing = len(incl.get("missing_digits", []))
        openness_signals.append(_clamp(1.0 - missing / 5.0))  # fewer missing = more open

    fired_ids = _extract_fired_ids(semantic)
    if "outlier_witness" in fired_ids:
        openness_signals.append(0.85)
    if "dominant_current" in fired_ids:
        openness_signals.append(0.75)

    convergence_count = synthesis.get("convergence_count", 0)
    openness_signals.append(_clamp(convergence_count / 20.0))

    scores["openness"] = {
        "score": round(_mean(openness_signals), 2) if openness_signals else 0.5,
        "label": "Openness to Experience",
        "reference": "Costa & McCrae (1992). NEO-PI-R Professional Manual.",
        "mapping_rationale": (
            "High torque (void asymmetry), outlier_witness pattern (observer stance), "
            "broad expressive range (few missing digits), and cross-system convergence "
            "all indicate structural openness to varied frameworks."
        ),
    }

    # ── Conscientiousness ──
    # High when: barzakh coefficient is high (fixed > kinetic = structure-dominant),
    # triple_gate fires (cross-system coherence = internal consistency),
    # lo_shu missing digits are few (complete structure).
    consc_signals = []

    barz = _find_result(results, "barzakh_coefficient")
    if barz:
        coeff = barz.get("coefficient", 0.5)
        consc_signals.append(_clamp(coeff))

    if "triple_gate" in fired_ids:
        consc_signals.append(0.80)

    lo_shu = _find_result(results, "lo_shu_grid")
    if lo_shu:
        missing = len(lo_shu.get("missing", []))
        consc_signals.append(_clamp(1.0 - missing / 6.0))

    scores["conscientiousness"] = {
        "score": round(_mean(consc_signals), 2) if consc_signals else 0.5,
        "label": "Conscientiousness",
        "reference": "Costa & McCrae (1992). NEO-PI-R Professional Manual.",
        "mapping_rationale": (
            "High barzakh coefficient (structural dominance over temporal flux), "
            "triple_gate (cross-system coherence), and complete Lo Shu grid "
            "(few structural gaps) indicate organized, consistent architecture."
        ),
    }

    # ── Extraversion ──
    # High when: biorhythm physical+emotional are high (energy output),
    # cyclic state is ACTIVE, planes_of_expression emotional plane is dominant,
    # timing consensus is EXPANSIVE.
    extra_signals = []

    bio = _find_result(results, "biorhythm")
    if bio:
        phys = abs(bio.get("physical_pct", 0))
        emot = abs(bio.get("emotional_pct", 0))
        extra_signals.append(_clamp((phys + emot) / 200.0))

    planes = _find_result(results, "planes_of_expression")
    if planes:
        emotional_pct = planes.get("emotional_pct", 0)
        extra_signals.append(_clamp(emotional_pct / 50.0))

    timing = _find_result(results, "timing_consensus")
    if timing:
        consensus = timing.get("consensus", "")
        if consensus == "EXPANSIVE":
            extra_signals.append(0.75)
        elif consensus == "CONTRACTIVE":
            extra_signals.append(0.25)
        else:
            extra_signals.append(0.50)

    cyclic_state = _extract_cyclic_state(semantic)
    if cyclic_state == "ACTIVE":
        extra_signals.append(0.80)
    elif cyclic_state == "DORMANT":
        extra_signals.append(0.25)
    else:
        extra_signals.append(0.50)

    scores["extraversion"] = {
        "score": round(_mean(extra_signals), 2) if extra_signals else 0.5,
        "label": "Extraversion",
        "reference": "Costa & McCrae (1992). NEO-PI-R Professional Manual.",
        "mapping_rationale": (
            "Biorhythm energy output, emotional plane expression percentage, "
            "timing consensus direction (expansive vs contractive), and cyclic "
            "activation state map to outward-directed energy."
        ),
    }

    # ── Agreeableness ──
    # High when: element consensus includes Water (relational element),
    # enneagram type is relational (2, 6, 9),
    # temperament is phlegmatic or sanguine.
    agree_signals = []

    elem = _find_result(results, "element_consensus")
    if elem:
        consensus_elem = elem.get("consensus_element", "")
        if consensus_elem == "Water":
            agree_signals.append(0.80)
        elif consensus_elem == "Earth":
            agree_signals.append(0.60)
        elif consensus_elem == "Air":
            agree_signals.append(0.55)
        else:  # Fire
            agree_signals.append(0.35)

    enn = _find_result(results, "enneagram_dob")
    if enn:
        etype = enn.get("enneagram_type", 0)
        agree_map = {1: 0.45, 2: 0.85, 3: 0.40, 4: 0.50, 5: 0.35,
                     6: 0.70, 7: 0.55, 8: 0.30, 9: 0.85}
        agree_signals.append(agree_map.get(etype, 0.50))

    temp = _find_result(results, "temperament")
    if temp:
        prim = temp.get("primary_temperament", "").lower().lower()
        temp_map = {"phlegmatic": 0.80, "sanguine": 0.70, "melancholic": 0.45, "choleric": 0.30}
        agree_signals.append(temp_map.get(prim, 0.50))

    scores["agreeableness"] = {
        "score": round(_mean(agree_signals), 2) if agree_signals else 0.5,
        "label": "Agreeableness",
        "reference": "Costa & McCrae (1992). NEO-PI-R Professional Manual.",
        "mapping_rationale": (
            "Element consensus (Water = relational), enneagram type affiliation "
            "tendencies, and classical temperament (phlegmatic/sanguine = cooperative) "
            "map to interpersonal orientation."
        ),
    }

    # ── Neuroticism (Emotional Reactivity) ──
    # High when: split_crown fires (unresolved identity tension),
    # threshold_birth fires (transition sensitivity),
    # vimshottari is malefic (temporal stress),
    # void_center is true (structural gap at center).
    neuro_signals = []

    if "split_crown" in fired_ids:
        neuro_signals.append(0.70)
    if "threshold_birth" in fired_ids:
        neuro_signals.append(0.60)

    if vm and vm.get("void_center"):
        neuro_signals.append(0.60)

    vim = _find_result(results, "vimshottari")
    if vim:
        quality = vim.get("period_quality", "")
        if quality == "malefic":
            neuro_signals.append(0.70)
        elif quality == "benefic":
            neuro_signals.append(0.30)
        else:
            neuro_signals.append(0.50)

    scores["neuroticism"] = {
        "score": round(_mean(neuro_signals), 2) if neuro_signals else 0.5,
        "label": "Neuroticism (Emotional Reactivity)",
        "reference": "Costa & McCrae (1992). NEO-PI-R Professional Manual.",
        "mapping_rationale": (
            "Split crown (unresolved identity tension), threshold birth (transition "
            "sensitivity), void center (structural gap), and malefic dasha period "
            "indicate heightened emotional reactivity potential."
        ),
    }

    return scores


# ── Standalone Construct Mappings ──────────────────────────────────────

def _map_sensory_processing_sensitivity(results: list[dict], semantic: dict) -> dict:
    """Sensory Processing Sensitivity (Aron & Aron, 1997).
    High SPS = deep processing, overstimulation susceptibility, emotional reactivity,
    sensitivity to subtleties.
    """
    signals = []
    fired_ids = _extract_fired_ids(semantic)

    # Outlier_witness → depth of processing (observes subtleties others miss)
    if "outlier_witness" in fired_ids:
        signals.append(0.80)

    # Threshold_birth → sensitivity to environmental transitions
    if "threshold_birth" in fired_ids:
        signals.append(0.75)

    # Void center → structural sensitivity (absence as felt presence)
    vm = _find_result(results, "void_matrix")
    if vm and vm.get("void_center"):
        signals.append(0.70)

    # Nine star ki: 4 (Wood) year star = sensitivity to growth/change
    nsk = _find_result(results, "nine_star_ki")
    if nsk:
        year_star = nsk.get("year_star", 0)
        if year_star in (4, 2):  # Wood, Earth — receptive stars
            signals.append(0.70)

    # High barzakh = deep structural processing
    barz = _find_result(results, "barzakh_coefficient")
    if barz:
        coeff = barz.get("coefficient", 0.5)
        if coeff > 0.80:
            signals.append(0.70)

    return {
        "score": round(_mean(signals), 2) if signals else 0.5,
        "label": "Sensory Processing Sensitivity",
        "reference": "Aron, E.N. & Aron, A. (1997). Sensory-processing sensitivity and its relation to introversion and emotionality. JPSP, 73(2), 345-368.",
        "mapping_rationale": (
            "Observer stance (outlier_witness), transition sensitivity (threshold_birth), "
            "void center (felt absence), high barzakh (deep structural processing), and "
            "receptive Nine Star Ki map to the SPS construct of depth of processing."
        ),
    }


def _map_sensation_seeking(results: list[dict], semantic: dict) -> dict:
    """Sensation Seeking (Zuckerman, 1994).
    High SS = need for novel, varied, complex sensations; willingness to take risks.
    """
    signals = []
    fired_ids = _extract_fired_ids(semantic)

    # Rahu dasha → amplified ambition, attraction to the unfamiliar
    vim = _find_result(results, "vimshottari")
    if vim:
        dasha = vim.get("current_maha_dasha", "")
        if dasha == "Rahu":
            signals.append(0.75)
        elif dasha in ("Ketu", "Saturn"):
            signals.append(0.30)
        else:
            signals.append(0.50)

    # Soul urge 5 → freedom, variety, change
    # (We read from profile via the output, not directly)
    bio = _find_result(results, "biorhythm")
    if bio:
        phys = abs(bio.get("physical_pct", 0))
        signals.append(_clamp(phys / 100.0))

    # Enneagram 7 or 3 = sensation/achievement seeking
    enn = _find_result(results, "enneagram_dob")
    if enn:
        etype = enn.get("enneagram_type", 0)
        ss_map = {1: 0.30, 2: 0.40, 3: 0.65, 4: 0.55, 5: 0.35,
                  6: 0.30, 7: 0.90, 8: 0.75, 9: 0.20}
        signals.append(ss_map.get(etype, 0.50))

    # Timing EXPANSIVE → outward reaching
    timing = _find_result(results, "timing_consensus")
    if timing:
        if timing.get("consensus") == "EXPANSIVE":
            signals.append(0.70)
        elif timing.get("consensus") == "CONTRACTIVE":
            signals.append(0.30)

    return {
        "score": round(_mean(signals), 2) if signals else 0.5,
        "label": "Sensation Seeking",
        "reference": "Zuckerman, M. (1994). Behavioral expressions and biosocial bases of sensation seeking. Cambridge University Press.",
        "mapping_rationale": (
            "Rahu dasha (attraction to unfamiliar), biorhythm physical energy, "
            "enneagram type approach to novelty, and timing consensus direction "
            "map to the SS-V construct of need for novel experience."
        ),
    }


def _map_psychological_flexibility(results: list[dict], semantic: dict) -> dict:
    """Psychological Flexibility (Hayes et al., 2006; ACT framework).
    High PF = ability to contact present moment fully, change/persist as needed.
    """
    signals = []
    fired_ids = _extract_fired_ids(semantic)

    # Triple_gate → structural coherence across independent frames (integration)
    if "triple_gate" in fired_ids:
        signals.append(0.80)

    # Dominant_current → strong organizing principle = internal stability
    if "dominant_current" in fired_ids:
        signals.append(0.70)

    # Split_crown → active negotiation (can be flexible IF integrated)
    if "split_crown" in fired_ids:
        signals.append(0.55)  # Ambiguous: tension can go either way

    # Barzakh: balanced (0.4-0.6) = most flexible; extremes = rigid
    barz = _find_result(results, "barzakh_coefficient")
    if barz:
        coeff = barz.get("coefficient", 0.5)
        # Distance from 0.5 center → less flexible
        flex = 1.0 - abs(coeff - 0.5) * 2.0
        signals.append(_clamp(flex))

    # Few convergences might mean high flexibility (not locked into one pattern)
    # Many convergences might mean structural rigidity
    # This is genuinely ambiguous — score neutrally
    signals.append(0.50)

    return {
        "score": round(_mean(signals), 2) if signals else 0.5,
        "label": "Psychological Flexibility",
        "reference": "Hayes, S.C., Luoma, J.B., Bond, F.W., Masuda, A., & Lillis, J. (2006). Acceptance and Commitment Therapy: Model, processes and outcomes. Behaviour Research and Therapy, 44(1), 1-25.",
        "mapping_rationale": (
            "Triple gate (cross-framework integration), barzakh balance (structural vs "
            "temporal flexibility), and dominant current (organizing coherence) indicate "
            "capacity to hold complexity while maintaining functional direction."
        ),
    }


def _map_rumination_index(results: list[dict], semantic: dict) -> dict:
    """Rumination tendency (Nolen-Hoeksema & Morrow, 1991).
    High = repetitive focus on distress causes/consequences.
    """
    signals = []
    fired_ids = _extract_fired_ids(semantic)

    # Split crown → unresolved identity tension invites ruminative processing
    if "split_crown" in fired_ids:
        signals.append(0.75)

    # Bifurcated roots → structural pull between axes → mental circling
    if "bifurcated_roots" in fired_ids:
        signals.append(0.70)

    # Void center → absence at center → existential questioning
    vm = _find_result(results, "void_matrix")
    if vm and vm.get("void_center"):
        signals.append(0.65)

    # Malefic timing → temporal stress amplifies ruminative tendency
    vim = _find_result(results, "vimshottari")
    if vim:
        if vim.get("period_quality") == "malefic":
            signals.append(0.65)
        elif vim.get("period_quality") == "benefic":
            signals.append(0.30)

    # DORMANT cyclic state → internalized processing can become rumination
    cyclic = _extract_cyclic_state(semantic)
    if cyclic == "DORMANT":
        signals.append(0.70)
    elif cyclic == "ACTIVE":
        signals.append(0.30)
    else:
        signals.append(0.50)

    # High mental plane % → cognitive over-processing
    planes = _find_result(results, "planes_of_expression")
    if planes:
        mental_pct = planes.get("mental_pct", 0)
        signals.append(_clamp(mental_pct / 50.0))

    return {
        "score": round(_mean(signals), 2) if signals else 0.5,
        "label": "Rumination Index",
        "reference": "Nolen-Hoeksema, S. & Morrow, J. (1991). A prospective study of depression and posttraumatic stress symptoms after a natural disaster. JPSP, 61(1), 115-121.",
        "mapping_rationale": (
            "Split crown (unresolved tension), bifurcated roots (cross-axis pull), "
            "void center (felt absence), malefic timing, dormant cyclic state, and "
            "high mental plane percentage all contribute to repetitive cognitive processing."
        ),
    }


def _map_cognitive_style(results: list[dict], semantic: dict) -> dict:
    """Cognitive Style: Analytic vs Holistic (Nisbett et al., 2001).
    Score >0.5 = more analytic; <0.5 = more holistic.
    """
    signals = []
    fired_ids = _extract_fired_ids(semantic)

    # Outlier_witness → analytic (stands outside to observe patterns)
    if "outlier_witness" in fired_ids:
        signals.append(0.80)

    # Triple_gate → holistic (sees convergence across frames)
    if "triple_gate" in fired_ids:
        signals.append(0.35)

    # Dominant_current → analytic (monothematic focus)
    if "dominant_current" in fired_ids:
        signals.append(0.70)

    # Mental plane dominant → analytic processing
    planes = _find_result(results, "planes_of_expression")
    if planes:
        dom = planes.get("dominant_plane", "")
        style_map = {"mental": 0.80, "intuitive": 0.35, "emotional": 0.40, "physical": 0.55}
        signals.append(style_map.get(dom, 0.50))

    # Enneagram: 5,1 = analytic; 9,4,2 = holistic
    enn = _find_result(results, "enneagram_dob")
    if enn:
        etype = enn.get("enneagram_type", 0)
        cog_map = {1: 0.75, 2: 0.35, 3: 0.60, 4: 0.40, 5: 0.90,
                   6: 0.55, 7: 0.45, 8: 0.65, 9: 0.30}
        signals.append(cog_map.get(etype, 0.50))

    score = round(_mean(signals), 2) if signals else 0.50
    style_label = "analytic" if score > 0.6 else "holistic" if score < 0.4 else "integrated"

    return {
        "score": score,
        "style": style_label,
        "label": "Cognitive Style (Analytic–Holistic)",
        "reference": "Nisbett, R.E., Peng, K., Choi, I., & Norenzayan, A. (2001). Culture and systems of thought: Holistic versus analytic cognition. Psychological Review, 108(2), 291-310.",
        "mapping_rationale": (
            "Outlier witness and dominant current favor analytic processing; "
            "triple gate favors holistic integration; mental plane dominance "
            "and enneagram type add specificity."
        ),
    }


def _map_stress_response(results: list[dict], semantic: dict) -> dict:
    """Stress Response Pattern: fight/flight/freeze/fawn tendency.
    Based on structural indicators, not clinical measurement.
    """
    # Compute tendency scores for each response
    fight = 0.0
    flight = 0.0
    freeze = 0.0
    fawn = 0.0
    n_signals = 0

    fired_ids = _extract_fired_ids(semantic)

    # Dominant root 1 → fight (autonomy, self-direction, initiation)
    sections = semantic.get("sections", [])
    dominant_roots = [s.get("dominant_root") for s in sections if s.get("dominant_root")]
    if dominant_roots:
        from collections import Counter
        root_freq = Counter(dominant_roots)
        dom_root = root_freq.most_common(1)[0][0]
        root_stress = {
            1: ("fight", 0.7), 3: ("flight", 0.5), 4: ("freeze", 0.5),
            5: ("flight", 0.6), 7: ("freeze", 0.7), 8: ("fight", 0.6),
            9: ("fawn", 0.5), 2: ("fawn", 0.6), 6: ("fawn", 0.6),
        }
        mode, val = root_stress.get(dom_root, ("fight", 0.5))
        if mode == "fight": fight += val
        elif mode == "flight": flight += val
        elif mode == "freeze": freeze += val
        else: fawn += val
        n_signals += 1

    # Temperament mapping
    temp = _find_result(results, "temperament")
    if temp:
        prim = temp.get("primary_temperament", "").lower()
        t_map = {"choleric": ("fight", 0.7), "sanguine": ("flight", 0.6),
                 "melancholic": ("freeze", 0.6), "phlegmatic": ("fawn", 0.6)}
        mode, val = t_map.get(prim, ("fight", 0.5))
        if mode == "fight": fight += val
        elif mode == "flight": flight += val
        elif mode == "freeze": freeze += val
        else: fawn += val
        n_signals += 1

    # Enneagram stress directions
    enn = _find_result(results, "enneagram_dob")
    if enn:
        etype = enn.get("enneagram_type", 0)
        e_map = {1: ("fight", 0.6), 2: ("fawn", 0.7), 3: ("fight", 0.5),
                 4: ("freeze", 0.6), 5: ("flight", 0.7), 6: ("freeze", 0.5),
                 7: ("flight", 0.6), 8: ("fight", 0.8), 9: ("fawn", 0.7)}
        mode, val = e_map.get(etype, ("fight", 0.5))
        if mode == "fight": fight += val
        elif mode == "flight": flight += val
        elif mode == "freeze": freeze += val
        else: fawn += val
        n_signals += 1

    responses = {"fight": fight, "flight": flight, "freeze": freeze, "fawn": fawn}
    primary = max(responses, key=responses.get) if n_signals > 0 else "fight"
    total = sum(responses.values()) or 1.0
    normalized = {k: round(v / total, 2) for k, v in responses.items()}

    return {
        "primary_response": primary,
        "distribution": normalized,
        "label": "Stress Response Tendency",
        "reference": "Walker, P. (2013). Complex PTSD: From Surviving to Thriving. Azure Coyote Publishing. / Porges, S.W. (2011). The Polyvagal Theory. Norton.",
        "mapping_rationale": (
            "Dominant root (1/8=fight, 5/7=flight/freeze), temperament (choleric=fight, "
            "phlegmatic=fawn), and enneagram stress patterns indicate structural "
            "stress-response tendency."
        ),
    }


def _map_attachment_tendency(results: list[dict], semantic: dict) -> dict:
    """Attachment Tendency (Bartholomew & Horowitz, 1991).
    Maps to secure/anxious-preoccupied/dismissive-avoidant/fearful-avoidant.
    """
    # Score dimensions: self-model (positive/negative) x other-model (positive/negative)
    self_positive = 0.0
    other_positive = 0.0
    n_self = 0
    n_other = 0

    fired_ids = _extract_fired_ids(semantic)

    # Triple gate → positive self-model (internal coherence = self-trust)
    if "triple_gate" in fired_ids:
        self_positive += 0.75
        n_self += 1

    # Dominant current → positive self-model (clear organizing principle)
    if "dominant_current" in fired_ids:
        self_positive += 0.70
        n_self += 1

    # Split crown → negative self-model (unresolved identity = self-doubt)
    if "split_crown" in fired_ids:
        self_positive += 0.30
        n_self += 1

    # Barzakh high → positive self (structural solidity)
    barz = _find_result(results, "barzakh_coefficient")
    if barz:
        coeff = barz.get("coefficient", 0.5)
        self_positive += _clamp(coeff)
        n_self += 1

    # Element consensus Water → positive other-model (relational orientation)
    elem = _find_result(results, "element_consensus")
    if elem:
        consensus_elem = elem.get("consensus_element", "")
        other_map = {"Water": 0.80, "Earth": 0.60, "Air": 0.55, "Fire": 0.35}
        other_positive += other_map.get(consensus_elem, 0.50)
        n_other += 1

    # Enneagram relational types
    enn = _find_result(results, "enneagram_dob")
    if enn:
        etype = enn.get("enneagram_type", 0)
        # Other-model: 2,6,9 = positive other; 5,8,4 = negative other
        other_map_e = {1: 0.45, 2: 0.85, 3: 0.50, 4: 0.40, 5: 0.30,
                       6: 0.65, 7: 0.60, 8: 0.35, 9: 0.80}
        other_positive += other_map_e.get(etype, 0.50)
        n_other += 1

    # Agreeableness proxy: temperament
    temp = _find_result(results, "temperament")
    if temp:
        prim = temp.get("primary_temperament", "").lower()
        other_t = {"phlegmatic": 0.75, "sanguine": 0.70, "melancholic": 0.40, "choleric": 0.35}
        other_positive += other_t.get(prim, 0.50)
        n_other += 1

    self_avg = self_positive / n_self if n_self > 0 else 0.5
    other_avg = other_positive / n_other if n_other > 0 else 0.5

    # Bartholomew quadrant
    if self_avg > 0.5 and other_avg > 0.5:
        style = "secure"
    elif self_avg <= 0.5 and other_avg > 0.5:
        style = "anxious-preoccupied"
    elif self_avg > 0.5 and other_avg <= 0.5:
        style = "dismissive-avoidant"
    else:
        style = "fearful-avoidant"

    return {
        "style": style,
        "self_model": round(self_avg, 2),
        "other_model": round(other_avg, 2),
        "label": "Attachment Tendency",
        "reference": "Bartholomew, K. & Horowitz, L.M. (1991). Attachment styles among young adults: A test of a four-category model. JPSP, 61(2), 226-244.",
        "mapping_rationale": (
            "Self-model: triple gate/dominant current (coherence→trust) vs split crown "
            "(tension→doubt); barzakh (structural solidity). Other-model: element consensus "
            "(Water→relational), enneagram relational type, temperament warmth."
        ),
    }


# ── Utility Functions ──────────────────────────────────────────────────

def _extract_fired_ids(semantic: dict) -> set:
    """Extract set of fired pattern IDs from semantic_reading."""
    fired_raw = semantic.get("meta_patterns_fired", [])
    return {p["pattern_id"] for p in fired_raw if p.get("fired")}


def _extract_cyclic_state(semantic: dict) -> str:
    for section in semantic.get("sections", []):
        if section.get("axis") == "cyclic":
            return section.get("activation_state") or "TRANSITIONAL"
    return "TRANSITIONAL"


def _extract_dominant_root(semantic: dict) -> int:
    """Get the most common dominant_root across all axes."""
    from collections import Counter
    roots = [s.get("dominant_root") for s in semantic.get("sections", [])
             if s.get("dominant_root")]
    if not roots:
        return 1
    return Counter(roots).most_common(1)[0][0]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.5


def _make_construct(score, label, reference, rationale, lived, **extra):
    """Standard construct dict factory.

    Defensively clamps `score` to [0.0, 1.0] so callers can't accidentally
    produce out-of-range scores via unclamped len/div arithmetic. All psych
    constructs are tendency indicators on a 0-1 scale; any score outside
    that range would be a bug (e.g. Einstein shadow_profile=1.17 on
    2026-04-17, caused by len(shadows)/6.0 overflow).

    Adds scholarship_fidelity="SCIENTIFIC_PSYCH_CONSTRUCT" automatically
    (all constructs going through this factory are empirically-anchored
    per §4.2 of the Scholarship Fidelity schema). The `reference` field
    carries the empirical provenance; `scholarship_note` flags the
    "tendency, not clinical assessment" frame that's standing policy.
    """
    clamped = _clamp(float(score), 0.0, 1.0) if isinstance(score, (int, float)) else 0.5
    d = {"score": round(clamped, 2), "label": label, "reference": reference,
         "mapping_rationale": rationale, "lived_description": lived,
         # §4.2 structured label — enables downstream filter for empirical dims
         "scholarship_fidelity": "SCIENTIFIC_PSYCH_CONSTRUCT",
         "scholarship_note": (
             "Tendency indicator mapped from symbolic inputs to an empirical "
             "psych construct. See `reference` for construct provenance. "
             "Standing disclaimer: structural tendency, not clinical assessment."
         )}
    d.update(extra)
    return d

def _normalize_psych_meta(profile: dict) -> dict:
    """Ensure every psych construct dict carries the correct §4.2 scholarship label.

    Two distinct labels per §4.2:
      - SCIENTIFIC_PSYCH_CONSTRUCT (27 dims): empirically-anchored constructs
        with peer-reviewed provenance (Costa-McCrae, Zuckerman, Gross,
        Bowlby, Wiggins, Haidt, Csikszentmihalyi, Aquino-Reed, etc.)
      - MODERN_SYNTHESIS (1 dim currently): Jungian/depth-psych constructs.
        Shadow Profile is the only member; per §4.2 "Jungian/Freudian/
        archetypal frameworks are academically recognized but non-empirical —
        construct validity is philosophical, not factor-analytic."

    Enables downstream consumers to filter by provenance:
        empirical = [v for v in profile.values()
                     if isinstance(v, dict)
                     and v.get("scholarship_fidelity") == "SCIENTIFIC_PSYCH_CONSTRUCT"]
    """
    # Dims that are Jungian depth psychology, not empirical constructs.
    # shadow_profile: Jung 1951 (Aion). Any future core_wound, dream_psyche,
    # or archetype_sketch additions should be added here.
    _DEPTH_PSYCH_DIMS = frozenset({"shadow_profile"})

    empirical_meta = {
        "scholarship_fidelity": "SCIENTIFIC_PSYCH_CONSTRUCT",
        "scholarship_note": (
            "Tendency indicator mapped from symbolic inputs to an empirical "
            "psych construct. See `reference` for construct provenance. "
            "Standing disclaimer: structural tendency, not clinical assessment."
        ),
    }
    depth_meta = {
        "scholarship_fidelity": "MODERN_SYNTHESIS",
        "scholarship_note": (
            "Jungian/depth-psychology construct. Academically recognized "
            "(analytical psychology is a legitimate school) but non-empirical; "
            "construct validity is philosophical, not factor-analytic. "
            "Standing disclaimer: structural tendency, not clinical assessment."
        ),
    }
    for key, val in list(profile.items()):
        if not isinstance(val, dict):
            continue
        meta = depth_meta if key in _DEPTH_PSYCH_DIMS else empirical_meta
        if key == "big_five":
            # big_five is a container of 5 sub-constructs — all empirical (Costa-McCrae)
            for sub in val.values():
                if isinstance(sub, dict):
                    # Always overwrite (possibly-stale factory output with correct label)
                    sub.update(empirical_meta)
        else:
            # Always overwrite so depth-psych dims get correctly relabeled even
            # if the factory already added SCIENTIFIC_PSYCH_CONSTRUCT.
            val.update(meta)
    return profile



# ── V2 Construct Mappings (9–28) ──────────────────────────────────────

def _map_defense_mechanisms(results, semantic):
    """Vaillant (1977) defense maturity spectrum: mature / neurotic / immature."""
    fired = _extract_fired_ids(semantic)
    signals = []
    # triple_gate = sublimation (mature — channeling into coherent structure)
    if "triple_gate" in fired: signals.append(0.80)
    # outlier_witness = intellectualization (neurotic — observer distance)
    if "outlier_witness" in fired: signals.append(0.60)
    # split_crown = splitting (immature — identity fragmentation)
    if "split_crown" in fired: signals.append(0.35)
    # dominant_current = rationalization (neurotic — everything explained by one frame)
    if "dominant_current" in fired: signals.append(0.55)
    # barzakh high = suppression (mature — conscious delay of response)
    barz = _find_result(results, "barzakh_coefficient")
    if barz and barz.get("coefficient", 0) > 0.80: signals.append(0.75)

    score = _mean(signals)
    if score > 0.65: level = "predominantly mature"
    elif score > 0.45: level = "neurotic range"
    else: level = "immature range"
    return _make_construct(score,
        "Defense Mechanism Maturity",
        "Vaillant, G.E. (1977). Adaptation to Life. Little, Brown.",
        "triple_gate→sublimation, outlier_witness→intellectualization, split_crown→splitting, high barzakh→suppression.",
        f"Structural defenses operate at the {level} level: internal tension is managed through "
        f"{'coherent channeling and delayed response' if score > 0.65 else 'analytical distance and rationalization' if score > 0.45 else 'fragmentation and avoidance'}.",
        level=level)


def _map_emotional_regulation(results, semantic):
    """Gross (2002) process model: reappraisal vs suppression tendency."""
    signals = []
    fired = _extract_fired_ids(semantic)
    # triple_gate = reappraisal (reframing across systems)
    if "triple_gate" in fired: signals.append(0.80)
    # dominant_current = focused reappraisal (one organizing frame)
    if "dominant_current" in fired: signals.append(0.70)
    # barzakh high = suppression tendency (fixed structure over kinetic expression)
    barz = _find_result(results, "barzakh_coefficient")
    if barz:
        coeff = barz.get("coefficient", 0.5)
        signals.append(1.0 - coeff)  # high barzakh = LOW reappraisal
    # biorhythm emotional amplitude
    bio = _find_result(results, "biorhythm")
    if bio:
        emot = abs(bio.get("emotional_pct", 0))
        signals.append(_clamp(1.0 - emot / 100.0))  # calm = high regulation

    score = _mean(signals)
    style = "reappraisal-dominant" if score > 0.55 else "suppression-dominant"
    _detail = ('Reframes emotional experience through structural understanding — '
               'feelings are processed as information.') if score > 0.55 else (
               'Manages affect through structural containment — '
               'emotional experience is bounded rather than reframed.')
    return _make_construct(score,
        "Emotional Regulation Strategy",
        "Gross, J.J. (2002). Emotion regulation: Affective, cognitive, and social consequences. Psychophysiology, 39(3), 281-291.",
        "triple_gate/dominant_current→reappraisal, high barzakh→suppression, emotional biorhythm amplitude.",
        f"Tends toward {style}. {_detail}",
        style=style)


def _map_self_determination(results, semantic):
    """Deci & Ryan (2000) SDT: autonomy, competence, relatedness."""
    fired = _extract_fired_ids(semantic)
    autonomy = []
    competence = []
    relatedness = []
    # Root 1 dominant = autonomy
    dom_root = _extract_dominant_root(semantic)
    if dom_root == 1: autonomy.append(0.85)
    elif dom_root in (3, 6): relatedness.append(0.70)
    # triple_gate = competence (structural mastery)
    if "triple_gate" in fired: competence.append(0.80)
    # dominant_current = autonomy (self-organizing)
    if "dominant_current" in fired: autonomy.append(0.75)
    # Element consensus
    elem = _find_result(results, "element_consensus")
    if elem:
        ce = elem.get("consensus_element", "")
        if ce == "Fire": autonomy.append(0.70)
        elif ce == "Water": relatedness.append(0.70)
        elif ce == "Earth": competence.append(0.65)
    # HD type
    hd = _find_result(results, "human_design")
    if hd:
        t = hd.get("type", "")
        if "Generator" in t: competence.append(0.75)
        if "Manifestor" in t or "Manifesting" in t: autonomy.append(0.75)
        if "Projector" in t: relatedness.append(0.70)

    a, c, r = _mean(autonomy), _mean(competence), _mean(relatedness)
    primary = max([("autonomy", a), ("competence", c), ("relatedness", r)], key=lambda x: x[1])
    return _make_construct(_mean([a, c, r]),
        "Self-Determination Needs",
        "Deci, E.L. & Ryan, R.M. (2000). The 'what' and 'why' of goal pursuits. Psychological Inquiry, 11(4), 227-268.",
        "Root 1→autonomy, triple_gate→competence, element Water→relatedness, HD type mapping.",
        f"Primary need: {primary[0]}. {'Driven by independence and self-direction.' if primary[0] == 'autonomy' else 'Driven by mastery and effective functioning.' if primary[0] == 'competence' else 'Driven by meaningful connection.'}",
        autonomy=round(a, 2), competence=round(c, 2), relatedness=round(r, 2),
        primary_need=primary[0])


def _map_shadow_profile(results, semantic):
    """Jung (1951) shadow: repressed/underdeveloped aspects from structural gaps."""
    shadows = []
    vm = _find_result(results, "void_matrix")
    if vm:
        if vm.get("void_center"): shadows.append("center-absence: difficulty resting in stillness or 'just being'")
        absent = vm.get("semantic_absent", [])
        if "stillness_devotion" in absent: shadows.append("suppressed contemplative capacity")
        if "praise_recognition" in absent: shadows.append("discomfort receiving acknowledgment")
    incl = _find_result(results, "inclusion_table")
    if incl:
        missing = incl.get("missing_digits", [])
        digit_shadow = {7: "withdrawal and solitary reflection", 4: "sustained routine and patient effort",
                        5: "embodied spontaneity", 8: "material authority and power assertion"}
        for d in missing:
            if d in digit_shadow: shadows.append(f"missing-{d}: {digit_shadow[d]}")
    gk = _find_result(results, "gene_keys")
    if gk:
        sh = gk.get("primary_shadow", "")
        if sh: shadows.append(f"Gene Keys shadow: {sh}")

    return _make_construct(_clamp(len(shadows) / 8.0) if shadows else 0.3,
        "Shadow Profile",
        "Jung, C.G. (1951). Aion: Researches into the Phenomenology of the Self. CW 9ii.",
        "void_matrix absences, inclusion_table missing digits, Gene Keys primary shadow.",
        f"Shadow material includes: {'; '.join(shadows[:4]) if shadows else 'minimal structural shadow detected'}.",
        shadow_elements=shadows[:6])


def _map_interpersonal_circumplex(results, semantic):
    """Wiggins (1979) IPC: agency (dominance) vs communion (warmth) axes."""
    agency = []
    communion = []
    fired = _extract_fired_ids(semantic)
    dom_root = _extract_dominant_root(semantic)
    if dom_root == 1: agency.append(0.80)
    if dom_root in (2, 6): communion.append(0.75)
    if "dominant_current" in fired: agency.append(0.70)
    if "outlier_witness" in fired: agency.append(0.60)
    elem = _find_result(results, "element_consensus")
    if elem:
        ce = elem.get("consensus_element", "")
        if ce == "Fire": agency.append(0.75)
        elif ce == "Water": communion.append(0.75)
    enn = _find_result(results, "enneagram_dob")
    if enn:
        t = enn.get("enneagram_type", 0)
        if t in (3, 8, 1): agency.append(0.70)
        elif t in (2, 9, 6): communion.append(0.70)
    a, c = _mean(agency), _mean(communion)
    if a > 0.55 and c > 0.55: octant = "assured-dominant"
    elif a > 0.55 and c <= 0.55: octant = "arrogant-calculating"
    elif a <= 0.55 and c > 0.55: octant = "warm-agreeable"
    else: octant = "unassured-submissive"
    return _make_construct(_mean([a, c]),
        "Interpersonal Circumplex Position",
        "Wiggins, J.S. (1979). A psychological taxonomy of trait-descriptive terms. JRSP, 13, 395-412.",
        "Root 1→agency, element Water→communion, enneagram type, meta-pattern stance.",
        f"Interpersonal style: {octant}. {'Projects competence and directedness; may underweight collaborative signals.' if a > c else 'Leads with warmth and attunement; may underweight assertive capacity.'}",
        agency=round(a, 2), communion=round(c, 2), octant=octant)


def _map_perfectionism(results, semantic):
    """Hewitt & Flett (1991): self-oriented vs other-oriented vs socially prescribed."""
    fired = _extract_fired_ids(semantic)
    self_oriented = []
    # triple_gate = high internal standards (cross-system coherence pursuit)
    if "triple_gate" in fired: self_oriented.append(0.80)
    if "dominant_current" in fired: self_oriented.append(0.70)
    barz = _find_result(results, "barzakh_coefficient")
    if barz and barz.get("coefficient", 0) > 0.80: self_oriented.append(0.75)
    enn = _find_result(results, "enneagram_dob")
    if enn:
        t = enn.get("enneagram_type", 0)
        if t == 1: self_oriented.append(0.90)
        elif t == 3: self_oriented.append(0.75)
        elif t in (9, 7): self_oriented.append(0.30)
    score = _mean(self_oriented) if self_oriented else 0.5
    return _make_construct(score,
        "Perfectionism Tendency",
        "Hewitt, P.L. & Flett, G.L. (1991). Perfectionism in the self and social contexts. JPSP, 60(3), 456-470.",
        "triple_gate→internal standards, barzakh→structural rigidity, enneagram 1/3→perfectionistic.",
        f"{'High self-oriented perfectionism: demands internal coherence and structural completeness. Standards are internally generated, not externally imposed.' if score > 0.65 else 'Moderate perfectionism: standards are present but flexible.' if score > 0.45 else 'Low perfectionism: comfortable with incompleteness.'}",
        subtype="self-oriented")


def _map_locus_of_control(results, semantic):
    """Rotter (1966) LOC: internal vs external."""
    signals = []
    fired = _extract_fired_ids(semantic)
    dom_root = _extract_dominant_root(semantic)
    if dom_root == 1: signals.append(0.85)  # Root 1 = self-directed
    if dom_root in (2, 6, 9): signals.append(0.35)  # relational = external
    if "dominant_current" in fired: signals.append(0.75)
    barz = _find_result(results, "barzakh_coefficient")
    if barz:
        coeff = barz.get("coefficient", 0.5)
        signals.append(_clamp(coeff))  # structural dominance = internal
    hd = _find_result(results, "human_design")
    if hd:
        t = hd.get("type", "")
        if "Manifestor" in t or "Manifesting" in t: signals.append(0.80)
        elif "Projector" in t: signals.append(0.45)
        elif "Reflector" in t: signals.append(0.30)
    score = _mean(signals)
    loc = "internal" if score > 0.55 else "external"
    return _make_construct(score,
        "Locus of Control",
        "Rotter, J.B. (1966). Generalized expectancies for internal versus external control of reinforcement. Psychological Monographs, 80(1), 1-28.",
        "Root 1→internal, barzakh→structural solidity, HD Manifestor→internal, Reflector→external.",
        f"{'Strong internal locus: attributes outcomes to personal agency and structural architecture. May underestimate contextual forces.' if score > 0.65 else 'Balanced locus: reads both personal and contextual causation.' if score > 0.45 else 'External locus: sensitive to environmental and relational forces shaping outcomes.'}",
        orientation=loc)


def _map_time_perspective(results, semantic):
    """Zimbardo & Boyd (1999) ZTPI: past/present/future orientation."""
    past, present, future = [], [], []
    fired = _extract_fired_ids(semantic)
    if "threshold_birth" in fired: past.append(0.70)  # birth-anchored
    cyclic = _extract_cyclic_state(semantic)
    if cyclic == "DORMANT": past.append(0.65)
    elif cyclic == "ACTIVE": present.append(0.70)
    else: future.append(0.60)
    vim = _find_result(results, "vimshottari")
    if vim:
        d = vim.get("current_maha_dasha", "")
        if d == "Rahu": future.append(0.75)  # Rahu = future-amplified ambition
        elif d == "Ketu": past.append(0.70)  # Ketu = past-karmic
        elif d in ("Saturn",): present.append(0.60)
    barz = _find_result(results, "barzakh_coefficient")
    if barz and barz.get("coefficient", 0) > 0.75: past.append(0.55)  # fixed = past-structured
    p, pr, f = _mean(past), _mean(present), _mean(future)
    primary = max([("past", p), ("present", pr), ("future", f)], key=lambda x: x[1])
    return _make_construct(_mean([p, pr, f]),
        "Time Perspective",
        "Zimbardo, P.G. & Boyd, J.N. (1999). Putting time in perspective: A valid, reliable individual-differences metric. JPSP, 77(6), 1271-1288.",
        "threshold_birth→past, Rahu dasha→future, ACTIVE cyclic→present, barzakh→fixed/past.",
        f"Primary orientation: {primary[0]}. {'The past serves as an organizing reference — identity is anchored in origin structures.' if primary[0] == 'past' else 'Attention lives in the present moment — responsiveness over planning.' if primary[0] == 'present' else 'Future-oriented — current patterns read as trajectories toward becoming.'}",
        past=round(p, 2), present=round(pr, 2), future=round(f, 2), primary_orientation=primary[0])


def _map_moral_foundations(results, semantic):
    """Haidt (2012) MFT: care/fairness/loyalty/authority/sanctity."""
    care, fairness, loyalty, authority, sanctity = 0.5, 0.5, 0.5, 0.5, 0.5
    elem = _find_result(results, "element_consensus")
    if elem:
        ce = elem.get("consensus_element", "")
        if ce == "Water": care = 0.75
        elif ce == "Earth": loyalty = 0.70; authority = 0.65
        elif ce == "Fire": authority = 0.70; fairness = 0.65
        elif ce == "Air": fairness = 0.75
    fired = _extract_fired_ids(semantic)
    if "triple_gate" in fired: fairness = max(fairness, 0.75)  # structural coherence = fairness sensitivity
    if "dominant_current" in fired: authority = max(authority, 0.70)
    enn = _find_result(results, "enneagram_dob")
    if enn:
        t = enn.get("enneagram_type", 0)
        if t == 1: fairness = max(fairness, 0.80)
        elif t == 2: care = max(care, 0.80)
        elif t == 6: loyalty = max(loyalty, 0.80)
    vm = _find_result(results, "void_matrix")
    if vm and vm.get("void_center"): sanctity = max(sanctity, 0.65)
    foundations = {"care": round(care, 2), "fairness": round(fairness, 2),
                   "loyalty": round(loyalty, 2), "authority": round(authority, 2),
                   "sanctity": round(sanctity, 2)}
    primary = max(foundations, key=foundations.get)
    return _make_construct(_mean(list(foundations.values())),
        "Moral Foundations",
        "Haidt, J. (2012). The Righteous Mind: Why Good People Are Divided by Politics and Religion. Vintage.",
        "Element consensus→care/fairness/loyalty, enneagram type moral sensitivity, meta-patterns.",
        f"Strongest foundation: {primary}. Moral intuitions are most activated by "
        f"{'harm and suffering' if primary == 'care' else 'injustice and cheating' if primary == 'fairness' else 'betrayal and group cohesion' if primary == 'loyalty' else 'subversion and tradition' if primary == 'authority' else 'degradation and purity'}.",
        foundations=foundations, primary_foundation=primary)


def _map_flow_state(results, semantic):
    """Csikszentmihalyi (1990): structural indicators of flow-proneness."""
    signals = []
    fired = _extract_fired_ids(semantic)
    if "triple_gate" in fired: signals.append(0.80)  # coherence = clear goals
    if "dominant_current" in fired: signals.append(0.75)  # focused attention
    if "outlier_witness" in fired: signals.append(0.70)  # immediate feedback loop (pattern detection)
    bio = _find_result(results, "biorhythm")
    if bio:
        phys = abs(bio.get("physical_pct", 0))
        intl = abs(bio.get("intellectual_pct", 0))
        signals.append(_clamp((phys + intl) / 200.0))
    hd = _find_result(results, "human_design")
    if hd:
        t = hd.get("type", "")
        if "Generator" in t: signals.append(0.80)  # sacral energy = sustained flow
        elif "Projector" in t: signals.append(0.60)
    return _make_construct(_mean(signals),
        "Flow State Proneness",
        "Csikszentmihalyi, M. (1990). Flow: The Psychology of Optimal Experience. Harper & Row.",
        "triple_gate→clear goals, dominant_current→focused attention, HD Generator→sustained energy.",
        ("High flow-proneness: structural architecture supports deep absorption — clear internal goals, "
         "feedback-responsive pattern recognition, and sustained energy.") if _mean(signals) > 0.65 else "Moderate flow access: flow states are available but may require deliberate environmental structuring.",
        )


def _map_communication_style(results, semantic):
    """Norton (1978) communicator style: dominant/dramatic/open/precise/relaxed."""
    planes = _find_result(results, "planes_of_expression")
    dom_root = _extract_dominant_root(semantic)
    fired = _extract_fired_ids(semantic)
    styles = {"dominant": 0.0, "dramatic": 0.0, "precise": 0.0, "open": 0.0, "relaxed": 0.0}
    if dom_root == 1: styles["dominant"] += 0.7
    elif dom_root == 3: styles["dramatic"] += 0.7; styles["open"] += 0.5
    if "outlier_witness" in fired: styles["precise"] += 0.7
    if "dominant_current" in fired: styles["dominant"] += 0.5
    if planes:
        dp = planes.get("dominant_plane", "")
        if dp == "mental": styles["precise"] += 0.6
        elif dp == "emotional": styles["dramatic"] += 0.6; styles["open"] += 0.5
        elif dp == "physical": styles["relaxed"] += 0.6
        elif dp == "intuitive": styles["open"] += 0.6
    nw = _find_result(results, "name_weight")
    if nw:
        cad = nw.get("cadence", "")
        if cad == "heavy": styles["dominant"] += 0.4
        elif cad == "light": styles["relaxed"] += 0.4
    primary = max(styles, key=styles.get)
    total = sum(styles.values()) or 1.0
    norm = {k: round(v / total, 2) for k, v in styles.items()}
    return _make_construct(max(styles.values()) / 2.0,
        "Communication Style",
        "Norton, R.W. (1978). Foundation of a communicator style construct. Human Communication Research, 4(2), 99-112.",
        "Root→dominance, planes→precision/drama, name_weight cadence→weight, outlier_witness→precision.",
        f"Primary style: {primary}. {'Communicates through structured, information-dense delivery — precision over performance.' if primary == 'precise' else 'Leads with presence and authority — message carries through force of conviction.' if primary == 'dominant' else 'Expressive and engaging — ideas arrive wrapped in narrative and affect.' if primary == 'dramatic' else 'Shares readily and transparently — low filtering between thought and speech.' if primary == 'open' else 'Calm, unhurried delivery — creates space for others to fill.'}",
        primary_style=primary, distribution=norm)


def _map_resilience(results, semantic):
    """Connor & Davidson (2003) CD-RISC domains: competence, trust, tolerance, control, spirituality."""
    signals = []
    fired = _extract_fired_ids(semantic)
    if "triple_gate" in fired: signals.append(0.80)  # structural coherence under complexity
    if "dominant_current" in fired: signals.append(0.70)
    barz = _find_result(results, "barzakh_coefficient")
    if barz: signals.append(_clamp(barz.get("coefficient", 0.5)))  # structural solidity
    if "threshold_birth" in fired: signals.append(0.65)  # familiarity with transitions
    timing = _find_result(results, "timing_consensus")
    if timing:
        if timing.get("consensus") == "EXPANSIVE": signals.append(0.70)
        elif timing.get("consensus") == "CONTRACTIVE": signals.append(0.40)
    return _make_construct(_mean(signals),
        "Resilience Capacity",
        "Connor, K.M. & Davidson, J.R.T. (2003). Development of a new resilience scale (CD-RISC). Depression and Anxiety, 18(2), 76-82.",
        "triple_gate→structural coherence, barzakh→solidity, threshold_birth→transition familiarity.",
        f"{'High structural resilience: architecture holds under pressure through internal coherence and transition familiarity.' if _mean(signals) > 0.65 else 'Moderate resilience: structural supports exist but may be tested during contractive timing phases.'}",
        )


def _map_creativity(results, semantic):
    """Kaufman (2012) domains of creativity: scholarly, performance, mechanical, self/everyday."""
    signals = []
    fired = _extract_fired_ids(semantic)
    if "outlier_witness" in fired: signals.append(0.80)  # divergent perspective
    vm = _find_result(results, "void_matrix")
    if vm:
        torque = vm.get("torque", 0)
        signals.append(_clamp(torque / 8.0))  # asymmetry = unconventionality
    if "bifurcated_roots" in fired: signals.append(0.70)  # tension as creative fuel
    incl = _find_result(results, "inclusion_table")
    if incl:
        dom_freq = incl.get("dominant_frequency", 0)
        signals.append(_clamp(dom_freq / 20.0))  # concentrated expressive energy
    # sonority curve
    son = _find_result(results, "sonority_curve")
    if son:
        entropy = son.get("rises", 0) + son.get("falls", 0)
        signals.append(_clamp(entropy / 20.0))  # phonetic variation = expressive range

    planes = _find_result(results, "planes_of_expression")
    domain = "scholarly"
    if planes:
        dp = planes.get("dominant_plane", "")
        if dp == "intuitive": domain = "self/everyday"
        elif dp == "emotional": domain = "performance"
        elif dp == "physical": domain = "mechanical"
    return _make_construct(_mean(signals),
        "Creative Potential",
        "Kaufman, J.C. (2012). Counting the muses: Development of the Kaufman Domains of Creativity Scale. Psychology of Aesthetics, Creativity, and the Arts, 6(4), 298-308.",
        "outlier_witness→divergent thinking, torque→unconventionality, bifurcated_roots→creative tension.",
        f"Primary creative domain: {domain}. {'Creativity expresses through intellectual synthesis and pattern recombination — the scholar-maker.' if domain == 'scholarly' else 'Creative energy channels through embodied or performative expression.'}",
        primary_domain=domain)


def _map_motivation(results, semantic):
    """McClelland (1961) needs: achievement, affiliation, power."""
    ach, aff, pwr = [], [], []
    fired = _extract_fired_ids(semantic)
    dom_root = _extract_dominant_root(semantic)
    if dom_root == 1: pwr.append(0.75)
    elif dom_root == 3: aff.append(0.65)
    if "triple_gate" in fired: ach.append(0.80)
    if "dominant_current" in fired: pwr.append(0.65); ach.append(0.65)
    enn = _find_result(results, "enneagram_dob")
    if enn:
        t = enn.get("enneagram_type", 0)
        if t == 3: ach.append(0.85)
        elif t == 8: pwr.append(0.85)
        elif t in (2, 9): aff.append(0.75)
    hd = _find_result(results, "human_design")
    if hd:
        t = hd.get("type", "")
        if "Manifestor" in t or "Manifesting" in t: pwr.append(0.70)
        elif "Generator" in t: ach.append(0.70)
    a, af, p = _mean(ach), _mean(aff), _mean(pwr)
    primary = max([("achievement", a), ("affiliation", af), ("power", p)], key=lambda x: x[1])
    return _make_construct(_mean([a, af, p]),
        "Motivational Profile",
        "McClelland, D.C. (1961). The Achieving Society. Van Nostrand.",
        "Root→power/affiliation, enneagram 3→achievement, HD type→drive orientation.",
        f"Primary motive: {primary[0]}. {'Driven to demonstrate competence and meet internal standards of excellence.' if primary[0] == 'achievement' else 'Driven to build meaningful connection and belonging.' if primary[0] == 'affiliation' else 'Driven to shape environment and exercise influence.'}",
        achievement=round(a, 2), affiliation=round(af, 2), power=round(p, 2), primary_motive=primary[0])


def _map_procrastination(results, semantic):
    """Steel (2007) temporal motivation theory: low expectancy × low value × high impulsivity × high delay."""
    signals = []  # higher = MORE procrastination-prone
    fired = _extract_fired_ids(semantic)
    if "split_crown" in fired: signals.append(0.70)  # unclear goals from identity tension
    if "bifurcated_roots" in fired: signals.append(0.65)  # structural ambivalence
    vm = _find_result(results, "void_matrix")
    if vm and vm.get("void_center"): signals.append(0.60)  # center-absence = difficulty initiating
    if "triple_gate" in fired: signals.append(0.25)  # coherence REDUCES procrastination
    if "dominant_current" in fired: signals.append(0.30)  # clear direction REDUCES it
    barz = _find_result(results, "barzakh_coefficient")
    if barz and barz.get("coefficient", 0) > 0.80: signals.append(0.30)  # structure-dominant = less procrastination
    return _make_construct(_mean(signals),
        "Procrastination Tendency",
        "Steel, P. (2007). The nature of procrastination: A meta-analytic and theoretical review. Psychological Bulletin, 133(1), 65-94.",
        "split_crown→goal ambiguity, void_center→initiation difficulty, triple_gate/dominant_current→reduce.",
        f"{'Low procrastination tendency: structural coherence provides clear initiation points.' if _mean(signals) < 0.40 else 'Moderate: clear architecture exists but center-voids or identity tension can delay engagement.' if _mean(signals) < 0.60 else 'Elevated: structural ambivalence and void-center create difficulty translating intention to action.'}",
        )


def _map_conflict_style(results, semantic):
    """Thomas & Kilmann (1974) TKI: competing/collaborating/compromising/avoiding/accommodating."""
    styles = {"competing": 0.0, "collaborating": 0.0, "compromising": 0.0,
              "avoiding": 0.0, "accommodating": 0.0}
    fired = _extract_fired_ids(semantic)
    dom_root = _extract_dominant_root(semantic)
    if dom_root == 1: styles["competing"] += 0.7
    if "triple_gate" in fired: styles["collaborating"] += 0.7
    if "outlier_witness" in fired: styles["avoiding"] += 0.5; styles["compromising"] += 0.4
    elem = _find_result(results, "element_consensus")
    if elem:
        ce = elem.get("consensus_element", "")
        if ce == "Fire": styles["competing"] += 0.5
        elif ce == "Water": styles["accommodating"] += 0.6
        elif ce == "Air": styles["compromising"] += 0.6
        elif ce == "Earth": styles["collaborating"] += 0.5
    enn = _find_result(results, "enneagram_dob")
    if enn:
        t = enn.get("enneagram_type", 0)
        if t == 8: styles["competing"] += 0.6
        elif t == 9: styles["avoiding"] += 0.7
        elif t == 2: styles["accommodating"] += 0.6
        elif t == 3: styles["competing"] += 0.4; styles["collaborating"] += 0.4
    primary = max(styles, key=styles.get)
    total = sum(styles.values()) or 1.0
    norm = {k: round(v / total, 2) for k, v in styles.items()}
    return _make_construct(max(styles.values()) / 2.0,
        "Conflict Style",
        "Thomas, K.W. & Kilmann, R.H. (1974). Thomas-Kilmann Conflict Mode Instrument. Xicom.",
        "Root 1→competing, triple_gate→collaborating, enneagram→style weighting, element→approach.",
        f"Primary conflict mode: {primary}. {'Approaches disagreement through direct assertion — wins the point but may lose the relationship.' if primary == 'competing' else 'Seeks integrative solutions — invests time to find outcomes that serve all parties.' if primary == 'collaborating' else 'Navigates conflict through tactical concession — pragmatic over principled.' if primary == 'compromising' else 'Withdraws from friction — preserves energy but may accumulate unresolved tension.' if primary == 'avoiding' else 'Yields to maintain harmony — prioritizes relationship over position.'}",
        primary_mode=primary, distribution=norm)


def _map_learning_style(results, semantic):
    """Kolb (1984) experiential learning: diverging/assimilating/converging/accommodating."""
    # CE (concrete experience) vs AC (abstract conceptualization)
    # AE (active experimentation) vs RO (reflective observation)
    ac_ce = 0.0  # positive = abstract, negative = concrete
    ae_ro = 0.0  # positive = active, negative = reflective
    fired = _extract_fired_ids(semantic)
    if "outlier_witness" in fired: ae_ro -= 0.3  # reflective
    if "dominant_current" in fired: ac_ce += 0.3  # abstract
    planes = _find_result(results, "planes_of_expression")
    if planes:
        dp = planes.get("dominant_plane", "")
        if dp == "mental": ac_ce += 0.3
        elif dp == "physical": ac_ce -= 0.3; ae_ro += 0.3
        elif dp == "emotional": ac_ce -= 0.2
        elif dp == "intuitive": ac_ce += 0.2; ae_ro -= 0.2
    hd = _find_result(results, "human_design")
    if hd:
        t = hd.get("type", "")
        if "Generator" in t: ae_ro += 0.3
        elif "Projector" in t: ae_ro -= 0.3
    if ac_ce > 0 and ae_ro <= 0: style = "assimilating"
    elif ac_ce > 0 and ae_ro > 0: style = "converging"
    elif ac_ce <= 0 and ae_ro <= 0: style = "diverging"
    else: style = "accommodating"
    return _make_construct(0.5,  # No linear scale applies to Kolb
        "Learning Style",
        "Kolb, D.A. (1984). Experiential Learning: Experience as the Source of Learning and Development. Prentice-Hall.",
        "outlier_witness→reflective, mental plane→abstract, HD Generator→active, physical plane→concrete.",
        f"Learning mode: {style}. {'Learns best through structured analysis of abstract models — the theorist.' if style == 'assimilating' else 'Learns through practical application of ideas — the engineer.' if style == 'converging' else 'Learns through imaginative exploration of concrete experience — the artist.' if style == 'diverging' else 'Learns through hands-on experimentation — the practitioner.'}",
        style=style, abstract_concrete=round(ac_ce, 2), active_reflective=round(ae_ro, 2))


def _map_moral_identity(results, semantic):
    """Aquino & Reed (2002): internalization (self-importance) vs symbolization (public display)."""
    internalization = []
    symbolization = []
    fired = _extract_fired_ids(semantic)
    if "triple_gate" in fired: internalization.append(0.80)
    if "dominant_current" in fired: internalization.append(0.70)
    dom_root = _extract_dominant_root(semantic)
    if dom_root in (1, 7): internalization.append(0.70)
    elif dom_root in (3, 6): symbolization.append(0.65)
    enn = _find_result(results, "enneagram_dob")
    if enn:
        t = enn.get("enneagram_type", 0)
        if t == 1: internalization.append(0.85)
        elif t == 3: symbolization.append(0.75)
        elif t == 2: symbolization.append(0.70)
    barz = _find_result(results, "barzakh_coefficient")
    if barz and barz.get("coefficient", 0) > 0.75: internalization.append(0.65)
    i, s = _mean(internalization), _mean(symbolization)
    return _make_construct(_mean([i, s]),
        "Moral Identity Centrality",
        "Aquino, K. & Reed, A. (2002). The self-importance of moral identity. JPSP, 83(6), 1423-1440.",
        "triple_gate→internalization, enneagram 1→principled, enneagram 3→symbolic display, barzakh→self-consistency.",
        ("Internalization-dominant: moral values are experienced as core identity architecture — "
         "integrity violations feel structurally destabilizing.") if i > s else ("Symbolization-dominant: moral identity is expressed through visible action and social signaling — "
         "the display IS the commitment."),
        internalization=round(i, 2), symbolization=round(s, 2))


def _map_maslow_needs(results, semantic):
    """Maslow (1943) hierarchy: physiological, safety, belonging, esteem, self-actualization."""
    fired = _extract_fired_ids(semantic)
    dom_root = _extract_dominant_root(semantic)
    # Map structural signals to hierarchy levels
    esteem, actualization, belonging = 0.5, 0.5, 0.5
    if "triple_gate" in fired: actualization = max(actualization, 0.80)
    if "dominant_current" in fired: actualization = max(actualization, 0.70)
    if dom_root == 1: esteem = max(esteem, 0.75)
    enn = _find_result(results, "enneagram_dob")
    if enn:
        t = enn.get("enneagram_type", 0)
        if t == 3: esteem = max(esteem, 0.80)
        elif t in (2, 9): belonging = max(belonging, 0.75)
        elif t in (4, 5): actualization = max(actualization, 0.70)
    barz = _find_result(results, "barzakh_coefficient")
    if barz and barz.get("coefficient", 0) > 0.75:
        # High fixed structure = safety is met, operating above
        pass
    levels = {"belonging": round(belonging, 2), "esteem": round(esteem, 2),
              "self_actualization": round(actualization, 2)}
    active = max(levels, key=levels.get)
    return _make_construct(levels[active],
        "Active Maslow Need Level",
        "Maslow, A.H. (1943). A theory of human motivation. Psychological Review, 50(4), 370-396.",
        "triple_gate→self-actualization, enneagram 3→esteem, enneagram 2/9→belonging, Root 1→esteem.",
        "Active level: " + active.replace('_', ' ') + ". " + (("Structural architecture points toward self-actualization — "
         "the organizing need is growth and meaning-realization.") if active == 'self_actualization' else ("Operating at the esteem level — recognition and competence are primary drivers.") if active == 'esteem' else "Belonging is the active frontier — relational security is the organizing need."),
        levels=levels, active_level=active)


def _map_impostor_profile(results, semantic):
    """Clance & Imes (1978) impostor phenomenon: structural incongruence indicators."""
    signals = []  # higher = MORE impostor-prone
    fired = _extract_fired_ids(semantic)
    if "split_crown" in fired: signals.append(0.80)  # internal-external mismatch
    if "bifurcated_roots" in fired: signals.append(0.75)  # name says one thing, birth says another
    enn = _find_result(results, "enneagram_dob")
    if enn:
        t = enn.get("enneagram_type", 0)
        if t == 3: signals.append(0.75)  # achiever = image management
        elif t == 1: signals.append(0.60)  # perfectionist = never good enough
        elif t == 8: signals.append(0.25)  # low impostor tendency
    if "triple_gate" in fired: signals.append(0.30)  # coherence REDUCES impostor feeling
    if "dominant_current" in fired: signals.append(0.35)  # clear signal REDUCES it
    vm = _find_result(results, "void_matrix")
    if vm and vm.get("void_center"): signals.append(0.65)  # center-absence = hollow feeling
    return _make_construct(_mean(signals),
        "Impostor Phenomenon Susceptibility",
        "Clance, P.R. & Imes, S.A. (1978). The impostor phenomenon in high-achieving women. Psychotherapy: Theory, Research and Practice, 15(3), 241-247.",
        "split_crown→internal/external mismatch, enneagram 3→image management, void_center→hollow core feeling, triple_gate→reduces.",
        ("Low impostor susceptibility: internal architecture matches external presentation — "
         "competence feels owned, not performed.") if _mean(signals) < 0.40 else (("Moderate impostor susceptibility: structural coherence exists but center-voids or "
         "identity tension create periodic doubt about whether competence is real or constructed.") if _mean(signals) < 0.60 else ("Elevated impostor susceptibility: structural mismatch between internal experience and external "
         "presentation — success may feel borrowed rather than earned.")),
        )


# ── Main Entry Point ───────────────────────────────────────────────────

def build_psychological_profile(output: dict) -> dict:
    """Build the full psychological_profile dict from engine output.

    Reads output["results"], output["semantic_reading"], output["synthesis"].
    Returns a dict to inject as output["psychological_profile"].
    """
    results = output.get("results", [])
    semantic = output.get("semantic_reading", {})
    synthesis = output.get("synthesis", {})

    if not semantic or "error" in semantic:
        return {"error": "semantic_reading unavailable — skipping psychological profile"}

    big_five = _map_big_five(results, semantic, synthesis)
    sps = _map_sensory_processing_sensitivity(results, semantic)
    ss = _map_sensation_seeking(results, semantic)
    pf = _map_psychological_flexibility(results, semantic)
    rum = _map_rumination_index(results, semantic)
    cog = _map_cognitive_style(results, semantic)
    stress = _map_stress_response(results, semantic)
    attach = _map_attachment_tendency(results, semantic)

    # v2 constructs (9–28)
    defense = _map_defense_mechanisms(results, semantic)
    regulation = _map_emotional_regulation(results, semantic)
    sdt = _map_self_determination(results, semantic)
    shadow = _map_shadow_profile(results, semantic)
    ipc = _map_interpersonal_circumplex(results, semantic)
    perf = _map_perfectionism(results, semantic)
    loc = _map_locus_of_control(results, semantic)
    time_p = _map_time_perspective(results, semantic)
    moral_f = _map_moral_foundations(results, semantic)
    flow = _map_flow_state(results, semantic)
    comm = _map_communication_style(results, semantic)
    resil = _map_resilience(results, semantic)
    creat = _map_creativity(results, semantic)
    motiv = _map_motivation(results, semantic)
    procrast = _map_procrastination(results, semantic)
    conflict = _map_conflict_style(results, semantic)
    learning = _map_learning_style(results, semantic)
    moral_id = _map_moral_identity(results, semantic)
    maslow = _map_maslow_needs(results, semantic)
    impostor = _map_impostor_profile(results, semantic)

    return _normalize_psych_meta({
        # v1 (1–8)
        "big_five": big_five,
        "sensory_processing_sensitivity": sps,
        "sensation_seeking": ss,
        "psychological_flexibility": pf,
        "rumination_index": rum,
        "cognitive_style": cog,
        "stress_response": stress,
        "attachment_tendency": attach,
        # v2 (9–28)
        "defense_mechanisms": defense,
        "emotional_regulation": regulation,
        "self_determination": sdt,
        "shadow_profile": shadow,
        "interpersonal_circumplex": ipc,
        "perfectionism": perf,
        "locus_of_control": loc,
        "time_perspective": time_p,
        "moral_foundations": moral_f,
        "flow_state": flow,
        "communication_style": comm,
        "resilience": resil,
        "creativity": creat,
        "motivation": motiv,
        "procrastination": procrast,
        "conflict_style": conflict,
        "learning_style": learning,
        "moral_identity": moral_id,
        "maslow_needs": maslow,
        "impostor_profile": impostor,
        "disclaimer": DISCLAIMER,
        "disclaimer_ar": DISCLAIMER_AR,
    })


# ── CLI test mode ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "output.json"
    if not path.exists():
        print(f"Error: {path} not found")
        sys.exit(1)

    output = json.loads(path.read_text(encoding="utf-8"))
    profile = build_psychological_profile(output)

    W = 72
    print("=" * W)
    print("SIRR PSYCHOLOGICAL CONSTRUCT PROFILE (28 constructs)")
    print("=" * W)

    def _bar(score):
        n = int(score * 20)
        return "█" * n + "░" * (20 - n)

    # ─── V1: Big Five ───
    print("\n── 1. BIG FIVE PERSONALITY TENDENCIES ──")
    for tk in ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"):
        t = profile["big_five"][tk]
        print(f"  {t['label']:<35} {_bar(t['score'])} {t['score']:.2f}")

    # ─── V1: Scalar constructs 2–5 ───
    print("\n── 2-5. SCALAR CONSTRUCTS ──")
    for key in ("sensory_processing_sensitivity", "sensation_seeking",
                "psychological_flexibility", "rumination_index"):
        c = profile[key]
        print(f"  {c['label']:<35} {_bar(c['score'])} {c['score']:.2f}")

    # ─── V1: Cognitive Style ───
    cog = profile["cognitive_style"]
    print(f"\n── 6. COGNITIVE STYLE ──")
    print(f"  {cog['style'].upper()} ({cog['score']:.2f})")
    print(f"  {cog['lived_description']}" if "lived_description" in cog else f"  {cog['mapping_rationale']}")

    # ─── V1: Stress Response ───
    stress = profile["stress_response"]
    print(f"\n── 7. STRESS RESPONSE ──")
    print(f"  Primary: {stress['primary_response'].upper()}")
    for mode, pct in sorted(stress["distribution"].items(), key=lambda x: -x[1]):
        if pct > 0:
            print(f"    {mode:<15} {_bar(pct)} {pct:.0%}")

    # ─── V1: Attachment ───
    a = profile["attachment_tendency"]
    print(f"\n── 8. ATTACHMENT TENDENCY ──")
    print(f"  {a['style'].upper()}  (self={a['self_model']:.2f}, other={a['other_model']:.2f})")

    # ─── V2: All 20 new constructs ───
    v2_keys = [
        ("defense_mechanisms", 9), ("emotional_regulation", 10),
        ("self_determination", 11), ("shadow_profile", 12),
        ("interpersonal_circumplex", 13), ("perfectionism", 14),
        ("locus_of_control", 15), ("time_perspective", 16),
        ("moral_foundations", 17), ("flow_state", 18),
        ("communication_style", 19), ("resilience", 20),
        ("creativity", 21), ("motivation", 22),
        ("procrastination", 23), ("conflict_style", 24),
        ("learning_style", 25), ("moral_identity", 26),
        ("maslow_needs", 27), ("impostor_profile", 28),
    ]

    for key, num in v2_keys:
        c = profile[key]
        print(f"\n── {num}. {c['label'].upper()} ──")
        # Score bar
        print(f"  Score: {_bar(c['score'])} {c['score']:.2f}")
        # Category/style if present
        for cat_key in ("level", "style", "primary_need", "octant", "orientation",
                        "primary_orientation", "primary_foundation", "primary_style",
                        "primary_domain", "primary_motive", "primary_mode",
                        "active_level", "subtype"):
            if cat_key in c:
                print(f"  {cat_key.replace('_', ' ').title()}: {c[cat_key]}")
        # Sub-scores if present
        for sub_key in ("autonomy", "competence", "relatedness",
                        "agency", "communion",
                        "past", "present", "future",
                        "achievement", "affiliation", "power",
                        "internalization", "symbolization",
                        "abstract_concrete", "active_reflective"):
            if sub_key in c:
                print(f"    {sub_key:<20} {c[sub_key]:.2f}")
        # Foundations/distributions
        if "foundations" in c:
            for fk, fv in c["foundations"].items():
                print(f"    {fk:<15} {_bar(fv)} {fv:.2f}")
        if "distribution" in c:
            for dk, dv in sorted(c["distribution"].items(), key=lambda x: -x[1]):
                if dv > 0:
                    print(f"    {dk:<15} {_bar(dv)} {dv:.2f}")
        if "shadow_elements" in c:
            for se in c["shadow_elements"][:4]:
                print(f"    - {se}")
        if "levels" in c:
            for lk, lv in c["levels"].items():
                print(f"    {lk:<20} {_bar(lv)} {lv:.2f}")
        # Lived description
        print(f"  {c['lived_description']}")

    # Disclaimer
    print(f"\n{'─' * W}")
    print(f"  {profile['disclaimer']}")
    print(f"\n  {profile['disclaimer_ar']}")
