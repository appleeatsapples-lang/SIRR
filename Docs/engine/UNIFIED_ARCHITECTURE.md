# SIRR Unified Architecture — Convergence Layer

**Status:** Authoritative as of 2026-04-29. Updated when synthesis layer fields change.
**Purpose:** Enumerates the convergence-layer fields that surface to customers. Required reference for `S3_CALIBRATION_BAR.md` and any future convergence-layer audit.

---

## What "Convergence" means in SIRR

SIRR runs 238 deterministic modules across 16 traditions. The **synthesis layer** (`Engine/modules/synthesis.py`) reads each module's output and detects when multiple modules independently emit the same value (number, element, or timing index).

A *convergence* is not a separate module. It is an emergent property of the multi-module output: when ≥3 systems in ≥2 independence groups vote for the same value, the synthesis layer emits a `Convergence` entry with a tier classification.

**The customer-visible "Convergence" in the reading** is the peak Number Convergence — the root that most traditions agree on. This is the headline product signal.

---

## Convergence types (output fields from `synthesize()`)

The synthesis layer produces five convergence categories. All five are published in `output.json` under `synthesis.*`:

### 1. `number_convergences` (PRIMARY, customer-visible)

A list of per-root convergence entries. Each entry has:

| Field | Type | Description |
|---|---|---|
| `number` | int | The root number (1-9, 11, 22, 33) |
| `system_count` | int | How many systems voted for this root |
| `group_count` | int | How many independence groups are represented |
| `groups` | list[str] | The independence group names |
| `systems` | list[str] | The system IDs that voted |
| `tier` | str | `TIER_1_SIGNIFICANT` / `TIER_1_RESONANCE` / `TIER_2_CONVERGENCE` |
| `baseline_percentile` | float \| null | Where this `system_count` sits in the n=10,000 baseline |

**Tier rules (from `synthesis.py:1015-1023`):**
- `TIER_1_SIGNIFICANT`: ≥3 groups AND (top-10th-percentile by system_count OR (≥5 groups AND top-15th-percentile))
- `TIER_1_RESONANCE`: ≥3 groups (without percentile boost)
- `TIER_2_CONVERGENCE`: ≥2 groups (≥3 systems and ≥2 groups required to appear at all)

**Customer-visible surface:** the **peak** number_convergence (highest `system_count`) is what the reading displays as the "primary signal." The block currently reads: *"X traditions converge on your primary signal across Y tradition families."*

### 2. `element_convergences` (SECONDARY, customer-visible)

When ≥2 systems in ≥2 groups assign the same dominant element (Fire/Water/Earth/Air or East-Asian Five Elements):

| Field | Type | Description |
|---|---|---|
| `element` | str | Element name |
| `system_count` | int | Systems voting |
| `group_count` | int | Independence groups |
| `tier` | str | `TIER_1_RESONANCE` (≥3 groups) / `TIER_2_CONVERGENCE` (≥2 groups) |

**Customer-visible surface:** mentioned in the reading's "Primary Tension" block when element disagreement is the structural signal.

### 3. `timing_convergences` (SECONDARY, customer-visible)

When ≥2 systems in ≥2 groups vote for the same number on Q4 (Timing) modules:

| Field | Type | Description |
|---|---|---|
| `number` | int | 1-12 |
| `system_count` | int | Systems voting |
| `group_count` | int | Independence groups |
| `tier` | str | `TIER_1_SIGNIFICANT` (≥4 groups + ≥6 systems) / `TIER_1_RESONANCE` (≥3 groups) / `TIER_2_CONVERGENCE` |

**Customer-visible surface:** referenced in the reading's "Current Cycles" block.

### 4. `master_pair_resonances` (TERTIARY, less customer-visible)

Master-number pair detection (11/22/33). Surfaces if the customer's profile has master numbers active across multiple traditions.

### 5. `confidence_summary` (META, customer-visible)

Aggregate statistics about the run:

| Field | Type | Description |
|---|---|---|
| `total_systems` | int | Total modules run (≈238) |
| `strict_locked` | int | Count of `COMPUTED_STRICT` modules |
| `method_locked` | int | Count of `LOOKUP_FIXED` modules |
| `approximate` | int | Count of `APPROX` modules |
| `lockable_pct` | float | (strict + lookup) / total × 100 |

**Customer-visible surface:** the reading footer cites the total system count ("238 computations across …").

---

## Tier classification at the `synthesis.*` field level (S3 measurement targets)

For S3 audit purposes, the **customer-visible Convergence "events"** are:

### Tier-1 (canonical, customer-visible) — joint FP target ≤1.5%

A profile is said to "trigger Tier-1 Convergence" if **any** of the following fire:
1. `number_convergences` has at least one entry with `tier == "TIER_1_SIGNIFICANT"` OR `tier == "TIER_1_RESONANCE"`
2. `element_convergences` has at least one entry with `tier == "TIER_1_RESONANCE"`
3. `timing_convergences` has at least one entry with `tier == "TIER_1_SIGNIFICANT"` OR `tier == "TIER_1_RESONANCE"`

### Tier-2 (extended, internal/diagnostic) — joint FP target ≤5%

A profile is said to "trigger Tier-2 Convergence" if any of the above OR a `TIER_2_CONVERGENCE` entry exists in any of the three lists. Tier-2 is a superset of Tier-1.

### Master-pair resonances and confidence_summary

Not part of the FP target measurement. They are descriptive aggregates, not "events."

---

## What is NOT a Convergence module

The S3 calibration bar previously referenced "the ~12 canonical Convergence modules." This phrasing was inherited from earlier informal docs and is **misleading**. There are no dedicated "Convergence modules." Convergence is an emergent property computed by `synthesize()` from the 238 base modules' outputs.

The correct framing for S3:
- **The 238 modules** are inputs.
- **`synthesize()`** emits convergence events (Number / Element / Timing) at three tier levels.
- **The customer-visible signal** is the peak Number Convergence with its tier classification.
- **FP rate** = the fraction of random profiles that produce at least one Tier-1 event.

---

## Independence groups

`SYSTEM_TO_GROUP` mapping in `Engine/modules/synthesis.py` assigns each module to one of these independence groups:

| Group | Modules | What it represents |
|---|---|---|
| `arabic_name` | abjad_kabir, abjad_saghir, abjad_wusta, abjad_maghribi, jafr, taksir, bast_kasr, etc. | Arabic letter-numerology computation |
| `latin_name` | chaldean, pythagorean, latin_ordinal, etc. | Latin-script numerology |
| `mandaean_name` | mandaean_gematria, malwasha | **Cognate-derived from Arabic** (Apr 16 finding); contributes ≤2 votes |
| `chaldean_name` | chaldean | Distinct from latin_name historically |
| `birth_digits` | life_path, day_ruler, pinnacles, etc. | DOB digit reductions |
| `birth_calendar` | hijri, hebrew_calendar, mayan, dreamspell, tonalpohualli, etc. | Calendar-derived |
| `astronomical` | natal_chart, decan, dwad, manazil, nakshatra, etc. | Ephemeris-dependent |
| `birth_time` | birth_time-gated systems (zi_wei_dou_shu, shadbala, etc.) | Requires birth_time |
| `derived` | synthesis-internal computations | Meta-level |
| `african_binary` | ifa, akan_kra_din | Distinct binary-divination computational lineage |

**Important honesty note (per Apr 16 Grok scholarship audit):**
- `hebrew_gematria`, `mandaean_gematria`, `ethiopian_asmat` operate on **Arabic input mapped to their script's letter values**. Their convergence with Arabic abjad is **identity-by-construction**, not independent witnesses.
- The `MODERN_SYNTHESIS` source-tier label applies to all three.
- This is reflected in customer-facing copy as of PR #50 (2026-04-29).
- For S3 FP measurement, these modules still contribute votes in their assigned groups, but readers of the architecture should know the cross-tradition agreement they produce is computational, not historical.

---

## Customer-visible signal flow

```
238 modules → synthesize() → number/element/timing convergences
                                    ↓
                          peak number_convergence
                                    ↓
                        html_reading.py renders:
                        "X traditions converge on your primary signal
                         across Y tradition families"
                                    ↓
                          Customer reads
```

The customer sees ONE peak signal (the highest number convergence). They do not see a count of "events fired" or a discrete "no convergence today" empty state. The reading always shows a peak.

---

## Why this matters for S3

The S3 calibration bar (`Docs/engine/S3_CALIBRATION_BAR.md`) targets ≤1.5% Tier-1 FP rate. Per `S3_FINDINGS_2026-04-29.md`, the existing n=10,000 MC baseline shows that **100% of random profiles produce at least one Tier-1 convergence event** at current thresholds — making the bar incompatible with current architecture without threshold tightening or a reframe of what "Tier-1 firing" means.

S3_FINDINGS proposes either tightening `min_systems` / `min_groups` thresholds in `synthesize()` to compress the Tier-1 firing rate, or reframing the customer-visible signal from binary "Tier-1 fired" to a continuous percentile display ("your peak sits at the Nth percentile of n=10,000 baseline profiles").

This document is the source-of-truth for what the convergence layer produces. Changes here require a doctrine PR.

---

*Document version 1.0 — 2026-04-29 — created in response to S3 calibration audit gap.*
