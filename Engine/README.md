# SIRR Engine — Deterministic Computation Core

238 numerological, astrological, and divinatory modules across 22+ civilizational traditions. Single-subject architecture: one person's name (Latin + Arabic) and date of birth.

## Quick Start

```bash
# Setup (first time)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run engine (default synthetic FATIMA profile)
python runner.py

# Run engine on a specific fixture
python runner.py fixtures/synthetic_full_nasab.json --output /tmp/out.json

# Run tests
pytest
```

## Output

- `output.json` — Full engine output (238 modules + synthesis + narrative)
- Terminal report with certainty labels and convergence summary

## Architecture

```
Input (name + DOB) -> Modules (pure compute) -> SystemResult (with certainty tag)
                                                      |
                                                Synthesis (cross-system convergence)
                                                      |
                                                Render (terminal + JSON)
                                                      |
                                                Ledger (contradiction flagging)
```

## Module Contract

Every module exports `compute(profile, constants, **kwargs) -> SystemResult` with:

- `id` — stable string identifier
- `name` — human-readable name
- `certainty` — one of `COMPUTED_STRICT | LOOKUP_FIXED | APPROX | NEEDS_EPHEMERIS | NEEDS_CORRELATION | NEEDS_INPUT | META`
- `data` — module-specific result dict
- `constants_version` — version string
- `references` — list of source citations

## Determinism

Every output is deterministic: same input → identical output. Modules are pure compute against bundled lookup tables and the Swiss Ephemeris.
