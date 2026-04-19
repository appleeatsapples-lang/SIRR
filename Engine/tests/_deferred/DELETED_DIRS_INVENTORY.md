# Deleted-directory inventory

During the public-repo separation cycle (April 2026), four `Engine/`
subdirectories were removed wholesale because their contents were
either personal-data-bound (specific to one profile, family-coupled,
or referenced muhab paths) or were development tooling not load-bearing
for the public engine + web demo.

This file is the index. Phase 2a can consult the vault snapshot at
`SIRR_PRIVATE/` (or the backup tarball
`~/Desktop/SIRR_REPO_BACKUP_20260419_0216.tar.gz`) and selectively
restore individual items if needed.

The four dirs:
- `Engine/specs/`         — AI build briefs (internal architecture history)
- `Engine/monte_carlo/`   — MC baseline generation scripts + outputs
- `Engine/analysis/`      — Cross-profile + benchmark + family analysis
- `Engine/reports/`       — Generated analysis report outputs

---

## Engine/specs/ — AI build briefs

| File | Purpose |
|---|---|
| BUGFIX_RAMADAN_FIELD.md | Bugfix brief: Ramadan field handling in Hijri calendar modules |
| BUGFIX_TRANSIT_ESSENCE.md | Bugfix brief: transit essence calculation drift |
| BUILD_SPEC_ANIMAL_SYMBOLISM.md | Build spec: animal-symbolism interpretation overlay |
| BUILD_SPEC_COMPARE_ENGINE.md | Build spec: cross-profile comparison engine |
| BUILD_SPEC_DYAD_READING.md | Build spec: two-person dyad reading composer |
| BUILD_SPEC_FAMILY_MC.md | Build spec: family-level Monte Carlo validation |
| BUILD_SPEC_FAMILY_MC_MODULES.md | Build spec: per-module family MC analysis |
| BUILD_SPEC_ORCHESTRATOR_V2.md | Build spec: multi-model orchestrator v2 |
| BUILD_SPEC_PLANETARY_SYMBOLISM.md | Build spec: planetary symbolism layer |
| BUILD_SPEC_PSYCH_LAYER.md | Build spec: psychological translation layer (v1) |
| BUILD_SPEC_PSYCH_LAYER_V2.md | Build spec: psychological translation layer (v2) |
| BUILD_SPEC_ROUND5.md | Build spec: Round-5 module expansion (27 new modules) |
| BUILD_SPEC_RUN_COMPARE.md | Build spec: comparative run harness |
| BUILD_SPEC_VISUAL_READING.md | Build spec: visual rendering of reading output |
| EXPANSION_ROADMAP_v3.1.md | Roadmap: 211→300 module expansion plan |
| INTERP_ALL_BATCHES.md | Index: all interpretation batches across waves |
| INTERP_BATCH1_PROMPT.md | LLM prompt: batch 1 interpretations |
| INTERP_BATCH2_PROMPT.md | LLM prompt: batch 2 interpretations |
| INTERP_BATCH3_PROMPT.md | LLM prompt: batch 3 interpretations |
| INTERP_BATCH4_PROMPT.md | LLM prompt: batch 4 interpretations |
| PRODUCT_ARCHITECTURE.md | Architecture doc: product surface vs engine-internal split |
| PROMPT_A_CHATGPT_REVIEW.md | LLM prompt: ChatGPT review pass A |
| PROMPT_B_CHATGPT_DEEPEN.md | LLM prompt: ChatGPT deepen pass B |
| PROMPT_C_GEMINI_ARABIC.md | LLM prompt: Gemini Arabic-linguistics scholarship |
| PROMPT_D_GROK_ADVERSARIAL.md | LLM prompt: Grok adversarial audit |
| ROUND5_SCOUT_CHATGPT.md | Round-5 scout brief routed to ChatGPT |
| ROUND5_SCOUT_GEMINI.md | Round-5 scout brief routed to Gemini |
| ROUND5_SCOUT_GROK.md | Round-5 scout brief routed to Grok |

## Engine/monte_carlo/ — MC baseline scripts + outputs

| File | Purpose |
|---|---|
| mc_baseline_core25.json | MC baseline output: core 25-module subset |
| mc_baseline_core25.py | MC baseline script: core 25-module subset |
| mc_baseline_core25_3word.json | MC baseline (length-matched 3-word names): output |
| mc_baseline_core25_3word.py | MC baseline (length-matched 3-word names): script |
| mc_baseline_core25_5word.json | MC baseline (length-matched 5-word names): output |
| mc_baseline_core25_5word.py | MC baseline (length-matched 5-word names): script |
| mc_baseline_core25_long_names.json | MC baseline (length-matched 8+-word names): output |
| mc_baseline_core25_long_names.py | MC baseline (length-matched 8+-word names): script |
| monte_carlo_baseline.json | MC baseline (default): output, n=10,000 |
| monte_carlo_baseline.py | MC baseline (default): script |
| monte_carlo_long_names.json | MC baseline (long names default): output |
| monte_carlo_long_names.py | MC baseline (long names default): script |
| monte_carlo_matched.py | MC baseline: name-length-matched comparator |

## Engine/analysis/ — Cross-profile + benchmark + family

| File | Purpose |
|---|---|
| activation_detector.py | Semantic-pipeline activation detector (duplicate of Engine root copy) |
| axis_reducer.py | Semantic-pipeline axis reducer (duplicate of Engine root copy) |
| benchmark_db.json | Benchmark output for ~64 famous-figure profiles |
| benchmark_db.py | Benchmark harness running engine across famous figures |
| benchmark_results_211.json | Benchmark results snapshot at 211-module engine state |
| benchmark_results_238.json | Benchmark results snapshot at 238-module engine state |
| combination_engine.py | Semantic-pipeline combination engine (duplicate of Engine root copy) |
| compare_profiles.py | Compare two engine outputs side-by-side |
| inter_axis_synthesizer.py | Semantic-pipeline inter-axis synthesizer (duplicate of Engine root copy) |
| meta_pattern_detector.py | Semantic-pipeline meta-pattern detector (duplicate of Engine root copy) |
| output_family/famous_summary.json | Cross-family + famous-figure aggregated summary |
| run_famous.py | Runs engine across the famous-figure fixture set |
| synastry_runner.py | Pairwise synastry runner across multiple profiles |

## Engine/reports/ — Generated analysis report outputs

| File | Purpose |
|---|---|
| README.md | Report directory README |
| benchmark_rescore_167.json | Benchmark rescore at 167-module engine state |
| calibration_report.md | Calibration pass report (axis/meta-pattern thresholds) |
| convergence_pvalues.json | Convergence p-value table (per number/element) |
| convergence_pvalues.md | Convergence p-value markdown report |
| element_signature.json | Per-profile element-signature analysis |
| family_mc_modules_results.json | Family-level MC results, module-level patterns |
| family_mc_results.json | Family-level MC results, date/name patterns |
| family_mirror_147.md | Family Mirror analysis at 147-module engine state |
| mc_baseline_report.json | MC baseline report (cross-stratum comparison) |
| module_signal_analysis.json | Per-module signal-vs-baseline analysis |
| monte_carlo_results.json | MC results (referenced by synthesis baseline metadata) |
| near_misses.json | Near-miss convergence candidates (one short of threshold) |
| set_modules_audit.json | Audit of set-returning modules for convergence promotion |
| timing_consensus.json | Timing consensus across cyclic modules |
