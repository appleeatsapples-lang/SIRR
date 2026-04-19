"""
Unified Product Regression Tests
=================================
Locks the coherence score + tension sentence + per-domain module counts
for the synthetic golden profile. Any future edit to the engine,
unified_synthesis, or the allowlist will be caught by these tests.

Run from Engine/ directory:
    python3 tests/unified/test_unified_regression.py

Fixtures live in tests/unified/fixtures/ and are regenerated when
this file is run with --lock (overwrites existing fixtures).
"""
from __future__ import annotations
import json
import sys
import os
from pathlib import Path
from collections import Counter

# Allow running from Engine/ root
THIS = Path(__file__).resolve()
ENGINE = THIS.parent.parent.parent
sys.path.insert(0, str(ENGINE))

from unified_synthesis import compute_unified_synthesis


# ── Load DOMAIN_MAP from server.py without triggering FastAPI init ──
def _load_domain_map():
    import ast
    src = (ENGINE / "web_backend" / "server.py").read_text()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Name) and t.id == "DOMAIN_MAP":
                return ast.literal_eval(node.value)
    raise RuntimeError("DOMAIN_MAP not found in server.py")


DOMAIN_MAP = _load_domain_map()
ALLOWLIST = set(DOMAIN_MAP.keys())


# ── Pipeline (mirrors what /api/analyze does) ──

def apply_unified_pipeline(output: dict) -> dict:
    """Apply the same transformation server.py does for unified=True."""
    output["unified"] = compute_unified_synthesis(output)
    filtered = []
    for r in output.get("results", []):
        rid = r.get("id", "")
        if rid in ALLOWLIST:
            r["domain"] = DOMAIN_MAP[rid]
            filtered.append(r)
    output["results"] = filtered
    return output


def extract_regression_shape(output: dict) -> dict:
    """Reduce the full pipeline output to a stable fingerprint for regression."""
    u = output.get("unified", {})
    coh = u.get("coherence", {})
    ten = u.get("tension", {})
    domain_counts = Counter(r.get("domain") for r in output.get("results", []))

    return {
        "profile": {
            "subject": output["profile"]["subject"],
            "dob": output["profile"]["dob"],
            "core_numbers": output["profile"]["core_numbers"],
        },
        "coherence": {
            "score": coh.get("score"),
            "tier": coh.get("tier"),
            "label": coh.get("label"),
            "components": coh.get("components"),
        },
        "tension": {
            "sentence": ten.get("sentence"),
            "primary_type": ten.get("primary", {}).get("type") if ten.get("primary") else None,
            "all_types": [t.get("type") for t in ten.get("all", [])],
        },
        "results": {
            "total_surfaced": sum(domain_counts.values()),
            "per_domain": dict(domain_counts),
        },
    }



# ── Test profiles ──

PROFILES = [
    {
        "name": "synthetic",
        "source": ENGINE / "fixtures" / "synthetic_output.json",
        "fixture": THIS.parent / "fixtures" / "synthetic_unified.json",
    },
]


def lock_fixtures():
    """Regenerate golden fixtures from current pipeline."""
    os.makedirs(THIS.parent / "fixtures", exist_ok=True)
    for p in PROFILES:
        raw = json.load(open(p["source"]))
        cooked = apply_unified_pipeline(raw)
        shape = extract_regression_shape(cooked)
        p["fixture"].write_text(json.dumps(shape, indent=2, ensure_ascii=False))
        print(f"  LOCKED: {p['name']:<12} score={shape['coherence']['score']:<3} "
              f"results={shape['results']['total_surfaced']}  → {p['fixture'].name}")


def run_tests() -> int:
    """Run all regressions. Return 0 = pass, nonzero = failures."""
    failures = 0
    for p in PROFILES:
        if not p["fixture"].exists():
            print(f"  ⚠  {p['name']:<12} NO FIXTURE (run with --lock first)")
            failures += 1
            continue

        expected = json.loads(p["fixture"].read_text())
        raw = json.load(open(p["source"]))
        cooked = apply_unified_pipeline(raw)
        actual = extract_regression_shape(cooked)

        if actual == expected:
            print(f"  ✓  {p['name']:<12} score={actual['coherence']['score']:<3} "
                  f"results={actual['results']['total_surfaced']:<3}  PASS")
        else:
            print(f"  ✗  {p['name']:<12} REGRESSION DETECTED")
            # Find specific diffs
            for key in ("coherence", "tension", "results"):
                if actual.get(key) != expected.get(key):
                    print(f"       {key}:")
                    print(f"         expected: {expected.get(key)}")
                    print(f"         actual  : {actual.get(key)}")
            failures += 1

    return failures


if __name__ == "__main__":
    if "--lock" in sys.argv:
        print("Regenerating fixtures:")
        lock_fixtures()
        print("Done.")
    else:
        print("Running unified pipeline regression tests:")
        rc = run_tests()
        if rc == 0:
            print(f"\n  All {len(PROFILES)} profiles passed.")
        else:
            print(f"\n  {rc} profile(s) failed regression.")
        sys.exit(rc)
