# Deferred test suite

Nine pytest modules that were excluded from the active suite during the
public-repo separation cycle (April 2026). They are kept here verbatim
for reference and progressive restoration; pytest is configured (in
`pyproject.toml` / `pytest.ini`) to skip this directory via
`norecursedirs = _deferred`.

## Why deferred

These tests were tightly coupled to a specific person's profile via
hand-curated golden fixtures (`expected_muhab_strict.json`,
`expected_batch9_strict.json`, `expected_round4_strict.json`,
`muhab_unified.json`, etc.) and inline `subject="MUHAB ..."` literals.
When the public engine repo replaced the personal profile with a
synthetic demo (`fixtures/synthetic_profile.json` — FATIMA AHMED OMAR
ALKATIB, 1990-03-15, Cairo), every numeric assertion in these tests
broke because it referenced values computed from a different birth
profile.

In addition, the legacy goldens carried schema drift relative to the
current engine output (e.g., `expected_muhab_strict.json` expected
`bridges.lp_su` flat-keyed but the live engine emits
`data.bridges.lp_su` nested), so even regenerating against a new
profile would have required test-side restructuring on top of golden
regeneration.

The pragmatic call was: ship the public repo with a clean smoke suite
(see `tests/test_engine_synthetic.py` and the rewritten
`test_transliterate.py`) and defer per-module strict regression for a
follow-up cycle.

## What each file covered

| File | Scope |
|---|---|
| `test_strict_outputs.py` | Per-module strict regression (~140 modules) against `expected_muhab_strict.json`. Each test `compute()`s one module and asserts every documented field equals the golden value. |
| `test_batch9_strict.py` | Strict regression for the Batch-9 module wave (cornerstone, life_purpose, steiner_cycles, enneagram_dob, etc.) against `expected_batch9_strict.json`. |
| `test_round4_strict.py` | Strict regression for the Round-4 cross-tradition modules (kala_sarpa_check, panchamahabhuta, ayurvedic_constitution, mantra_seed_syllable, etc.) against `expected_round4_strict.json`. |
| `test_torah_figures.py` | Cross-checks the `torah_figures` module against the locked corpus (68 Tanakh figures, Hebrew Gematria standard). |
| `test_quranic_figures_full.py` | Cross-checks the `quranic_figures` module against the locked corpus (46 named Quranic figures across prophets/humans/angels/jinn). |
| `test_nt_figures.py` | Cross-checks the `nt_figures` module against the locked corpus (34 New Testament figures, Greek Isopsephy). |
| `test_cross_scripture.py` | Cross-tradition intersection assertions across torah/nt/quranic figure roots (e.g., عيسى/Ἰησοῦς both reduce to 6). |
| `test_synastry_parents.py` | Synastry between two family-fixture profiles (gen2_omar × gen2_miral). Fixtures purged from public repo. |
| `test_dyad.py` | Cross-tradition dyad analysis between two specific family members (Muhab × Mazen). Output JSON purged from public repo. |

## Restoration path

1. Pick one deferred module per cycle.
2. Regenerate its golden against the current synthetic profile:
   - Run the engine: `python runner.py fixtures/synthetic_profile.json --output fixtures/synthetic_output.json`
   - Extract the relevant module's `data` block from `synthetic_output.json` and write a synthetic golden file (mirror the shape the test code reads).
3. Update the test file:
   - Replace the inline `subject="MUHAB ..."` literal with FATIMA's nasab and the matching DOB / location / mother fields.
   - Repoint the `_load()` helper at the new synthetic golden.
   - Adjust any assertions whose field paths drifted between the legacy golden shape and live engine output.
4. Move the file out of `_deferred/` back to `tests/` and run.
5. Verify: `pytest tests/<the_one_file>.py --tb=short`.
6. If green, commit. Otherwise iterate.

For the family-coupled tests (`test_synastry_parents.py`, `test_dyad.py`),
restoration additionally requires generating synthetic family fixtures
or rewriting the tests to use a synthetic dyad — which itself is a
follow-up build.
