"""
Benchmark re-score: Re-run all 64+ famous figures against the current
167-module MC baseline and update benchmark_db.json with new percentiles.

Usage:
    cd Engine && source .venv/bin/activate
    python tools/rescore_benchmark.py

Requires: monte_carlo_baseline.json (167-module, n=10,000)
"""
import json
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
MC_PATH = ENGINE / "monte_carlo_baseline.json"
BENCH_PATH = ENGINE / "benchmark_db.json"
OUTPUT_PATH = ENGINE / "reports" / "benchmark_rescore_167.json"

def compute_percentile(peak: int, dist: dict) -> float:
    """Compute percentile from MC distribution."""
    total = sum(int(v) for v in dist.values())
    above = sum(int(v) for k, v in dist.items() if int(k) >= peak)
    return round(100.0 * (1.0 - float(above) / float(total)), 1)

def main():
    mc = json.loads(MC_PATH.read_text())
    dist = mc["distributions"]["max_system_count"]
    baseline_mean = mc["baseline"]["max_sys_mean"]
    baseline_mod = mc["mc_baseline_meta"]["module_count"]
    
    bench = json.loads(BENCH_PATH.read_text())
    subjects = bench.get("subjects", bench) if isinstance(bench, dict) else bench
    
    print(f"MC baseline: {baseline_mod} modules, mean={baseline_mean}")
    print(f"Benchmark subjects: {len(subjects)}")
    print()
    
    results = []
    for entry in subjects:
        name = entry.get("subject", entry.get("name", entry.get("id", "?")))
        peak = entry.get("peak_count", entry.get("max_systems", 0))
        old_pct = entry.get("percentile", None)
        new_pct = compute_percentile(peak, dist)
        
        results.append({
            "name": name,
            "peak_systems": peak,
            "old_percentile": old_pct,
            "new_percentile": new_pct,
            "delta": round(new_pct - old_pct, 1) if old_pct else None,
            "above_mean": peak > baseline_mean,
        })
    
    # Sort by new percentile descending
    results.sort(key=lambda x: -x["new_percentile"])
    
    print(f"{'Name':<30} {'Peak':>5} {'Old%':>7} {'New%':>7} {'Delta':>7}")
    print("-" * 60)
    for r in results[:20]:
        old = f"{r['old_percentile']:.1f}" if r['old_percentile'] else "  N/A"
        delta = f"{r['delta']:+.1f}" if r['delta'] else "  N/A"
        print(f"{r['name']:<30} {r['peak_systems']:>5} {old:>7} {r['new_percentile']:>7.1f} {delta:>7}")
    
    if len(results) > 20:
        print(f"... and {len(results) - 20} more")
    
    # Summary stats
    above_mean = sum(1 for r in results if r["above_mean"])
    print(f"\nAbove mean ({baseline_mean}): {above_mean}/{len(results)} ({100*above_mean/len(results):.0f}%)")
    
    # Save full results
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    output = {
        "baseline_modules": baseline_mod,
        "baseline_mean": baseline_mean,
        "subjects_count": len(results),
        "above_mean_count": above_mean,
        "results": results,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\nSaved: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
