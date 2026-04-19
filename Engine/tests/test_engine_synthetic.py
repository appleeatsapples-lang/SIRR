"""
Smoke tests: engine runs end-to-end on the synthetic profile.

Replaces the older profile-locked strict regression suite. These tests assert
shape-level invariants (module count, certainty mix, presence of synthesis +
psychological_mirror keys) rather than profile-specific numerical values.

For numeric regression on a specific profile, fork this file and add your
own assertions against your own fixture.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
FIXTURES = ENGINE / "fixtures"


def _load_synthetic_output() -> dict:
    """Load the pre-generated synthetic output."""
    return json.loads((FIXTURES / "synthetic_output.json").read_text())


def test_synthetic_output_loads():
    """synthetic_output.json must parse and contain a non-empty results array."""
    out = _load_synthetic_output()
    assert isinstance(out, dict)
    assert isinstance(out.get("results"), list)
    assert len(out["results"]) > 200, f"expected 200+ modules, got {len(out['results'])}"


def test_synthetic_profile_metadata():
    """Profile block carries the FATIMA synthetic identity."""
    out = _load_synthetic_output()
    profile = out["profile"]
    assert profile["subject"].startswith("FATIMA")
    assert profile["dob"] == "1990-03-15"


def test_synthetic_certainty_distribution():
    """Most modules should be COMPUTED_STRICT or LOOKUP_FIXED."""
    out = _load_synthetic_output()
    counts = {}
    for r in out["results"]:
        c = r.get("certainty")
        counts[c] = counts.get(c, 0) + 1
    locked = counts.get("COMPUTED_STRICT", 0) + counts.get("LOOKUP_FIXED", 0)
    total = sum(counts.values())
    assert locked / total > 0.85, \
        f"expected >85% locked, got {locked}/{total} = {locked/total:.1%} | {counts}"


def test_synthetic_synthesis_present():
    """Top-level synthesis block must be populated."""
    out = _load_synthetic_output()
    synth = out.get("synthesis", {})
    assert "number_convergences" in synth
    assert "convergence_count" in synth
    assert synth["convergence_count"] >= 1


def test_synthetic_psychological_mirror_present():
    """psychological_mirror should emit the dominant-root translation."""
    out = _load_synthetic_output()
    pm = out.get("psychological_mirror", {})
    assert "dominant_root_translation" in pm
    assert "constitutional_note" in pm


def test_synthetic_semantic_reading_present():
    """semantic_reading should fire at least one meta-pattern."""
    out = _load_synthetic_output()
    sr = out.get("semantic_reading", {})
    fired = [p for p in sr.get("meta_patterns_fired", []) if p.get("fired")]
    assert len(fired) >= 1, "expected >=1 meta-pattern to fire on synthetic profile"


def test_runner_runs_synthetic_end_to_end(tmp_path):
    """runner.py executes against synthetic_profile.json without crashing."""
    out_path = tmp_path / "out.json"
    venv_python = ENGINE / ".venv" / "bin" / "python3"
    py = str(venv_python) if venv_python.exists() else sys.executable
    result = subprocess.run(
        [py, str(ENGINE / "runner.py"),
         str(FIXTURES / "synthetic_profile.json"),
         "--output", str(out_path)],
        capture_output=True, text=True, cwd=str(ENGINE), timeout=180
    )
    assert result.returncode == 0, \
        f"runner failed:\nstdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"
    assert out_path.exists()
    fresh = json.loads(out_path.read_text())
    assert len(fresh["results"]) > 200
