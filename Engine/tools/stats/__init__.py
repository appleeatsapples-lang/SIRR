"""DeepSeek Statistical Validation Framework for SIRR.

Scaffolded 2026-03-04. Implements the statistical rigor recommendations
from DeepSeek Validator Round 2. Each module is independently usable
and imports only from stdlib + numpy/scipy (optional).

Modules:
    null_models          — Permutation and bootstrap null distributions
    dependency_audit     — Module input dependency graph analysis
    fdr_correction       — Benjamini-Hochberg FDR correction for multiple comparisons
    effect_sizes         — Cohen's d, Cramér's V, eta-squared for convergence claims
    similarity_significance — Significance testing for family/cross-profile similarity
    robustness           — Jackknife and leave-one-out stability analysis
    reporting            — Structured JSON/Markdown report generation
    cli_demo             — CLI entry point for running validation suite
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Ensure Engine/ is on sys.path so sirr_core imports work
_ENGINE_DIR = Path(__file__).resolve().parent.parent.parent
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from sirr_core.types import SystemResult


def analyze_run(output_path: str = "output.json",
                mc_path: str | None = None) -> dict[str, Any]:
    """Load a SIRR engine run and produce a statistical validation summary.

    Args:
        output_path: Path to output.json from runner.py
        mc_path:     Optional path to Monte Carlo baseline results JSON

    Returns:
        Dict with keys: profile, module_count, certainty_breakdown,
        convergences, baseline, and framework_status for each stats module.
    """
    out_file = Path(output_path)
    if not out_file.exists():
        raise FileNotFoundError(f"Output not found: {output_path}")

    data = json.loads(out_file.read_text())

    # ── Extract results ──
    results_raw = data.get("results", [])
    module_count = len(results_raw)

    # ── Certainty breakdown ──
    certainty_counts: dict[str, int] = {}
    for r in results_raw:
        cert = r.get("certainty", "UNKNOWN")
        certainty_counts[cert] = certainty_counts.get(cert, 0) + 1

    # ── Synthesis / convergence data ──
    # Synthesis lives at top-level data["synthesis"], not inside results[]
    synthesis = data.get("synthesis")

    convergences: dict[str, Any] = {}
    if synthesis:
        num_conv = synthesis.get("number_convergences", [])
        elem_conv = synthesis.get("element_convergences", [])
        convergences = {
            "number_convergences": len(num_conv),
            "element_convergences": len(elem_conv),
            "resonance_count": synthesis.get("resonance_count", 0),
            "significant_count": synthesis.get("significant_count", 0),
            "top_numbers": [
                {"number": c["number"], "systems": c["system_count"],
                 "groups": c["group_count"], "tier": c["tier"]}
                for c in sorted(num_conv, key=lambda x: -x["system_count"])[:5]
            ],
        }

    # ── Monte Carlo baseline ──
    baseline_summary: dict[str, Any] | None = None
    if mc_path:
        mc_file = Path(mc_path)
        if mc_file.exists():
            mc = json.loads(mc_file.read_text())
            bl = mc.get("baseline", {})
            # P95/P99 are derived from the max_system_count distribution
            p95 = p99 = None
            dist = mc.get("distributions", {}).get("max_system_count", {})
            n = mc.get("n", 10000)
            if dist and n:
                cumul = 0
                for k in sorted(dist.keys(), key=int):
                    cumul += dist[k]
                    pct = cumul / n * 100
                    if pct >= 95 and p95 is None:
                        p95 = int(k)
                    if pct >= 99 and p99 is None:
                        p99 = int(k)
            baseline_summary = {
                "n": mc.get("n"),
                "max_sys_mean": bl.get("max_sys_mean"),
                "max_sys_median": bl.get("max_sys_median"),
                "p95": p95,
                "p99": p99,
            }

    # ── Framework module status ──
    framework_status = {
        "null_models": "STUB",
        "dependency_audit": "STUB",
        "fdr_correction": "STUB",
        "effect_sizes": "STUB",
        "similarity_significance": "STUB",
        "robustness": "STUB",
        "reporting": "STUB",
    }

    return {
        "profile": data.get("profile", {}).get("subject", "UNKNOWN"),
        "module_count": module_count,
        "certainty_breakdown": certainty_counts,
        "convergences": convergences,
        "baseline": baseline_summary,
        "framework_status": framework_status,
    }
