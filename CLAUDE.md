# CLAUDE.md — SIRR Engineering Context

**Audience:** Claude (and any other model) working on this repo.
**Last refreshed:** 2026-05-02.
**Companion file:** `~/dev/SIRR/PRIVATE/CLAUDE_ORCHESTRATION.md` (operator-side context, not in this repo).

This file is the source-of-truth for engineering context. Read it at the start of any SIRR work session before acting on memory or assumptions. Memory is index-only; this file is canonical.

---

## What SIRR is

SIRR (سِرّ) is a deterministic symbolic identity engine. Given a name and birth data, it computes a unified identity profile across multiple civilizational traditions (Islamic, Hebrew, Greek, Chinese, Vedic, Hellenistic, and others). Output is one profile, not many.

**Production:** `web-production-ec2871.up.railway.app` (Railway).
**Repo:** `github.com/appleeatsapples-lang/SIRR` (public).
**Stack:** FastAPI backend, Lemon Squeezy payments, Railway hosting, AES-256-GCM AEAD for tokens, per-record encryption-at-rest.

---

## Architecture (one product, four domains)

ONE product. ONE engine. ONE unified profile. Internally there are four computation domains:

| Domain               | Modules |
|---|---|
| Numerology           | 28 |
| Name Intelligence    | 42 |
| Astro Timing         | 30 |
| Convergence          | 12 |
| **Total**            | **241 modules** (112 in customer distillate, 129 debug-only) |

**Fidelity classification:** 159 CLASSICAL / 68 MODERN_SYNTHESIS / 11 CMMA / 3 unclassified.

**Source-of-truth for module counts:** `Engine/sirr_core/module_taxonomy.py`. Do NOT trust `SIRR_MASTER_REGISTRY.md` for counts — that file tracks privacy-doctrine state, not taxonomy.

**Architecture spec:** `Docs/engine/UNIFIED_ARCHITECTURE.md`.

**Customer distillate (112 modules) is a curated subset of the 241.** Debug-only modules run but are not surfaced. The 112 cut was originally a vibe-cut for cultural familiarity, not principled — a principled re-cut is on the engineering backlog as a separate arc.

---

## Six-operator framing (replaces "convergence" headline)

Per §X.3 (locked 2026-04-30), the customer-facing framing is **six operators**, not "12 systems converge on 1":

1. agreement
2. divergence
3. anomaly
4. temporal-cascade
5. lineage
6. structural-absence

**Retired phrase:** "12 systems converge on 1" — historical reference only. Must NOT appear in customer copy, doctrine, templates, or examples. The convergence headline was structurally overstated: S3 (n=10,000 random profiles) showed 100% trigger Tier-1, making rarity claims empirically false. Only ~3 of ~10 named "convergences" are genuinely independent.

---

## Routing rules (locked)

- **Arithmetic recomputation of engine values must route to the engine** (`python3 Engine/...`), never to any LLM. Verified failure: an LLM produced Abjad Kabir 1454 → Root 5 for a name where engine shows 1385 → Root 8 (Root 5 in 0 modules).
- **Any LLM-produced number for an engine field is a defect**, not a result. Verify against `Engine/` before quoting.

---

## Scholarship corrections (locked)

Several modules compute via Arabic→X cognate mapping rather than native systems. This is admitted in each module's `note` field and must be referenced in any output that touches them:

- `mandaean_gematria` — uses cognate map. Native Mandaic uses a distinct duodecimal system (Häberl).
- `ethiopian_asmat` — uses cognate map.
- `hebrew_gematria` — uses cognate map.

**Implication:** when multiple cognate-mapped modules produce identical totals (e.g., 1385 across all three), that is **identity-by-construction, not cross-tradition convergence**. The cognate-mapping caveat is referenced in §X.5 of the claims doctrine and in `UNIFIED_ARCHITECTURE.md`.

---

## Privacy doctrine (§13)

§13 expanded to 11 sub-rules (§13.1–§13.11) during the V-3 privacy wave (closed 2026-04-27, main at `f40b192`). Public repo runs zero PII; pytest 217/217 at closure. Key sub-rules:

- §13.6 — combination-based Arabic PII patterns over bare-token substrings
- §13.7 — no-PII rule extends to PR descriptions and comments
- §13.8 — three-class taxonomy for PII scope
- §13.9 — closure-gate patterns stored outside audit surfaces
- §13.10 — explicit qualification of closure-gate-ZERO vs raw-tree-ZERO claims
- §13.11 — line-wrap-stable phrases in post-merge grep validations

Full doctrine: `Docs/doctrine/§13_*.md` (do NOT rely on this file for verbatim rules).

---

## Security baseline (current as of P2G closure, 2026-04-28)

- AES-256-GCM AEAD encrypted URL tokens
- Per-record encryption-at-rest
- Log scrubbing at 14+ sites
- `sanitize_exception()` pattern for error paths
- Idempotent delete

**Always grep before briefing audit work.** The security baseline is more mature than audit-plan templates assume; stale plans repeatedly suggest fixes that already shipped.

**Two §16.5 items still deferred** (logged in `Tools/handoff/SIRR_FUTURE_WORK.md` — that path is in PRIVATE post-gitignore):
- `hash_oid`
- `_make_slug`

---

## Test discipline

**Source of truth:** `pytest`. Run from repo root.

Recent pass counts:
- V-3 privacy wave closure (2026-04-27): 217/217
- P2G closure (2026-04-28): 240/240
- S4 launch gate (2026-04-30): 268/268
- Current main HEAD: `97cc54b` (post-PR #57, doctrine-x-v0.1.1-lock)

**CI gates** (5 checks must be green before merge): unit tests, type checks, lint, security scan, doctrine grep.

---

## Workflow

All R2+ changes go through this gate sequence:

1. Pre-flight verification (clean tree, HEAD anchor, baseline pytest)
2. Implementation on feature branch
3. Local tests pass
4. CI green (5 checks)
5. **Adversarial audit by a different model** (cross-model veto)
6. Pre-merge diff review
7. Merge
8. Railway deploy watched with fail-fast discipline
9. Post-deploy regression verification

**Doctrine document handling:** Xcode and IDEs with auto-save **must NOT open doctrine files** (§12, shipped in PR #31). Auto-formatting can silently corrupt §-numbered rules.

---

## Repo paths (canonical)

- Repo: `~/dev/SIRR/REPO/` (NOT `~/Desktop/MKB/SIRR 2/REPO/` — that's stale; iCloud-renamed location was migrated 2026-05-01)
- Private vault: `~/dev/SIRR/PRIVATE/` (paired sibling, not in this repo)
- Archive: `~/dev/SIRR/ARCHIVE/`
- Sessions/journal: `~/dev/SIRR/PRIVATE/Orchestration/Sessions/journal.txt` (in private vault — there is no `Sessions/` dir under REPO)

**Hardcoded output paths** in engine (relative to `Engine/`):
- `output.json`
- `output_original.json`
- `output_gen1_huda.json`
- `output_gen2_mazen_maternal.json`

**Env vars:**
- `SIRR_PRIVATE_OVERLAY` → `~/dev/SIRR/PRIVATE/Engine/data/private_linguistic_overlay.json` (set in `~/.zshrc`; engine degrades gracefully if absent)
- `SIRR_DATA_DIR` → Railway persistent volume path (prod only)

---

## Where to look next

| Need | File |
|---|---|
| Architecture spec | `Docs/engine/UNIFIED_ARCHITECTURE.md` |
| Module taxonomy (counts source-of-truth) | `Engine/sirr_core/module_taxonomy.py` |
| Privacy doctrine §13 | `Docs/doctrine/` |
| Claims doctrine §X v0.1 | `Docs/operations/CLAIMS_DOCTRINE_X.md` (when CC implements T3) |
| Future-work tracker | `PRIVATE/Orchestration/handoff/SIRR_FUTURE_WORK.md` |
| Operator/orchestration context | `~/dev/SIRR/PRIVATE/CLAUDE_ORCHESTRATION.md` |

---

## Refresh discipline

This file is **maintained by hand**, not generated. Update it when:
- A wave/PR closure changes the verified pytest count or HEAD anchor
- A retired phrase is added or removed
- A locked rule is added under any §-number
- A canonical path changes
- A doctrine version locks (note the version, e.g., §X v0.1 → v0.2)

Stale CLAUDE.md is worse than no CLAUDE.md. If a section's date is more than 30 days old and you're uncertain whether it's current, **verify against the source-of-truth file before acting on it**.
