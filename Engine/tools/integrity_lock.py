#!/usr/bin/env python3
"""
SIRR Engine Integrity Lock — Automated Health Check
====================================================
Checks module count, test pass rate, convergence coverage,
fixture coverage, and MC baseline freshness. Produces a
scored health report and exits 0 (healthy) or 1 (degraded).

Usage:
    python -m tools.integrity_lock
    python tools/integrity_lock.py
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent.parent
EXCLUDED_BY_DESIGN_COUNT = 40  # categorical/timeline/grid modules with set() in CONVERGENCE_FIELDS


def _git_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ENGINE_DIR), stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def count_modules() -> int:
    output_path = ENGINE_DIR / "output.json"
    data = json.loads(output_path.read_text(encoding="utf-8"))
    return len(data["results"])


def run_tests() -> tuple[int, int]:
    """Run pytest, return (passed, failed)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--tb=no", "-q"],
        cwd=str(ENGINE_DIR),
        capture_output=True, text=True, timeout=120
    )
    output = result.stdout + result.stderr
    # Parse "177 passed" or "175 passed, 2 failed"
    passed = failed = 0
    for line in output.strip().split("\n"):
        line = line.strip()
        if "passed" in line or "failed" in line:
            import re
            m_pass = re.search(r"(\d+)\s+passed", line)
            m_fail = re.search(r"(\d+)\s+failed", line)
            if m_pass:
                passed = int(m_pass.group(1))
            if m_fail:
                failed = int(m_fail.group(1))
    return passed, failed


def count_convergence_active() -> int:
    data = json.loads((ENGINE_DIR / "output.json").read_text(encoding="utf-8"))
    active = set()
    for conv in data["synthesis"]["number_convergences"]:
        active.update(conv.get("systems", []))
    return len(active)


def count_fixture_coverage() -> int:
    """Count modules with at least 1 fixture entry in any expected_*_strict.json."""
    fixture_dir = ENGINE_DIR / "fixtures"
    covered = set()
    for fp in fixture_dir.glob("expected_*_strict.json"):
        data = json.loads(fp.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            covered.update(data.keys())
        elif isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict) and "id" in entry:
                    covered.add(entry["id"])
    return len(covered)


def check_baseline_freshness(module_count: int) -> float:
    """Check MC baseline meta. Returns freshness score 0.0/0.5/1.0."""
    baseline_path = ENGINE_DIR / "monte_carlo_baseline.json"
    if not baseline_path.exists():
        return 0.0
    try:
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
        meta = data.get("mc_baseline_meta", {})
        bl_modules = meta.get("module_count")
        if bl_modules is None or bl_modules == "unknown":
            return 0.0
        diff = abs(int(bl_modules) - module_count)
        if diff <= 5:
            return 1.0
        elif diff <= 20:
            return 0.5
        else:
            return 0.0
    except Exception:
        return 0.0


def main():
    print("SIRR Engine Integrity Lock")
    print("=" * 50)

    # 1. Module count
    module_count = count_modules()
    print(f"  Modules in output.json:  {module_count}")

    # 2. Tests
    passed, failed = run_tests()
    total_tests = passed + failed
    test_pass_rate = passed / total_tests if total_tests > 0 else 0.0
    print(f"  Tests:                   {passed} passed, {failed} failed ({test_pass_rate:.1%})")

    # 3. Convergence active
    conv_active = count_convergence_active()
    print(f"  Convergence-active:      {conv_active}/{module_count}")

    # 4. Fixture coverage
    fixture_covered = count_fixture_coverage()
    fixture_rate = fixture_covered / module_count if module_count > 0 else 0.0
    print(f"  Fixture coverage:        {fixture_covered}/{module_count} ({fixture_rate:.1%})")

    # 5. Baseline freshness
    freshness = check_baseline_freshness(module_count)
    freshness_label = {1.0: "FRESH", 0.5: "STALE", 0.0: "MISSING/OUTDATED"}
    print(f"  Baseline freshness:      {freshness} ({freshness_label.get(freshness, '?')})")

    # 6. Health score
    eligible = module_count - EXCLUDED_BY_DESIGN_COUNT
    whitelist_coverage = conv_active / eligible if eligible > 0 else 0.0

    health = (
        test_pass_rate * 0.35
        + whitelist_coverage * 0.25
        + fixture_rate * 0.20
        + freshness * 0.20
    )

    print(f"\n  {'─' * 40}")
    print(f"  Whitelist coverage adj:  {conv_active}/{eligible} ({whitelist_coverage:.1%})")
    print(f"  HEALTH SCORE:            {health:.4f}")
    status = "HEALTHY" if health >= 0.85 else "DEGRADED"
    print(f"  STATUS:                  {status}")
    print(f"  {'─' * 40}")

    # 7. Write status snapshot
    git_hash = _git_hash()
    now = datetime.now(timezone.utc)
    snapshot = {
        "generated": now.isoformat(),
        "engine_commit": git_hash,
        "module_count": module_count,
        "tests_passed": passed,
        "tests_failed": failed,
        "tests_total": total_tests,
        "test_pass_rate": round(test_pass_rate, 4),
        "convergence_active": conv_active,
        "excluded_by_design": EXCLUDED_BY_DESIGN_COUNT,
        "eligible_for_convergence": eligible,
        "whitelist_coverage_adjusted": round(whitelist_coverage, 4),
        "fixture_covered": fixture_covered,
        "fixture_rate": round(fixture_rate, 4),
        "baseline_freshness": freshness,
        "health_score": round(health, 4),
        "status": status,
    }

    artifacts_dir = ENGINE_DIR / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    ts = now.strftime("%Y-%m-%d_%H%M")
    snapshot_path = artifacts_dir / f"status_{ts}.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"\n  Snapshot: {snapshot_path.relative_to(ENGINE_DIR)}")

    sys.exit(0 if health >= 0.85 else 1)


if __name__ == "__main__":
    main()
