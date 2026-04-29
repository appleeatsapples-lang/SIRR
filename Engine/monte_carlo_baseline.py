"""
SIRR Monte Carlo Baseline — Statistical Denominator for Convergence Claims
===========================================================================

Runs N random name+date profiles through the engine and measures convergence
distributions. Used for S3 false-positive-rate calibration and as the n=10,000
baseline that customer percentile displays reference.

Output: a JSON file with distributions of:
  - max_system_count (peak convergence count for any single root)
  - tier1_count (TIER_1_RESONANCE + TIER_1_SIGNIFICANT events)
  - dominant_number
  - lp_convergence_systems
  - lp_matches_dominant

Plus baseline summary stats (mean, median, p_values for the canonical demo
profile).

Companion docs:
  - Docs/engine/UNIFIED_ARCHITECTURE.md (defines what convergence is)
  - Docs/engine/S3_CALIBRATION_BAR.md (locked FP target rates)
  - Docs/engine/S3_FINDINGS_2026-04-29.md (most recent measurement)

Usage:
    python3 -m monte_carlo_baseline                   # n=100 smoke test
    python3 -m monte_carlo_baseline --n 1000          # n=1000 fast pass
    python3 -m monte_carlo_baseline --n 10000         # n=10000 canonical
    python3 -m monte_carlo_baseline --n 1000 --out reports/mc_baseline.json

The canonical n=10,000 baseline is bundled into the iOS app data at
PRIVATE/App/BundledData/monte_carlo_results.json (built 2026-04-11).
This script regenerates it for the current engine.

EXPECTED RUNTIME (rough, dependent on hardware):
  - n=100:     ~1-2 minutes  (subprocess overhead dominates at small N)
  - n=1000:    ~10-15 minutes
  - n=10000:   ~2-3 hours    (recommend running detached)

The subprocess approach (vs in-process import) is intentional: it avoids
touching Engine/runner.py (which is a doctrine path-trigger requiring R2
review) and ensures the MC measures the same code path real customer
runs use.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import random
import subprocess
import sys
import time
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Optional

ENGINE_DIR = Path(__file__).parent
RUNNER_PATH = ENGINE_DIR / "runner.py"

# ─── ARABIC MALE NAME POOL ─────────────────────────────────────────────
# Same pool as the canonical April 11 baseline. Adding new names changes
# the random distribution and should be a deliberate calibration commit.
FIRST_NAMES = [
    ("أحمد", "AHMAD"),       ("محمد", "MUHAMMAD"),  ("علي", "ALI"),
    ("خالد", "KHALID"),      ("عمر", "OMAR"),       ("يوسف", "YOUSSEF"),
    ("إبراهيم", "IBRAHIM"),  ("حسن", "HASSAN"),     ("سعيد", "SAEED"),
    ("طارق", "TARIQ"),       ("فهد", "FAHD"),       ("سلطان", "SULTAN"),
    ("ناصر", "NASSER"),      ("عبدالله", "ABDULLAH"), ("ماجد", "MAJID"),
    ("بدر", "BADR"),         ("فيصل", "FAISAL"),    ("منصور", "MANSOUR"),
    ("رائد", "RAED"),        ("هاشم", "HASHIM"),    ("كريم", "KARIM"),
    ("جمال", "JAMAL"),       ("وليد", "WALID"),     ("زياد", "ZIAD"),
    ("سامي", "SAMI"),        ("رامي", "RAMI"),      ("عادل", "ADIL"),
    ("صالح", "SALIH"),       ("مصطفى", "MUSTAFA"),  ("ياسر", "YASER"),
]
FATHER_NAMES = list(FIRST_NAMES)  # Same pool
FAMILY_NAMES = [
    ("الحربي", "ALHARBI"),   ("الشمري", "ALSHAMMARI"), ("القحطاني", "ALQAHTANI"),
    ("الدوسري", "ALDOSARI"), ("العتيبي", "ALOTAIBI"),  ("الزهراني", "ALZAHRANI"),
    ("الغامدي", "ALGHAMDI"), ("الشهري", "ALSHEHRI"),   ("المطيري", "ALMUTAIRI"),
    ("الرشيد", "ALRASHEED"), ("الأنصاري", "ALANSARI"), ("التميمي", "ALTAMIMI"),
    ("الفيفي", "ALFAIFI"),   ("السبيعي", "ALSUBAIE"),  ("الخالدي", "ALKHALEDI"),
]


def _generate_random_profile_dict(today: date) -> dict[str, Any]:
    """Generate a random Arabic male profile as a dict matching the fixture
    schema runner.load_profile expects."""
    first_ar, first_en = random.choice(FIRST_NAMES)
    father_ar, father_en = random.choice(FATHER_NAMES)
    family_ar, family_en = random.choice(FAMILY_NAMES)

    full_en = f"{first_en} {father_en} {family_en}"
    full_ar = f"{first_ar} {father_ar} {family_ar}"

    # Random DOB in 1960-2005 (matches canonical baseline range)
    start = date(1960, 1, 1)
    end = date(2005, 12, 31)
    days_range = (end - start).days
    dob = start + timedelta(days=random.randint(0, days_range))

    return {
        "subject": full_en,
        "arabic": full_ar,
        "dob": dob.isoformat(),
        "today": today.isoformat(),
        "birth_time_local": "12:00",
        "timezone": "Asia/Riyadh",
        "location": "Riyadh",
        "gender": "male",
        "latitude": 24.7136,
        "longitude": 46.6753,
        "utc_offset": 3.0,
    }


def _run_one(seed_profile_idx: tuple[int, int]) -> Optional[dict[str, Any]]:
    """Run a single random profile through the engine. Returns synthesis
    stats. Designed to be called by multiprocessing.Pool.map."""
    seed, idx = seed_profile_idx
    random.seed(seed + idx)
    today = date.today()
    profile = _generate_random_profile_dict(today)

    # Write to a unique temp fixture and run runner.py
    tmp_fixture = ENGINE_DIR / f"_mc_fixture_{idx}.json"
    tmp_output = ENGINE_DIR / f"_mc_output_{idx}.json"

    try:
        tmp_fixture.write_text(json.dumps(profile), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(RUNNER_PATH), str(tmp_fixture),
             "--output", str(tmp_output)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=ENGINE_DIR,
        )
        if result.returncode != 0:
            return None
        if not tmp_output.exists():
            return None
        out = json.loads(tmp_output.read_text(encoding="utf-8"))
        synth = out.get("synthesis", {})
        ncs = synth.get("number_convergences", [])
        if not ncs:
            max_sys = 0
            dominant = None
            tier1_count = 0
        else:
            max_entry = max(ncs, key=lambda nc: nc.get("system_count", 0))
            max_sys = max_entry.get("system_count", 0)
            dominant = max_entry.get("number")
            tier1_count = sum(
                1 for nc in ncs
                if nc.get("tier") in ("TIER_1_RESONANCE", "TIER_1_SIGNIFICANT")
            )
        # Life-path convergence (read from output's profile.core_numbers, set by load_profile)
        out_profile = out.get("profile", {})
        out_core = out_profile.get("core_numbers", {})
        lp = out_core.get("life_path")
        lp_systems = 0
        lp_matches = False
        if lp is not None and ncs:
            lp_entry = next((nc for nc in ncs if nc.get("number") == lp), None)
            if lp_entry:
                lp_systems = lp_entry.get("system_count", 0)
            if dominant == lp:
                lp_matches = True
        return {
            "max_sys": max_sys,
            "tier1_count": tier1_count,
            "total": len(ncs),
            "dominant": dominant,
            "lp": lp,
            "lp_sys": lp_systems,
            "lp_matches_dominant": lp_matches,
        }
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None
    finally:
        tmp_fixture.unlink(missing_ok=True)
        tmp_output.unlink(missing_ok=True)


def run_mc(n: int = 100, seed: int = 42, workers: Optional[int] = None,
           progress_every: int = 10) -> dict[str, Any]:
    """Run a Monte Carlo baseline of N random profiles. Returns aggregated
    distributions and summary stats."""
    workers = workers or max(1, mp.cpu_count() - 1)
    print(f"Running MC: n={n}, workers={workers}, seed={seed}")
    print(f"Engine: {ENGINE_DIR}")
    print()

    t0 = time.time()
    args = [(seed, i) for i in range(n)]

    completed = []
    failures = 0
    with mp.Pool(workers) as pool:
        for i, result in enumerate(pool.imap_unordered(_run_one, args, chunksize=4), start=1):
            if result is None:
                failures += 1
            else:
                completed.append(result)
            if i % progress_every == 0 or i == n:
                elapsed = time.time() - t0
                rate = i / elapsed if elapsed > 0 else 0
                eta = (n - i) / rate if rate > 0 else 0
                print(f"  [{i}/{n}] elapsed {elapsed:.0f}s | {rate:.2f}/s | "
                      f"ETA {eta:.0f}s | failures {failures}")

    elapsed = time.time() - t0
    print()
    print(f"Done. {len(completed)}/{n} profiles completed in {elapsed:.1f}s")
    if failures:
        print(f"WARNING: {failures} profiles failed (see runner errors above)")

    if not completed:
        raise RuntimeError("Zero profiles completed — MC run failed")

    # Aggregate
    max_sys_vals = [c["max_sys"] for c in completed]
    tier1_vals = [c["tier1_count"] for c in completed]
    total_vals = [c["total"] for c in completed]
    dom_vals = [c["dominant"] for c in completed if c["dominant"] is not None]
    lp_match_count = sum(1 for c in completed if c["lp_matches_dominant"])
    lp_sys_vals = [c["lp_sys"] for c in completed]
    lp_at_16_plus = sum(1 for c in completed
                        if c["lp_matches_dominant"] and c["lp_sys"] >= 16)

    n_completed = len(completed)
    return {
        "mc_baseline_meta": {
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
            "module_count": "238 (from runner.py at run time)",
            "runs": n_completed,
            "engine_commit": _git_head_commit(),
        },
        "n": n_completed,
        "elapsed_s": round(elapsed, 1),
        "baseline": {
            "max_sys_mean": round(sum(max_sys_vals) / n_completed, 2),
            "max_sys_median": sorted(max_sys_vals)[n_completed // 2],
            "max_sys_max": max(max_sys_vals),
            "t1_mean": round(sum(tier1_vals) / n_completed, 2),
            "t1_median": sorted(tier1_vals)[n_completed // 2],
            "lp_match_rate": round(lp_match_count / n_completed, 4),
            "lp_sys_mean": round(sum(lp_sys_vals) / n_completed, 2),
        },
        "p_values": {
            "lp_matches_dominant": round(lp_match_count / n_completed, 4),
            "lp_at_16_plus_systems": round(lp_at_16_plus / n_completed, 4),
        },
        "distributions": {
            "max_system_count": dict(Counter(max_sys_vals)),
            "tier1_count": dict(Counter(tier1_vals)),
            "dominant_number": dict(Counter(dom_vals)),
            "lp_convergence_systems": dict(Counter(lp_sys_vals)),
            "total_convergences": dict(Counter(total_vals)),
        },
    }


def _git_head_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=ENGINE_DIR.parent,
        )
        return r.stdout.strip()[:12] if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(description="SIRR Monte Carlo Baseline")
    parser.add_argument("--n", type=int, default=100,
                        help="Number of random profiles (default: 100, canonical: 10000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--workers", type=int, default=None,
                        help="Worker processes (default: cpu_count - 1)")
    parser.add_argument("--out", default="reports/mc_baseline.json",
                        help="Output JSON path (default: reports/mc_baseline.json)")
    args = parser.parse_args()

    out_path = ENGINE_DIR.parent / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results = run_mc(n=args.n, seed=args.seed, workers=args.workers)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print()
    print(f"  Output: {out_path}")
    print(f"  Tier-1 distribution (top counts):")
    t1d = results["distributions"]["tier1_count"]
    for k, v in sorted(t1d.items(), key=lambda x: int(x[0])):
        print(f"    {k:>4}: {v:>6} ({100*v/results['n']:.2f}%)")
    print()
    print(f"  Max system count: mean={results['baseline']['max_sys_mean']}, "
          f"median={results['baseline']['max_sys_median']}, "
          f"max={results['baseline']['max_sys_max']}")
    print(f"  Tier-1 mean: {results['baseline']['t1_mean']}")
    print(f"  LP matches dominant: {results['baseline']['lp_match_rate']*100:.2f}%")
    print(f"  LP @ 16+ systems: {results['p_values']['lp_at_16_plus_systems']*100:.2f}%")


if __name__ == "__main__":
    main()
