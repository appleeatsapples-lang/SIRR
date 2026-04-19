#!/usr/bin/env python3
"""CLI entry point for running the DeepSeek statistical validation suite.

Usage:
    python -m tools.stats.cli_demo output.json --mc-path reports/monte_carlo_results.json
"""
from __future__ import annotations

import argparse
import json
import sys

from tools.stats import analyze_run


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SIRR Statistical Validation Suite (DeepSeek framework)"
    )
    parser.add_argument("output", nargs="?", default="output.json",
                        help="Path to SIRR engine output.json")
    parser.add_argument("--mc-path", default=None,
                        help="Path to Monte Carlo baseline JSON")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of formatted text")
    args = parser.parse_args()

    try:
        report = analyze_run(args.output, mc_path=args.mc_path)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    # ── Formatted text output ──
    print("SIRR Statistical Validation Suite")
    print("=" * 50)
    print(f"Profile:  {report['profile']}")
    print(f"Modules:  {report['module_count']}")
    print()

    print("Certainty Breakdown:")
    for cert, count in sorted(report["certainty_breakdown"].items(),
                               key=lambda x: -x[1]):
        print(f"  {cert:<20s} {count:>3d}")
    print()

    conv = report.get("convergences", {})
    if conv:
        print("Convergence Summary:")
        print(f"  Number convergences:  {conv.get('number_convergences', 0)}")
        print(f"  Element convergences: {conv.get('element_convergences', 0)}")
        print(f"  Resonance claims:     {conv.get('resonance_count', 0)}")
        print(f"  Significant claims:   {conv.get('significant_count', 0)}")
        top = conv.get("top_numbers", [])
        if top:
            print("  Top convergences:")
            for t in top:
                print(f"    Number {t['number']:>2d}: "
                      f"{t['systems']} systems, {t['groups']} groups "
                      f"[{t['tier']}]")
        print()

    bl = report.get("baseline")
    if bl:
        print("Monte Carlo Baseline:")
        print(f"  n={bl.get('n')}, mean_peak={bl.get('max_sys_mean')}, "
              f"P95={bl.get('p95')}, P99={bl.get('p99')}")
        print()

    print("Framework Module Status:")
    for mod, status in report["framework_status"].items():
        print(f"  {mod:<30s} [{status}]")
    print()
    print("All 7 analysis modules are scaffolded (STUB).")
    print("Implement by wiring DeepSeek Round 2 specs into each module.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
