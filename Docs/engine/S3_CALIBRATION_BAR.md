# S3 — Convergence Convergence-Layer False-Positive Target

**Status:** LOCKED 2026-04-27 by Muhab. Tier-1 1.5%, Tier-2 5.0%. Tier source confirmed.
**Original draft:** `Tools/handoff/S3_CONVERGENCE_FP_TARGET_BRIEF.md`
**Locks:** S3 audit pass/fail bar; informs launch path.
**Revisable:** Yes, post-launch with real distribution data.

---

## What this brief decides

The maximum acceptable rate at which a randomly-generated profile triggers a Convergence event in the deterministic engine. This is the calibration target for S3.

A profile that "triggers Convergence" means: the engine output flags one or more of the ~12 Convergence modules with sufficient activation that a customer reading the output would experience it as a notable convergence event, not as ambient noise.

## Why this number is load-bearing

Convergence is the headline output of SIRR. Per the locked product doctrine: *"Convergence is never announced — the user discovers it. No interpretation layer on the visual artifact. Pattern accumulates in the user, not on the page."*

If FP rate is too high, every profile lights up, the discovery moment cheapens, and the doctrine of rare-and-significant collapses. If FP rate is too low, real convergences in real customer profiles get suppressed and the engine becomes too conservative to deliver the experience.

The audit plan's draft proposed 5%. That's wrong on the doctrine — 1 in 20 random profiles triggering Convergence is noise, not discovery. This brief revises down.

## Proposal

**Tier-1 Convergence (canonical, customer-visible): ≤ 1.5% FP rate**

Tier-1 Convergence is what surfaces on the visual artifact and in the customer-facing output. The 1.5% number means: out of 10,000 randomly-generated profiles in the Monte Carlo baseline (already in place per memory), at most 150 should trigger any Tier-1 Convergence module.

Justification:
- Below 2% threshold matches the "rare and significant" framing.
- Above 1% leaves room for genuine convergences in genuinely-aligned profiles to actually fire.
- 1.5% is the midpoint, defensible as a launch number, revisable when real customer distribution data arrives.

**Tier-2 Convergence (extended modules, internal/diagnostic): ≤ 5% FP rate**

Tier-2 covers the broader Convergence-adjacent modules that don't surface on the artifact but inform the underlying engine state. These can run looser since they don't shape the customer's discovery moment directly.

5% on Tier-2 matches the audit plan's original number, repositioned for the right tier.

## Tier definitions (locks for S3 audit)

Tier-1 modules: the ~12 canonical Convergence modules already enumerated in the unified architecture spec at `Docs/engine/UNIFIED_ARCHITECTURE.md`. S3 audit measures their joint FP rate, not per-module FP rate (a module firing in 0.5% of profiles is fine if no two of them co-fire on the same noise; what matters is the rate at which a customer sees a Convergence event of any kind).

Tier-2 modules: anything Convergence-adjacent that ships in the engine output but is suppressed from the customer-facing visual layer. Exact list to be enumerated as the first task in S3.

## What S3 must produce

1. A Monte Carlo run at n=10,000 (existing baseline) measuring Tier-1 joint FP rate against the proposed 1.5% bar.
2. Same for Tier-2 against 5%.
3. If Tier-1 measured FP exceeds 1.5%: identify which modules contribute most noise, propose threshold tightening within those modules, re-measure. Iterate until the joint rate is within target.
4. Tier-2: same protocol if rate exceeds 5%.
5. A documented "calibration commit" recording the threshold values that achieved target rates, the measured rates at those thresholds, and the date.

## What this does NOT decide

- Module-level activation thresholds (S3's job to derive these from the FP target).
- Whether tiered Convergence is the right product abstraction (assumed yes per existing architecture; out of scope for FP target).
- Convergence presentation on the visual artifact (locked by product doctrine — "user discovers it").
- Detection threshold for false negatives (asymmetric to FP — FN is what customer-facing real-world feedback measures, requires real traffic, post-launch).

## Revisability

Three triggers to revisit this number:

1. **First 100 customers' profile distribution lands.** Real distributions are not Monte Carlo distributions. If real customers' profiles cluster in regions of the input space that produce more or fewer Convergences than the Monte Carlo baseline, the calibration may need a single one-shot adjustment.
2. **Customer feedback on Convergence frequency.** If discovery moments are reported as too rare or too common, that's signal to revisit.
3. **New Convergence modules added.** Each new module shifts the joint rate; recalibration mandatory.

Outside these triggers, the number is fixed.

## Sign-off block

```
Tier-1 FP target: 1.5%  APPROVED 2026-04-27
Tier-2 FP target: 5.0%  APPROVED 2026-04-27
Tier definition source: Docs/engine/UNIFIED_ARCHITECTURE.md  CONFIRMED
Locked at: 2026-04-27
Revisability triggers: locked as above
```

S3 audit measures against this bar. Revisability triggers (first 100 customers' real distribution / customer feedback / new module additions) are the only paths to re-open.
