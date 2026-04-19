"""
SIRR Unified Synthesis
======================
Derived outputs computed on top of the existing synthesis layer:
- coherence_score: 0-100 alignment metric (name × birth × traditions)
- tension_mapping: multi-dimensional cross-tradition dialogue
- signal_summary: quick structural read of what's computationally significant

All read from existing engine output (profile.core_numbers + synthesis.* + results[]).
No new computation primitives — this layer interprets what the engine found.

Upgraded 2026-04-17 (sacred/personal mode):
- Coherence score now weighs TIER_1_SIGNIFICANT > TIER_1_RESONANCE > TIER_2
- Uses baseline_percentile directly when available (truer than raw counts)
- Uses independence-group diversity (not just group_count)
- signal_summary surfaces the top significant convergences for display
- tension_mapping expanded with 5 structural dialogue dimensions:
    birth_vs_name, inner_vs_outer, script (Arabic vs Latin gematria),
    element_plurality (traditions' elemental answers), trajectory
    (Life Path vs Maturity — innate vs eventual self)
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List
from collections import Counter


# ── Meaning tags for core numbers (used in tension_mapping templates) ──
NUMBER_THEMES = {
    1: "independence",
    2: "partnership",
    3: "expression",
    4: "structure",
    5: "change",
    6: "responsibility",
    7: "analysis",
    8: "authority",
    9: "completion",
    11: "vision",
    22: "building",
    33: "teaching",
}


# ── Groups that are genuinely independent input modalities. ──
# Used to compute group_diversity: how many fundamentally different kinds
# of input (not just count of groups) does a convergence span.
INDEPENDENT_MODALITIES = {
    # Name/letter groups — letter_script modality
    "arabic_name":              "letter_script",
    "mandaean_name":            "letter_script",   # cognate-mapped from Arabic
    "latin_name":               "letter_script",
    "chaldean_name":            "letter_script",

    # Birth-digit arithmetic
    "birth_digits":             "date_digits",

    # Civilizational calendar lineages (split 2026-04-17 from unified birth_calendar).
    # All share date_calendar modality — different traditions, same raw input kind.
    "chinese_calendar":         "date_calendar",
    "hijri_calendar":           "date_calendar",
    "hebrew_calendar_family":   "date_calendar",
    "tibetan_calendar":         "date_calendar",
    "mayan_calendar":           "date_calendar",
    "indo_javanese_calendar":   "date_calendar",
    "oceanic_lunar_calendar":   "date_calendar",
    "germanic_celtic_calendar": "date_calendar",
    "zoroastrian_calendar":     "date_calendar",
    "african_calendar":         "date_calendar",
    "hellenistic_day":          "date_calendar",
    "solar_cycle":              "date_calendar",
    "jdn_infrastructure":       "date_calendar",   # infrastructure tier, kept for backward compat
    "birth_calendar":           "date_calendar",   # legacy fallback (any leftover)

    # Ephemeris/astronomical groups
    "astronomical":    "sky",
    "birth_time":      "sky",                      # birth-time data is ephemeris-adjacent
    "approx":          "sky",                      # approximate astronomy

    # Non-Western oracle
    "african_binary":  "oracle",

    # Catch-all
    "derived":         "derived",
    "unknown":         "unknown",
}


# ── Tradition → element-source module mapping (upgrade #6, 2026-04-17) ──
# For element_plurality, we ask four independent civilizational traditions
# "what element is this person?" and see if they agree.
# Each entry: tradition_label → (module_id, data_field, explanation_suffix)
ELEMENT_ORACLES = [
    ("Chinese",  "bazi_daymaster",   "day_master_element",   "BaZi Day Master"),
    ("Western",  "temperament",      "primary_element",      "Sun-sign temperament"),
    ("Vedic",    "nakshatra",        "element",              "birth-nakshatra element"),
    ("Arabic",   "elemental_letters","dominant_element",     "letter composition"),
]


def _theme(n: int) -> str:
    """Return theme word for a number, with graceful fallback."""
    if n in NUMBER_THEMES:
        return NUMBER_THEMES[n]
    # Reduce compound numbers to single digit (preserving masters)
    if n > 9 and n not in (11, 22, 33):
        r = sum(int(d) for d in str(n))
        while r > 9:
            r = sum(int(d) for d in str(r))
        return NUMBER_THEMES.get(r, "self")
    return "self"


def _reduce_single(n: int) -> int:
    """Reduce an int to single digit, preserving master numbers 11/22/33."""
    if not isinstance(n, int):
        return 0
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n


def _modality_diversity(groups: List[str]) -> int:
    """Count distinct independent modalities across a convergence's groups.

    A convergence spanning 5 letter-script groups is LESS diverse than one
    spanning letter_script + sky + oracle + date_calendar, even if group_count
    is the same. This function returns modality count (true independence).
    """
    modalities = set()
    for g in groups or []:
        modalities.add(INDEPENDENT_MODALITIES.get(g, g))
    return len(modalities)


def _get_result(output: Dict[str, Any], module_id: str) -> Dict[str, Any]:
    """Find a module's result dict in output.results by id. Returns {} if absent."""
    for r in output.get("results", []) or []:
        if r.get("id") == module_id:
            return r
    return {}


def compute_coherence_score(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute a 0-100 coherence score for this profile.

    Higher = name, birth, and traditions converge on consistent signals.
    Lower  = inputs pull in different directions.

    Algorithm (post-2026-04-17 upgrade):
    1. Tier-weighted significance: TIER_1_SIGNIFICANT counts most,
       TIER_1_RESONANCE counts, TIER_2_CONVERGENCE counts least.
    2. Modality diversity: convergences spanning truly independent input
       modalities (name + date + sky + oracle) weigh more than same-modality
       convergences.
    3. Core-number alignment: does the user's Life Path / Expression land
       in a significant convergence?
    4. Global resonance density: how many of the engine's modules hit.
    """
    profile = output.get("profile", {})
    synth = output.get("synthesis", {})
    core = profile.get("core_numbers", {})

    num_conv = {c["number"]: c for c in synth.get("number_convergences", [])}
    all_conv = synth.get("number_convergences", [])

    # ── (1) Tier-weighted significance ──
    # Each convergence contributes points proportional to tier and modality diversity.
    # Max possible per convergence ≈ 100 when it hits top 10% and 5+ modalities.
    tier_weights = {
        "TIER_1_SIGNIFICANT": 1.0,
        "TIER_1_RESONANCE":   0.5,
        "TIER_2_CONVERGENCE": 0.2,
    }
    sig_points = 0.0
    sig_possible = 0.0
    for c in all_conv:
        w = tier_weights.get(c.get("tier", ""), 0.2)
        # Prefer percentile when available; fall back to group_count proxy
        pct = c.get("baseline_percentile")
        if pct is not None:
            pct_norm = max(0.0, min(pct / 100.0, 1.0))
        else:
            pct_norm = min(c.get("group_count", 0) / 8.0, 1.0)
        # Modality diversity (0-5+ → 0-1)
        modalities = _modality_diversity(c.get("groups", []))
        mod_norm = min(modalities / 5.0, 1.0)
        # Combined contribution: tier × (0.6 percentile + 0.4 modality diversity)
        contribution = w * (0.6 * pct_norm + 0.4 * mod_norm)
        sig_points += contribution
        sig_possible += 1.0  # cap per convergence at full contribution

    # Normalize: aggregate tier-weighted signal vs theoretical max
    # (practical max ≈ 4-6 for strong profiles — don't require all 14 convergences to be significant)
    practical_max = min(sig_possible, 6.0)
    sig_pct = min(sig_points / max(practical_max, 1.0) * 100.0, 100.0) if practical_max > 0 else 0.0

    # ── (2) Core-number alignment ──
    # Do LP, Expression, Soul Urge, Personality sit in strong convergences?
    targets = ["life_path", "expression", "soul_urge", "personality"]
    core_scores = []
    for key in targets:
        n = core.get(key)
        if n is None:
            continue
        conv = num_conv.get(n)
        if conv:
            w = tier_weights.get(conv.get("tier", ""), 0.2)
            groups_n = conv.get("group_count", 0)
            core_scores.append(100 * w * min(groups_n / 8.0, 1.0))
        else:
            core_scores.append(15.0)  # weak signal fallback
    core_avg = sum(core_scores) / len(core_scores) if core_scores else 40.0

    # ── (3) Global resonance density ──
    total = synth.get("confidence_summary", {}).get("total_systems", 238) or 238
    resonance = synth.get("resonance_count", 0) or 0
    density_pct = min((resonance / max(total, 1)) * 1000.0, 100.0)  # 5% resonance → 50 score

    # ── Blend ──
    # 50% tier-weighted significance, 35% core-number alignment, 15% density
    score = round(0.50 * sig_pct + 0.35 * core_avg + 0.15 * density_pct)

    # Tier label
    if score >= 75:
        tier = "high"
        label = "Strongly aligned"
    elif score >= 55:
        tier = "moderate"
        label = "Partial alignment"
    elif score >= 30:
        tier = "low"
        label = "Divergent"
    else:
        tier = "minimal"
        label = "Weak signal"

    # Baseline provenance for transparency
    baseline_meta = synth.get("baseline") or {}

    # ── Name architecture context (research finding 2026-04-17) ──
    # Per-word convergence density inversely tracks name length (universally,
    # mechanically per the name-variant study). Exposing word count + category
    # lets downstream consumers contextualize the coherence score without
    # pretending a normalization we haven't calibrated.
    # Ref: Docs/research/name_variant_COMPARATIVE_SYNTHESIS.md
    subject = profile.get("subject", "") or ""
    word_count = len(subject.split()) if subject else 0
    if word_count == 0:
        name_category = "unknown"
        name_note = "No subject name provided — coherence interpretation limited."
    elif word_count == 1:
        name_category = "concentrated"
        name_note = ("Single-component name. Convergence signal concentrates into one name "
                     "component; per-word density is maximum. Coherence scores tend higher "
                     "by construction.")
    elif word_count <= 3:
        name_category = "standard"
        name_note = ("Short multi-component name (typical Western given+family). Convergence "
                     "signal spreads across 2-3 name components; per-word density moderate.")
    else:
        name_category = "distributed"
        name_note = ("Long multi-component name (Arabic nasab / extended patronymic lineage). "
                     "Convergence signal distributes across many name components; per-word "
                     "density low even when total convergence count is high. Coherence scores "
                     "should be read against this architecture — not compared directly with "
                     "single-component or short-name profiles.")

    return {
        "score": int(score),
        "tier": tier,
        "label": label,
        "components": {
            "tier_weighted_significance": round(sig_pct, 1),
            "core_number_alignment": round(core_avg, 1),
            "resonance_density": round(density_pct, 1),
            "significant_count": synth.get("significant_count", 0),
            "resonance_count": synth.get("resonance_count", 0),
        },
        "baseline_stratum": baseline_meta.get("stratum", "default"),
        "name_architecture": {
            "word_count": word_count,
            "category": name_category,
            "note": name_note,
        },
    }


# ──────────────────────────────────────────────────────────────────────────
# TENSION MAPPING (upgrade #6, 2026-04-17)
# ──────────────────────────────────────────────────────────────────────────
# Each _detect_* function returns a tension dict or None. The main function
# compose_tension_mapping aggregates them and picks a headline.
#
# Tension dict shape:
#   {
#     "type": str,               # stable machine ID
#     "dimension": str,          # human label for UI grouping
#     "values": [a, b, ...],     # the values in tension
#     "gap": float,              # magnitude of divergence (for ranking headline)
#     "agreement": bool,         # True if values agree (not really a tension)
#     "sentence": str,           # rendered one-liner
#   }


def _detect_birth_vs_name(core: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Life Path (birth digits) vs Expression (Latin name).
    Innate blueprint vs name-expressed direction."""
    lp = core.get("life_path")
    exp = core.get("expression")
    if lp is None or exp is None:
        return None
    exp_red = _reduce_single(exp)
    agreement = (lp == exp_red or lp == exp)
    if agreement:
        return {
            "type": "birth_vs_name",
            "dimension": "birth blueprint ↔ name expression",
            "values": [lp, exp],
            "gap": 0,
            "agreement": True,
            "sentence": (
                f"Your Life Path ({lp}) and Expression ({exp}) agree — "
                f"{_theme(lp)} as both innate and expressed."
            ),
        }
    return {
        "type": "birth_vs_name",
        "dimension": "birth blueprint ↔ name expression",
        "values": [lp, exp],
        "gap": abs(lp - exp_red),
        "agreement": False,
        "sentence": (
            f"Your birth pulls toward {_theme(lp)} (Life Path {lp}), "
            f"your name pushes toward {_theme(exp)} (Expression {exp})."
        ),
    }


def _detect_inner_vs_outer(core: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Soul Urge (vowels, inner drive) vs Personality (consonants, outer projection)."""
    su = core.get("soul_urge")
    per = core.get("personality")
    if su is None or per is None:
        return None
    agreement = (_reduce_single(su) == _reduce_single(per))
    if agreement:
        return {
            "type": "inner_vs_outer",
            "dimension": "inner drive ↔ outer projection",
            "values": [su, per],
            "gap": 0,
            "agreement": True,
            "sentence": (
                f"What you want matches what you show — "
                f"{_theme(su)} is both your drive and your impression."
            ),
        }
    return {
        "type": "inner_vs_outer",
        "dimension": "inner drive ↔ outer projection",
        "values": [su, per],
        "gap": abs(su - per),
        "agreement": False,
        "sentence": (
            f"You want {_theme(su)} (Soul Urge {su}) "
            f"but present as {_theme(per)} (Personality {per})."
        ),
    }


def _detect_script_tension(core: Dict[str, Any],
                           output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Arabic full-nasab abjad root vs Latin Expression root.

    The same person, computed by Arabic letter values vs Latin Pythagorean.
    When they agree → dual-script identity. When they diverge → two
    identities wearing the same body.
    """
    # Arabic: abjad_kabir.root (full nasab digital root)
    abjad_result = _get_result(output, "abjad_kabir")
    arabic_root = abjad_result.get("data", {}).get("root")
    if not isinstance(arabic_root, int):
        return None

    # Latin: Expression (full Pythagorean of Latin subject)
    latin_root_raw = core.get("expression")
    if not isinstance(latin_root_raw, int):
        return None
    latin_root = _reduce_single(latin_root_raw)

    agreement = (arabic_root == latin_root)
    if agreement:
        return {
            "type": "script",
            "dimension": "Arabic script ↔ Latin script",
            "values": [arabic_root, latin_root_raw],
            "gap": 0,
            "agreement": True,
            "sentence": (
                f"Arabic and Latin both reduce to {arabic_root} — "
                f"{_theme(arabic_root)} across script traditions."
            ),
        }
    return {
        "type": "script",
        "dimension": "Arabic script ↔ Latin script",
        "values": [arabic_root, latin_root_raw],
        "gap": abs(arabic_root - latin_root),
        "agreement": False,
        "sentence": (
            f"Arabic letters call you toward {_theme(arabic_root)} "
            f"(abjad root {arabic_root}); Latin letters call you toward "
            f"{_theme(latin_root_raw)} (Expression {latin_root_raw})."
        ),
    }


def _detect_trajectory(core: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Life Path (who you come in as) vs Maturity (who emerges after ~35-40).

    Maturity = reduced(Life Path + Expression). When it differs from Life Path,
    it signals a trajectory shift at midlife — what the name expresses fuses
    with birth identity into a new center.
    """
    lp = core.get("life_path")
    exp = core.get("expression")
    if not isinstance(lp, int) or not isinstance(exp, int):
        return None
    maturity_raw = lp + exp
    maturity = _reduce_single(maturity_raw)
    if lp == maturity:
        return None  # no trajectory shift — stable identity
    return {
        "type": "trajectory",
        "dimension": "innate self ↔ mature self",
        "values": [lp, maturity],
        "gap": abs(lp - maturity),
        "agreement": False,
        "sentence": (
            f"Your early-life center is {_theme(lp)} (Life Path {lp}); "
            f"after midlife (≈35-40), {_theme(maturity)} emerges as the "
            f"mature signature (Maturity {maturity})."
        ),
    }


def _detect_element_plurality(output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """How many distinct elements do independent traditions assign this person?

    Queries four oracles:
      Chinese (BaZi Day Master), Western (Sun-sign temperament),
      Vedic (nakshatra), Arabic (elemental letters).

    Returns:
      - If 1 element: strong convergence (rare, meaningful alignment).
      - If 2-3: partial convergence with named tension.
      - If 4: elemental plurality (every tradition sees a different element).
    """
    readings: List[Dict[str, str]] = []
    for tradition, mod_id, field, label in ELEMENT_ORACLES:
        r = _get_result(output, mod_id)
        val = r.get("data", {}).get(field)
        if isinstance(val, str) and val:
            elem_norm = val.strip().capitalize()
            readings.append({
                "tradition": tradition,
                "element": elem_norm,
                "source": label,
            })
    if len(readings) < 2:
        return None  # not enough oracles ran

    counter = Counter(r["element"] for r in readings)
    distinct = len(counter)
    total = len(readings)

    # Describe distribution
    tradition_strs = [f"{r['tradition']} = {r['element']}" for r in readings]
    sig_line = "; ".join(tradition_strs)

    if distinct == 1:
        only_elem = next(iter(counter))
        return {
            "type": "element_plurality",
            "dimension": f"{total} traditions ↔ single element",
            "values": [r["element"] for r in readings],
            "readings": readings,
            "distinct_elements": distinct,
            "gap": 0,
            "agreement": True,
            "sentence": (
                f"All {total} traditions agree: you are {only_elem} "
                f"({sig_line}). Rare single-element convergence."
            ),
        }

    if distinct == total:
        return {
            "type": "element_plurality",
            "dimension": f"{total} traditions ↔ {distinct} distinct elements",
            "values": [r["element"] for r in readings],
            "readings": readings,
            "distinct_elements": distinct,
            "gap": distinct,  # use distinct count as the gap for ranking
            "agreement": False,
            "sentence": (
                f"Every tradition gives a different element — "
                f"{sig_line}. Elemental plurality: you shape-shift across systems."
            ),
        }

    # 2 or 3 distinct among N (mixed)
    dominant_elem, dominant_count = counter.most_common(1)[0]
    minority = [r for r in readings if r["element"] != dominant_elem]
    minority_str = ", ".join(f"{r['tradition']} ({r['element']})" for r in minority)
    return {
        "type": "element_plurality",
        "dimension": f"{total} traditions ↔ {distinct} elements",
        "values": [r["element"] for r in readings],
        "readings": readings,
        "distinct_elements": distinct,
        "gap": distinct - 1,  # 1 for partial, 2 for more spread
        "agreement": False,
        "sentence": (
            f"{dominant_count} of {total} traditions center on {dominant_elem} "
            f"({sig_line}); {minority_str} diverge."
        ),
    }


def compute_tension_mapping(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce a multi-dimensional tension narrative.

    Runs five detectors across cross-tradition dialogue dimensions:
      - birth_vs_name          (Life Path vs Expression)
      - inner_vs_outer         (Soul Urge vs Personality)
      - script                 (Arabic abjad vs Latin Pythagorean root)
      - trajectory             (Life Path vs Maturity — midlife shift)
      - element_plurality      (Chinese + Western + Vedic + Arabic element oracles)

    Returns the full list plus a headline "primary" (biggest gap) plus a
    rendered sentence. When no tension exists anywhere, returns an alignment
    message.
    """
    core = output.get("profile", {}).get("core_numbers", {})

    detectors = [
        _detect_birth_vs_name(core),
        _detect_inner_vs_outer(core),
        _detect_script_tension(core, output),
        _detect_trajectory(core),
        _detect_element_plurality(output),
    ]
    tensions = [t for t in detectors if t is not None]

    # Divergences only, for ranking "primary"
    divergences = [t for t in tensions if not t.get("agreement", False)]

    if not tensions:
        return {
            "primary": None,
            "all": [],
            "divergence_count": 0,
            "sentence": (
                "No cross-tradition tensions surfaced — structural alignment is "
                "strong across name, birth, and elemental traditions."
            ),
        }

    if not divergences:
        # All detectors fired but all agreed
        first = tensions[0]
        return {
            "primary": first,
            "all": tensions,
            "divergence_count": 0,
            "sentence": first["sentence"],
        }

    primary = max(divergences, key=lambda t: t.get("gap", 0))
    return {
        "primary": primary,
        "all": tensions,
        "divergence_count": len(divergences),
        "sentence": primary["sentence"],
    }


def compute_signal_summary(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Surface the top statistically-significant convergences for display.

    Returns the convergences flagged TIER_1_SIGNIFICANT by the synthesis layer,
    annotated with modality diversity and a one-line human-readable summary.
    This is the sacred-mode "what is the engine saying about you" quick read.
    """
    synth = output.get("synthesis", {})
    all_conv = synth.get("number_convergences", [])

    significant = [c for c in all_conv if c.get("tier") == "TIER_1_SIGNIFICANT"]
    resonance   = [c for c in all_conv if c.get("tier") == "TIER_1_RESONANCE"]

    def summarize(c: Dict[str, Any]) -> Dict[str, Any]:
        groups = c.get("groups", [])
        modalities = _modality_diversity(groups)
        n = c["number"]
        return {
            "number": n,
            "theme": _theme(n),
            "system_count": c["system_count"],
            "group_count": c["group_count"],
            "modality_diversity": modalities,
            "baseline_percentile": c.get("baseline_percentile"),
            "groups": sorted(groups),
            "sentence": (
                f"{c['system_count']} systems across {c['group_count']} independence "
                f"groups ({modalities} distinct input modalities) converge on "
                f"Root {n} — {_theme(n)}."
            ),
        }

    return {
        "significant": [summarize(c) for c in sorted(significant, key=lambda x: -x.get("baseline_percentile", 0))],
        "resonance":   [summarize(c) for c in sorted(resonance, key=lambda x: -x["system_count"])[:5]],
        "total_significant": len(significant),
        "total_resonance": len(resonance),
        "baseline_stratum": (synth.get("baseline") or {}).get("stratum", "default"),
    }


# ──────────────────────────────────────────────────────────────────────────
# PSYCH SIGNALS (upgrade #7, 2026-04-17)
# ──────────────────────────────────────────────────────────────────────────
# The engine already computes psychological_profile with 28+ dimensions.
# This surface compacts them into reading-friendly signals:
#   - big_five (bucketed labels + outliers)
#   - dominant_tendencies (top-N high-score dimensions)
#   - compensating_tendencies (bottom-N low-score dimensions)
#   - structural_signature (one-line synthesis)
# Full psychological_profile is preserved in output.psychological_profile —
# this is the "at a glance" surface, not a replacement.

# Thresholds for bucketing 0-1 scores
_PSYCH_HIGH  = 0.70
_PSYCH_LOW   = 0.40

# Big Five traits whose HIGH end is the interesting direction
# (For neuroticism, "low" is the notable direction, culturally; but for
# signal purposes we still report what the score is — the interpretation
# layer above can add valence.)
_BIG_FIVE_TRAITS = ("openness", "conscientiousness", "extraversion",
                    "agreeableness", "neuroticism")

# Dimensions to exclude from dominant/compensating rankings because they
# aren't ranked-interesting in isolation (they need paired interpretation)
_PSYCH_EXCLUDE_FROM_RANKING = {
    "big_five",                       # composite — we handle separately
    "disclaimer", "disclaimer_ar",
    "stress_response",                # primary_response is categorical
    "attachment_tendency",            # style is categorical
    "cognitive_style",                # style axis
    "communication_style",            # primary_style is categorical
    "conflict_style",                 # primary_mode is categorical
    "learning_style",                 # style is categorical
    "moral_foundations",              # primary_foundation is categorical
    "time_perspective",               # three-way balance
    "self_determination",             # three-component decomposition
    "motivation",                     # three-component decomposition
    "interpersonal_circumplex",       # agency/communion coordinates
    "maslow_needs",                   # active_level is categorical
}


def _psych_bucket(score: float) -> str:
    """Map 0-1 score to low / moderate / high bucket label."""
    if not isinstance(score, (int, float)):
        return "unknown"
    if score >= _PSYCH_HIGH:
        return "high"
    if score <= _PSYCH_LOW:
        return "low"
    return "moderate"


def _first_sentence(text: str, max_chars: int = 200) -> str:
    """Return the first sentence of a string, capped at max_chars."""
    if not isinstance(text, str) or not text.strip():
        return ""
    # Prefer true sentence boundary
    for sep in (". ", "؛ ", "؟ ", "! "):
        if sep in text:
            first = text.split(sep, 1)[0] + sep.strip()
            return first[:max_chars].strip()
    return text[:max_chars].strip()


def compute_psych_signals(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Surface compact psychological signals from output.psychological_profile.

    Returns:
      big_five: { trait: bucket, ... } + outliers list
      dominant_tendencies: top-3 dimensions with score >= 0.70
      compensating_tendencies: bottom-2 dimensions with score <= 0.40
      structural_signature: one-line synthesis from the top tendencies
      disclaimer: pass-through
      dimensions_count: total number of dims in the profile
    """
    pp = output.get("psychological_profile")
    if not isinstance(pp, dict) or not pp:
        return {
            "available": False,
            "big_five": None,
            "dominant_tendencies": [],
            "compensating_tendencies": [],
            "structural_signature": None,
            "dimensions_count": 0,
        }

    # ── Big Five summary ──
    bf = pp.get("big_five", {}) or {}
    big_five: Dict[str, Any] = {}
    bf_outliers: List[str] = []
    if isinstance(bf, dict):
        for trait in _BIG_FIVE_TRAITS:
            tdata = bf.get(trait, {})
            if isinstance(tdata, dict):
                s = tdata.get("score")
                bucket = _psych_bucket(s) if isinstance(s, (int, float)) else "unknown"
                big_five[trait] = {
                    "score": round(s, 2) if isinstance(s, (int, float)) else None,
                    "bucket": bucket,
                    "label": tdata.get("label", trait.title()),
                }
                if bucket in ("high", "low"):
                    bf_outliers.append(f"{trait}_{bucket}")

    # ── Ranked dimensions ──
    scored: List[Dict[str, Any]] = []
    for key, val in pp.items():
        if key in _PSYCH_EXCLUDE_FROM_RANKING:
            continue
        if not isinstance(val, dict):
            continue
        s = val.get("score")
        if not isinstance(s, (int, float)):
            continue
        scored.append({
            "dimension": key,
            "score": round(s, 2),
            "label": val.get("label", key.replace("_", " ").title()),
            "lived": _first_sentence(val.get("lived_description", "")),
        })

    dominant = sorted(
        [s for s in scored if s["score"] >= _PSYCH_HIGH],
        key=lambda x: -x["score"],
    )[:3]

    compensating = sorted(
        [s for s in scored if s["score"] <= _PSYCH_LOW],
        key=lambda x: x["score"],
    )[:2]

    # ── Structural signature (one-line synthesis) ──
    # Compact form: the top-3 dominant dimension labels. The reading layer
    # (or ChatGPT/Grok downstream) can expand this into narrative prose;
    # here we surface the raw fingerprint.
    structural_signature = None
    if dominant:
        labels = [d["label"] for d in dominant[:3]]
        if len(labels) == 1:
            structural_signature = f"Dominant structural tendency: {labels[0]}."
        else:
            joined = ", ".join(labels[:-1]) + f", and {labels[-1]}"
            structural_signature = f"Dominant structural tendencies: {joined}."
    elif scored:
        # No strong dominants — describe the flat profile
        strongest = max(scored, key=lambda x: x["score"])
        structural_signature = (
            f"No dominant tendencies above {_PSYCH_HIGH:.2f}; strongest "
            f"signal is {strongest['label']} at {strongest['score']}."
        )

    return {
        "available": True,
        "big_five": {
            "traits": big_five,
            "outliers": bf_outliers,
        } if big_five else None,
        "dominant_tendencies": dominant,
        "compensating_tendencies": compensating,
        "structural_signature": structural_signature,
        "dimensions_count": sum(1 for k, v in pp.items()
                                if isinstance(v, dict) and k not in {"disclaimer", "disclaimer_ar"}),
        "disclaimer": pp.get("disclaimer"),
    }


def compute_unified_synthesis(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Single entry point for all derived outputs.
    Call this in the /api/analyze response path.
    """
    return {
        "coherence": compute_coherence_score(output),
        "tension":   compute_tension_mapping(output),
        "signal":    compute_signal_summary(output),
        "psych":     compute_psych_signals(output),
    }
