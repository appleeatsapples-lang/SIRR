# DeepSeek Statistical Validation Framework

**Status:** SCAFFOLDED (2026-03-04) — awaiting DeepSeek Round 2 raw specifications to implement.

## Purpose

Provides rigorous statistical validation for SIRR convergence claims. Each module addresses a specific recommendation from DeepSeek Validator Round 2.

## Modules

| Module | Function | DeepSeek Recommendation |
|--------|----------|------------------------|
| `null_models.py` | Permutation & bootstrap null distributions | "Add permutation tests preserving independence group structure" |
| `dependency_audit.py` | Module dependency graph analysis | "Map every kwargs dependency and verify SYSTEM_TO_GROUP assignments" |
| `fdr_correction.py` | Benjamini-Hochberg FDR correction | "Apply BH FDR to all convergence p-values before tier assignment" |
| `effect_sizes.py` | Cohen's d, Cramér's V | "Report effect sizes alongside p-values for every claim" |
| `similarity_significance.py` | Family echo significance testing | "Build controlled null for shared-input channels" |
| `robustness.py` | Jackknife leave-one-out stability | "Run LOO — if single module removal breaks a claim, flag fragile" |
| `reporting.py` | Structured JSON/Markdown reports | "Every claim needs: raw p, FDR-adjusted p, effect size, robustness flag" |
| `cli_demo.py` | CLI entry point | Runs full validation suite |

## Integration Plan

1. **Phase 1 — Implement `dependency_audit.py`** first (no external deps, can validate immediately against runner.py)
2. **Phase 2 — Implement `null_models.py` + `fdr_correction.py`** (requires numpy/scipy; produces calibrated p-values)
3. **Phase 3 — Implement `effect_sizes.py` + `robustness.py`** (augments convergence claims with strength metrics)
4. **Phase 4 — Implement `similarity_significance.py`** (family mirror statistical testing)
5. **Phase 5 — Wire `reporting.py` + `cli_demo.py`** to produce final validation report

## Usage

```bash
cd Engine
python -m tools.stats.cli_demo --input output.json --output-dir reports/stats/
```

## Dependencies

- Python 3.10+ (stdlib only for Phase 1)
- numpy + scipy (Phase 2+, optional — graceful degradation if unavailable)
- No SIRR engine dependencies — reads output.json as input
