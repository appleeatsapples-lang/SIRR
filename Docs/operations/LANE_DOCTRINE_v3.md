# Lane Doctrine v3 — Multi-model orchestration for SIRR

**Authors:** Claude (chat) + Codex via Muhab routing, 2026-04-25
**Status:** Final after 3 rounds of cross-model review. Ships as repo doctrine, supersedes LANE_DOCTRINE_v2.md
**Design history:** v0 (Claude solo) → Codex r1 (structural) → v1 → Codex r2 (refinements) → v2 → Codex r3 (mechanical) → v3 (this)

---

## Preamble

This document is the operational doctrine for multi-model work on SIRR. It supersedes `LANE_DOCTRINE_v2.md` (which captured P2F session lessons) by carrying forward all v2 operational rules and adding the lane structure designed in collaboration with Codex during the 2026-04-25 design exercise.

**Roles unchanged from v2.** **Anti-patterns unchanged from v2 + Codex round 1 additions.** **Working-pattern unchanged from v2.** **New material:** Risk labels (§2), Process tiers (§3), Reserved configs (§4), Auto-trigger Codex challenge mechanics (§5), Codex classification veto (§6), Closure sweep (§7).

---

## §1 — Roles (unchanged)

### Orchestrator (Claude in chat — currently web)

Reads the codebase via Desktop Commander. Writes only to
`SIRR_PRIVATE/Orchestration/Briefs/`. Does not commit, does not push,
does not deploy. State verified via tools before every decision —
never inferred from memory.

The orchestrator's job is to compose briefs that are precise enough
that the executor can implement them mechanically, with explicit
gates at each high-risk step. Briefs include: pre-flight checks,
section-by-section diffs, mandatory pre-push verification commands,
post-deploy verification commands, and stop conditions.

### Executor (Claude Code, Opus model)

Implements briefs. Commits, pushes, opens PRs, watches CI, watches
deploys. Does not make architectural choices outside the brief —
when an unspecified design question arises, asks the orchestrator
or surfaces explicitly in the implementation report. Drift into
unilateral design decisions is the anti-pattern in §8 (Claude Code error class #1).

The executor's job is to do exactly what the brief says, surface
discrepancies between brief and reality before acting on them, and
report verbatim. The executor is not a designer; the executor is a
high-trust pair of hands.

### Cross-model auditor (Codex)

Adversarial read-only audit. **Mandatory** gate when the orchestrator
wrote the spec — same-model audit by the spec author is structurally
insufficient (see §8 Claude (chat) error class #4). Routing in the
current SIRR setup: Codex CLI is not installed on the executor's
machine. The orchestrator drafts the audit prompt; Muhab routes it
to Codex from his side; results are pasted back to the orchestrator.
This adds latency (~5-15min per round) but preserves the cross-model
property. Future improvement: install a Codex CLI on the executor's
machine so the round-trip can be automated (open issue, not blocking).

Codex reads the diff against main, attacks the PR's claims, and
returns per-claim verdicts (PASS / FINDING / UNCLEAR) with
file:line evidence. Findings are real. The orchestrator's job is to
classify each finding as in-scope (apply now), defer (PR-N+1), or
escalate (architecturally new — see §7).

### Editorial approver (Muhab)

Merge gate. The bright line that no orchestrator and no executor
crosses without explicit approval. Routes Codex audits, signs off
on merge, owns post-deploy operational verification. The merge
gate is sacred — see §10.

---

## §2 — Risk labels

Every PR labeled before brief is written:

| Label | Description | Codex involvement |
|---|---|---|
| **R0** Routine | typo, dependency bump, single-file refactor with no doctrine touch | None by default; **path triggers can promote** |
| **R1** Risky | new endpoint, schema change, API surface upgrade | Optional Codex post-impl audit |
| **R2** Doctrine / privacy / security | encryption, retention, deletion, logs, payment metadata, public privacy copy, doctrine docs, auth | **Mandatory:** Codex pre-review (T2) + audit (T4) + classification veto (T5) + trigger challenge (T6) + closure sweep (T7) |
| **R3** Architecture migration | order_store encryption (P2G), database swap, auth model change, multi-tenant split | R2 + **C-lite mandatory (independent sketches from neutral problem statement)** |

Claude (chat) proposes the label. Codex can veto if the label undersells risk. Muhab resolves veto.

### R0 path triggers (mandatory escalation)

If a PR touches any of these paths, it CANNOT be R0 unless Codex sees the label or Muhab explicitly waives review. The minimum label becomes R1; if the path is on the doctrine list (`Docs/architecture/PRIVACY_TIERS.md`, `Docs/engine/SIRR_MASTER_REGISTRY.md`, `Docs/operations/LANE_DOCTRINE_v*.md`, `Engine/web/*.html`), minimum becomes R2.

**Backend runtime (→ R1 min):**
- `Engine/web_backend/**/*.py` (all backend Python: tokens, crypto, sanitize, retention, order_store, server, auth, middleware, errors, metrics, scheduler, paths, routers/*)
- `Engine/{runner,reading_generator,html_reading,unified_view,merged_view}.py` (engine pipeline)

**User-facing surfaces (→ R2 min):**
- `Engine/web/*.html` (any user- or admin-facing page; privacy, terms, success, index, admin, _error, email_template all covered) — customer-facing copy is treated as doctrine because privacy and legal claims are doctrine

**Doctrine (→ R2 min):**
- `Docs/architecture/PRIVACY_TIERS.md`
- `Docs/engine/SIRR_MASTER_REGISTRY.md`
- `Docs/operations/LANE_DOCTRINE_v*.md`

**Tests (→ R1 min):**
- `Engine/tests/**` (any test under the test tree)

**Build / CI / runtime / deployment config (→ R1 min):**
- `.github/workflows/ci.yml`
- `Procfile`, `railway.toml`
- `Engine/pyproject.toml`, `requirements.txt`, `runtime.txt`
- `Tools/scripts/**` (bootstrap, deployment, environment scripts)
- `Docs/deployment/**`

**Deployment-doc R2 promotion clause:** Edits to `Docs/deployment/**` that touch retention, deletion, privacy, or security procedures promote to R2 (errors carry customer-facing implications via the 30-day Tier 2 retention obligation and reading-persistence guarantees). Other deployment-doc edits (build scripts, environment notes) remain R1. Authors who are unsure should default to R2.

Path-trigger rule overrides Claude's risk label; cannot be argued away.

---

## §3 — Process tiers

### T1 — Brief pack (R≥1)

For R1+ PRs, brief includes named sections:

- **Claims** — what closes
- **Non-goals** — what's deliberately out of scope
- **Deferrals** — what stays open after merge, routed where
- **Threat model** — adversary + objective
- **Expected touched files** — pre-flight prediction
- **Failure modes** — what happens when components fail
- **Tests** — labeled behavioral vs source-inspection
- **External commands already verified** — every CLI flag, env
  var, library API, or HTTP API named in the brief must be
  verified before the brief ships. The P2D access-log incident
  cost ~45min of production downtime because the orchestrator
  wrote `--access-log false` from training-data memory rather
  than running `uvicorn --help`. Required verification commands
  by interface type:

    - **CLI flag**: `<command> --help | grep <flag>` — confirms
      exact spelling and whether the flag takes a value or is a
      boolean toggle
    - **Env var**: `printenv | grep <PREFIX>` on the target
      runtime context (some env vars are only visible inside the
      container, not via `railway run` — verify in the right
      context)
    - **Library API**: import the library at orchestrator's REPL,
      confirm the function signature
    - **HTTP API shape**: pull a real response from the live
      endpoint (or staging) and read the JSON; do not paraphrase
      from memory

    The cost of a 30-second `--help` check is always less than
    the cost of a failed deploy.
- **Public-copy implications** — does this require updates to privacy.html, terms.html, marketing copy?
- **What remains false after merge?** — explicit deferral honesty

R0 escalated by path-trigger: brief pack still required.

### T2 — Codex round 0 (R≥2)

Codex reads the brief BEFORE Claude Code touches code. Output:
- Risk label confirmation (or veto + suggested label)
- Missing surfaces
- Dangerous assumptions
- Required tests (with bias toward behavioral over source-inspect)
- Deferral honesty check
- Alternate architecture if approach has issues
- Claim sweep: are "closure" claims overreaching given the deferrals?

### T3 — Claude Code execution

Implements only the accepted brief. Drift-detection duties:
- Self-contradicting brief → flag and pause
- Brief requires choosing semantics not specified → stop and ask, do not silently choose
- Brief references "per orchestrator's prescription" without inlined text → flag and pause (§9 below)
- Brief includes external command not in T1 verification list → flag and verify before implementing

### T4 — Codex post-impl audit + property verification (R≥1)

Standard adversarial audit + executable property checks where claims are runnable.

Property check format:
- One-sentence property
- Concrete expected invariant
- How to produce the artifact
- Commands to run
- Known fixtures
- What counts as failure

Test policy: source-inspection assertions are allowed but NOT the sole verification for a property. If claim is "X file is encrypted at rest," the test should actually open the file and check; not just assert path appears in `encrypt_targets`.

### Compression: T4 + T5 + T6 in one round (R≥2)

For R2+ PRs, T4 + T5 + T6 can be combined into a single Codex prompt covering audit, property checks, classification veto, and trigger phrase challenge. Compression has safety constraints — three paths:

- **Safe path (no findings):** Codex's audit produces no new findings. T5 trivially has nothing to classify; T6 trigger challenge runs against Claude's standing claims. Compression saves a round.
- **Pre-classified path:** Claude includes proposed classifications for likely-findings in the prompt ("if you find X, my classification is Y"). Codex can veto-or-confirm in the same round.
- **Discovery path (compression STOPS):** Codex finds something not pre-classified during compressed T4. Compression halts at T4. Claude must classify the new finding, then Codex re-engages for T5 veto. Do NOT let Codex auto-classify Claude's finding — that re-introduces author-judge collapse in the opposite direction.

Default for now: try compression with proposed classifications for any findings Claude can predict; fall back to separate rounds when Codex surfaces an unanticipated class of finding.

### T5 — Classification with Codex veto (R≥1)

Claude proposes classification of T4 findings (in-scope / defer / escalate) with one-sentence rationale per finding.

Codex has explicit veto on these classification claims:

- "safe to defer"
- "closure complete"
- "out of scope"
- "customer-facing privacy copy accurate" / "public/legal copy accurate"
- "bright line final" (any equivalent stop-iteration claim)
- "risk label is correct"
- "tests are sufficient"
- "property is verified"
- "architecturally new vs same class" (either direction)
- "direct edit exception valid"
- "brief scope adequate"
- "deploy/runtime assumption verified"
- "migration/backward-compatibility risk is acceptable"

**Veto procedure:** Codex writes `VETO: <reason>` in standard audit output. Veto auto-blocks merge until Muhab explicitly resolves it.

Muhab resolution options:
- Sustain veto (apply Codex's recommendation; usually escalate or fold-in)
- Override veto (Claude's classification stands; Muhab takes responsibility)
- Reroute (different classification entirely)

### T6 — Auto-trigger Codex challenge (R≥1)

Codex is invoked to challenge Claude when Claude's output contains any of these phrases:

**Bright-line walkback triggers (P2F-tested):**
- "this closes X"
- "last patch round" / "final round"
- "defer to next PR"
- "bright line"
- "direct edit exception" / "explicit override"
- "safe to merge despite residual"
- "out of scope"
- "this is the close"

**Decision-stabilization triggers (P2F-tested):**
- "ready to merge"
- "no residuals"
- "residuals should be empty"
- "defer is honest"
- "only docs" / "test-only" / "docs-only"
- "no behavior change"
- "not customer-visible"
- "same class"
- "convergent class"
- "safe because…"
- "not blocking"
- "accepted risk"
- "Muhab override" (when Claude is invoking it, not when Muhab issues it)
- "small/bounded fix"

T6 output: PASS / CONTEST. PASS = Claude's framing holds. CONTEST = Claude is using doc wording to stabilize a decision that should still be open. Muhab sees both.

This is the structural fix to "judge becoming advocate without noticing."

### T7 — Closure sweep

#### T7-light

Triggers: small doctrine-doc change that doesn't alter a claim, deferral, public copy, or "source of truth" wording.

Reads: touched doctrine doc + directly linked docs/claims.

#### T7-full

Triggers: any PR that:
- Adds, removes, or rewords a "closure" claim
- Changes deferral list
- Touches privacy.html, terms.html, or marketing copy
- Touches doctrine "source of truth" sections (registry §16.5, PRIVACY_TIERS Tier definitions, LANE_DOCTRINE structural sections)

Reads: source code (relevant subsystem) + tests + all doctrine docs + public copy + recent commit messages.

**Defaults:** R2+ PRs default to T7-full; path-triggered R0 defaults to T7-light. Either can be downgraded or upgraded with explicit rationale.

---

## §4 — Reserved configurations

### C-lite — independent migration sketches (R3 only, MANDATORY)

Sequence:
1. **Muhab writes neutral problem statement.** Just the problem, constraints, and scope boundary. No proposed approach. (If Muhab is bandwidth-constrained, Claude can draft and Muhab edits to neutrality.)
2. **Claude (chat) produces sketch A** without seeing any other sketch.
3. **Codex produces sketch B** without seeing sketch A. Same problem statement, independent design.
4. **Muhab compares A and B.** Picks one, merges, or asks for sketch C from a different angle.
5. **Claude writes brief pack** based on chosen sketch.
6. **T2 forward** as normal.

Without step 1's neutral problem statement, C-lite collapses into "Codex audits Claude's sketch" — which is just standard audit in disguise.

### Config D — parallel implementation

Reserved. Expensive; risks reducing independence. Only invoke when Muhab has specific reason.

---

## §5 — Bright line discipline (carried forward from v2)

A bright line is a constraint set by the orchestrator before a
risky decision (typical: "I will defer further findings to PR-N+1
rather than queue another fix here"). Bright lines must be:

1. **Stated explicitly** before the relevant decision point — not
   in retrospect.
2. **Pre-equipped with walk-back conditions.** Without conditions,
   a bright line is an arbitrary line and not a real constraint.
   Format: "If the next finding is X-class, defer; if Y-class, escalate."
3. **Walked back openly** when conditions warrant — never quietly
   moved. Quiet movement is drift; explicit movement is judgment.

P2F-PR2 round 4 is the canonical example. The line was "round 3 is
the last patch round on PR-2." When Codex round 4 surfaced FIX E,
the orchestrator walked the line back with the named justification:
"this finding is convergent on the same architectural class as
rounds 2-3 (encryption integrity end-to-end), not a new class —
closing it here is consistent, not new scope." The walk-back was
named, the new line was set ("round 5 is final, in any direction"),
and that line held.

The pathology to prevent is **infinite-fix-loop** (anti-pattern §8).
Convergence (each round narrowing toward a single architectural
property) is acceptable; divergence (each round opening a new class)
is the sign that the PR scope is wrong.

**Addendum:** the T6 trigger list above operationalizes §5 for cross-model enforcement. When Claude says "bright line," T6 fires automatically — Claude can no longer claim a bright line without Codex review of whether it's premature.

---

## §6 — Prescription completeness (carried forward from v2)

When a brief says "per orchestrator's prescription" or "orchestrator
has the exact text," the paste-block sent to the executor MUST contain
the verbatim text inline. Forcing the executor to scroll up and
reconstruct the prescription from earlier orchestrator messages is
functionally indistinguishable from telling them to derive it
themselves, which §8 (Claude Code error class #1, executor design drift) forbids.

Worked example: P2F-PR3 round 5, 2026-04-25. Orchestrator drafted the
verbatim text for two doctrine-accuracy fixes in chat, then composed
an executor instruction that referenced the text by saying
"orchestrator has the exact text" without inlining it. Executor
correctly paused and refused to derive doctrine wording independently,
citing §8 (Claude Code error class #1). Round-trip cost: one extra message exchange. Could have
been zero with prescription completeness.

Rule: every executor instruction is self-contained. The executor
should not need any context outside the instruction block to
implement. If the orchestrator catches itself writing
"per orchestrator's prescription" or similar, that's the signal to
inline the text instead.

---

## §7 — Orchestrator-direct-edit exception (carried forward from v2)

The orchestrator's default lane is read-and-brief, never write-to-repo.
There is one exception: explicit Muhab override for late-session,
bounded, doc-only changes where the round-trip cost exceeds the value
of preserving lane separation.

Worked example: P2F-PR3 round 5 commit `aaa6204`, 2026-04-25.
Orchestrator applied two doctrine-accuracy fixes (one bullet
addition + one comment swap) directly via Desktop Commander
git/python heredoc edits after Muhab issued "do it yourself now"
instruction. Conditions met:

- Explicit Muhab override (not orchestrator self-authorization)
- Bounded scope (two doc edits, no code-behavior change, +6/-1 lines)
- Late-session expediency (Muhab racing to field; the round-trip
  cost would have exceeded the value of maintaining lane purity)
- All other gates honored: pytest 213/213, 3 mandatory verification
  checks, CI green. The direct-edit was applied as round 5 of PR-3.
  Codex round 4 (auditing the post-edit branch) returned PASS on
  the four PR-3-internal claims and surfaced one new residual
  (privacy.html customer-copy overclaim) which was routed to PR-4
  per the round-3 bright line, not folded back into PR-3. The
  direct-edit and the residual are independent: the edit closed
  PR-3's internal doctrine, the residual closed customer-facing
  doctrine, and both gates held.

Rule: this exception is for Muhab to invoke, not for the orchestrator
to claim. Orchestrator should always offer to draft the executor
instruction first; only when Muhab explicitly says "do it yourself"
does the exception apply. Default remains read-and-brief.

**Worked example addendum, 2026-04-25 (PR-4 round 1):** orchestrator
caught itself about to direct-edit a §7-class fix to this very
document without explicit Muhab override. Reverted before any
commit, routed the fix through the executor (this paste). The
near-violation reinforces §7's narrow scope: "explicit Muhab
override" means a paste like "do it yourself now," not orchestrator
inferring expediency from session context. When in doubt, route.

---

## §8 — Anti-patterns (combined from v2 §3 + design exercise additions)

### Claude (chat) error classes

1. Writes specs from memory rather than verification (P2D access-log incident)
2. Overclaims closure (PR-3 registry headline pre-correction)
3. Sets bright lines too early, then walks back (PR-2 round 4 walkback; PR-3 round 5 walkback)
4. Same-model review misses what cross-model catches (PR-1 round 1 token JSON; this lane design exercise round 1)
5. Moves from judge to advocate without noticing — drifts from impartial classifier to defender of own brief
6. Compresses history into clean narratives — session summaries lose nuance
7. Uses doc wording to stabilize decisions that should still be questioned — registry "closure" claims solidify scope choices
8. Wants direct edit power when tired/pressed (PR-3 round 5)

### Claude Code error classes

1. Implements plausible deviations from brief intent (PR-2 FIX C soft-fail wrapper)
2. Adds soft-fail when strict-fail was specified
3. Fixes happy path while leaving exceptional path (PR-3 _reading.md cleanup pre-finally)
4. Misses target completeness (PR-2 _merged.html omission)
5. Writes source-inspect tests when behavioral tests were warranted
6. Preserves stale comments around changed behavior (PR-3 server.py:869 comment)

### Codex error classes (self-disclosed during this design exercise)

1. Overfits prompt checklist; misses adjacent surfaces not in the prompt
2. Late-stage wording churn (P2F-PR3 → PR-4 round 2-3 progression)
3. Too literal about line-level contradictions; can lose forest for trees
4. Accepts provided scope instead of challenging it (corrected via T2 brief review)
5. Source-inspect / grep-heavy rather than running executable property tests
6. Originally only audited finished work, not briefs (corrected via T2)

Lane design defends against all three classes:
- T6 auto-trigger defends Claude's drift-to-advocate (#5, #7)
- T3 explicit drift-detection defends Claude Code's silent deviations (#1)
- T4 prefers behavioral tests defends Codex's grep-tunnel-vision (#5)

---

## §9 — Working pattern (carried forward from v2)

The arc that has worked: brief → executor implements → executor
runs local mandatory verification (3+ tests) → executor pushes →
CI green → executor pings orchestrator → orchestrator pulls diff
locally and re-reads → orchestrator drafts Codex prompt for Muhab
→ Muhab routes Codex → Codex returns findings → orchestrator
classifies (in-scope / defer / escalate) → if in-scope, executor
applies; if defer, registry update notes the residual; if escalate,
Muhab decides scope → orchestrator approves merge → executor
merges → executor watches deploy with fail-fast → executor runs
post-deploy verification suite → executor reports → orchestrator
final-checks against original brief.

The cycle time per round when everything works: ~20-30 minutes.
When something doesn't work (P2D access-log, P2F-PR2 round 3
soft-fail), expect 60-90 minutes of recovery + cleanup. Build the
cycle for the failure case, not the happy path.

**v3 update:** the "orchestrator classifies" step now runs through T5 (Codex veto) and T6 (auto-trigger challenge) before reaching Muhab for approval. Classification is no longer Claude's unilateral call.

---

## §10 — The merge gate

The squash-merge step is sacred. The orchestrator does not run
`gh pr merge` without explicit approval from Muhab. The executor
does not run `gh pr merge` without explicit approval from
orchestrator + Muhab.

Merging without explicit approval is the worst-case anti-pattern
because:

1. The post-merge state is the source of truth that production
   deploys from.
2. Reverts are possible but expensive (~7-15 min downtime in the
   P2D case, plus operational anxiety).
3. The act of merging is irreversible in the sense that the
   commit lives in main forever, even after a revert. The history
   shows the cost.

If in doubt, ask. Always.

---

## §11 — When to escalate to Muhab

- Codex finds something architecturally new (different class
  from PR's stated scope)
- Bright line walk-back would be the second walk-back in same PR
- A pre-flight verification fails (env var unset, baseline tests
  not green, etc.)
- Production deploy returns FAILED
- Any operation that requires database mutation outside the
  current PR scope
- A merge approval is requested but the diff has changed since
  the last orchestrator read
- Codex T5 veto on any classification claim (per §3 T5: "veto
  auto-blocks merge until Muhab explicitly resolves")

---

## §12 — Doctrine doc handling

Doctrine docs (paths matching `Docs/architecture/PRIVACY_TIERS.md`, `Docs/engine/SIRR_MASTER_REGISTRY.md`, `Docs/operations/LANE_DOCTRINE_v*.md`) MUST NOT be opened in editors that perform auto-format-on-save, auto-save, or any silent buffer-to-disk behavior. The structural risk is that these editors quietly mutate or truncate the file while the orchestrator is reading or drafting against it, producing a brief aligned with corrupted state rather than the committed baseline.

**Prohibited:** Xcode (treats `.md` as code, applies destructive auto-format and silent saves; documented to truncate doctrine docs by ~90% over short windows). Any IDE with `editor.formatOnSave: true` for markdown unless explicitly disabled at the file or workspace level.

**Allowed:** terminal viewers (`less`, `cat`), terminal editors with no auto-format (`vim`, `nano`), VSCode/Cursor only when ALL of `editor.formatOnSave: false` for markdown, `files.autoSave: "off"`, and any markdown-formatter extension is either disabled or scoped to exclude doctrine docs. Other IDEs are allowed only after equivalent verification that no auto-format, auto-save, or silent buffer-to-disk behavior is enabled. Plain text editors in plain-text mode (TextEdit → Format → Make Plain Text). Reading via Desktop Commander or `git show HEAD:<path>` is always safe — read-only, bypasses any editor buffer state.

**Recovery procedure when corruption is detected:**

1. STOP all work touching the affected doc.
2. Verify damage: `git status` (file marked modified), `git diff HEAD -- <path>`, `wc -l <path>` vs `git show HEAD:<path> | wc -l` (significant line-count drop indicates truncation).
3. Identify and close the editor session holding the file. `lsof <path>` shows current handles. Quit the editor entirely if uncertain which tab is the offender.
4. Restore from HEAD: `git checkout HEAD -- <path>`. Verify line count post-restore matches HEAD.
5. Confirm `git status` clean. Resume work from the restored baseline.

**Reported incident (session-recorded, no preserved tracked artifact):** 2026-04-25 PR-5 incident. Xcode held `LANE_DOCTRINE_v3.md` and `SIRR_MASTER_REGISTRY.md` in editor tabs and silently truncated v3.md from 537 lines to 53 lines over a ~30-minute window during which the orchestrator (Claude in chat) drafted PR-5's brief against the corrupted state. Two of the four "issues" identified in that draft (markdown formatting bugs at lines 104 and 113 in the dirty file) were Xcode artifacts, not real doctrine bugs in HEAD. Claude Code rejected the brief at pre-flight via the dirty-tree stop condition; orchestrator verified against HEAD via `git show HEAD:`; files restored via `git checkout HEAD --`; brief revised against the clean baseline; PR-5 re-routed. Cost: one full brief-revision cycle (~30 min) plus formatter-source investigation. Future cost prevented by this section.

*Evidentiary note: this account is reconstructed from session memory. The dirty working-tree state was discarded via `git checkout HEAD --` during recovery, and the original (corrupted-state) brief was overwritten in place by the revised brief at `SIRR_PRIVATE/Orchestration/Briefs/PR5_LINE119_CATEGORIZATION_BRIEF.md`, so neither artifact is preserved in tracked history. Future incidents of this class should preserve evidence before recovery: copy the dirty file to `SIRR_PRIVATE/Incidents/<YYYY-MM-DD>_<short-name>/` (or `git stash` if the working tree state is recoverable that way) before running `git checkout HEAD --`. This makes the next worked example independently verifiable.*

**Pre-flight check (now mandatory for any doctrine-doc PR):**

```bash
lsof Docs/operations/LANE_DOCTRINE_v*.md Docs/architecture/PRIVACY_TIERS.md Docs/engine/SIRR_MASTER_REGISTRY.md 2>/dev/null | grep -vE '^(Claude|COMMAND)'
# Expect: empty output. Any non-Claude reader (especially Xcode) is a STOP condition.
```

---

## §13 — V-6 broadening, framing-amend, and history-scope

### §13.1 — V-6 broadened pattern matrix

The narrow V-6 pattern (`[REDACTED-NAME]|YYYY-MM-DD`) used in PR #33 and PR #34 missed compact digit forms, Arabic-script names, integer-tuple DOBs, and generated-artifact files. PR #34's Codex round-1 verdict surfaced 12 public files with `DDMMYYYY`, ~18 with Arabic-script same-person residues, and 5 module `.py` files with embedded family-name constants — all past V-6.

V-6 is now defined as the union of the patterns below, run against the full repository tree (see §13.2). Each PR's V-6 must match all classes; misses on any class are closure-blocking unless the PR explicitly defers a class with a forward-reference to a later sub-PR.

```bash
# V-6 broadened — paste into PR verification scripts.
# Substitute SUBJ_LATIN, SUBJ_AR, SUBJ_FAMILY_AR, DOB_Y/M/D for the personal
# identifiers being protected. Defaults shown below are for the canonical
# customer-zero protection set; expand the SUBJ_* lists as new identifiers
# are added (mother's name, etc.).
#
# Implementation notes (these were violated in the v3 §13 round-1 draft):
#   - Pass `-i` for case-insensitive matching (catches [REDACTED-NAME], [REDACTED-NAME]).
#   - Use POSIX `[[:space:]]` for whitespace. `\s` is Perl/PCRE; BSD grep
#     (macOS default) does NOT recognize it as whitespace.
#   - Pass `-i` to `git log --grep` as well; default is case-sensitive.

SUBJ_LATIN_RE='muhab[[:space:]._-]?akif|akif[[:space:]._-]?muhab'
SUBJ_USER_RE='/Users/muhab(/|$)|~muhab(/|$)'
SUBJ_AR_RE='مهاب|عاكف|[REDACTED-FAMILY-AR]'

DOB_Y=YYYY; DOB_M=M; DOB_D=D
DOB_Y2=$(printf "%04d" $DOB_Y); DOB_M2=$(printf "%02d" $DOB_M); DOB_D2=$(printf "%02d" $DOB_D)

# Compact (no separator) forms — all three orderings
DOB_DDMMYYYY="${DOB_D2}${DOB_M2}${DOB_Y2}"     # DDMMYYYY
DOB_YYYYMMDD="${DOB_Y2}${DOB_M2}${DOB_D2}"     # YYYYMMDD
DOB_MMDDYYYY="${DOB_M2}${DOB_D2}${DOB_Y2}"     # MMDDYYYY

# Year-leading separated forms
DOB_HYPH_Y="${DOB_Y2}-${DOB_M2}-${DOB_D2}"     # YYYY-MM-DD
DOB_DOT_Y="${DOB_Y2}\.${DOB_M2}\.${DOB_D2}"    # YYYY.MM.DD
DOB_SLASH_Y="${DOB_Y2}/${DOB_M2}/${DOB_D2}"    # YYYY/MM/DD

# Day-leading separated forms (locale-common in EU/MENA)
DOB_HYPH_D="${DOB_D2}-${DOB_M2}-${DOB_Y2}"     # DD-MM-YYYY
DOB_DOT_D="${DOB_D2}\.${DOB_M2}\.${DOB_Y2}"    # DD.MM.YYYY
DOB_SLASH_D="${DOB_D2}/${DOB_M2}/${DOB_Y2}"    # DD/MM/YYYY

# Named-month variants (sep, sept, september — case-insensitive via -i flag)
DOB_NAMED="${DOB_D2}[[:space:]_-]?(sep|sept|september)[[:space:]_-]?${DOB_Y2}"

# Integer-tuple form
DOB_TUPLE="\b${DOB_Y},[[:space:]]*${DOB_M},[[:space:]]*${DOB_D}\b"

DOB_RE="${DOB_DDMMYYYY}|${DOB_YYYYMMDD}|${DOB_MMDDYYYY}|${DOB_HYPH_Y}|${DOB_DOT_Y}|${DOB_SLASH_Y}|${DOB_HYPH_D}|${DOB_DOT_D}|${DOB_SLASH_D}|${DOB_NAMED}|${DOB_TUPLE}"

# Paths excluded from closure-blocking V-6 hits — see "Exclusions" below.
EXCLUDE_PATHS='Docs/operations/LANE_DOCTRINE_v.*\.md$|Docs/operations/SCRUB_V.*_BRIEF\.md$'

# Tracked files (public-repo concern); excluded paths filtered before grep.
git ls-files \
  | grep -vE "$EXCLUDE_PATHS" \
  | xargs -I{} sh -c '
      count=$(grep -icE "'"$SUBJ_LATIN_RE|$SUBJ_USER_RE|$SUBJ_AR_RE|$DOB_RE"'" "$1" 2>/dev/null)
      if [ "$count" -gt "0" ]; then echo "$count $1"; fi
    ' _ {} 2>/dev/null | sort -rn

# Commit messages on the working branch and main
git log --all -i --grep="$SUBJ_LATIN_RE" -E --oneline
git log --all -i --grep="$DOB_HYPH_Y|$DOB_DDMMYYYY" -E --oneline
```

The DOB matrix above must be regenerated (not hardcoded) whenever the protected DOB changes. Same applies to subject names; do not hardcode them as literals in the doctrine doc — leave them as variables. The literal pattern values shown above (`DDMMYYYY`, `YYYY-MM-DD`, etc.) are illustrative.

**Exclusions.** V-6 hits in the following paths are by-design didactic and do not block PR closure:

- `Docs/operations/LANE_DOCTRINE_v*.md` — this very doc; §13.3's worked example deliberately quotes the literal SCRUB-V2 PII fragment in past tense as the incident description. Per §13.4 (working-tree ≠ git-history scrub), this is an explicit doctrine choice, not a leak.
- `Docs/operations/SCRUB_V*_BRIEF.md` — orchestrator briefs may quote scrubbed-from PII strings as "old form" examples in find/replace blocks.
- Any path explicitly enumerated in a PR's brief as a forward-deferred class (e.g., V-3a forward-defers Class A and Class B residuals to V-3b; V-3b's own brief is the closure for those classes — those files are expected hits in V-3a's V-6 run, classified explicitly).

V-6 hits outside the exclusion list are closure-blocking unless the PR's brief explicitly defers the affected class to a named follow-up sub-PR. The bash block above strips the doctrine-doc and brief-doc paths via the `EXCLUDE_PATHS` filter before the `xargs`. Per-PR ad-hoc deferrals are not encoded in `EXCLUDE_PATHS`; they appear as expected hits in the V-6 output and the PR description must classify each.

### §13.2 — V-6 must grep against the full tree, not changed-files-only

PR #33 and PR #34 ran V-6 only against the changed-files diff and the planned-fix list. Both shipped because their narrow scopes did not include files where residuals lived (output_variant_synthetic_*.json, semantic_layer/scalar_field_inventory.json, expansion/chatgpt_interpretations/*.json, module .py files with embedded constants).

V-6 is now defined as full-tree by default. The bash block in §13.1 demonstrates the required pattern: `git ls-files | xargs ... grep` rather than `git diff origin/main..HEAD ... grep`.

If a PR's brief explicitly defers a residual class to a later sub-PR (as PR #34's amended description does for V-3a/b/c), V-6's full-tree run is still mandatory — the deferred classes show up as expected hits, classified explicitly in the PR description, not silently absent from the V-6 run.

### §13.3 — Framing-amend protocol when squash-merging

`gh pr merge --squash --delete-branch` defaults to using the original commit message (the message of the single commit on the PR branch), not the PR title. When a PR title is amended after the commit lands — e.g., to address a Codex framing veto — the amendment is visible on the PR display but is NOT carried into the squash commit on main.

When a framing amendment must land on main (any case where the closure-tier requires the amended language to be the audit-trail-of-record), use ONE of:

**(a) Amend the local commit + force-push the PR branch BEFORE merge:**

```bash
git commit --amend -m "<full amended message>"
git push --force-with-lease origin <branch-name>
gh pr merge <N> --squash --delete-branch
```

**(b) Override at merge time:**

```bash
gh pr merge <N> --squash --delete-branch \
  --subject "<amended title>" \
  --body-file /tmp/squash_body.md
```

Verify `gh pr merge --help | grep subject` to confirm the local `gh` version supports the flag. As of `gh 2.87.0`, both `--subject` and `--body-file` are supported.

If neither (a) nor (b) is invoked and the PR title was amended post-Codex, the unamended framing lands on main. **Force-push to a protected branch to retroactively fix the squash commit is doctrine-worse than the partial-amend outcome and is therefore prohibited as a recovery action.** Accept the partial-amend outcome and log the deviation in the merge-decision comment.

**Worked example:** SCRUB-V2 / PR #34 (2026-04-26). Codex round-1 sustained two framing vetoes (`comprehensive sweep`, `privacy closure complete`). PR title and body were amended; merge-decision comment was posted; `gh pr merge --squash --delete-branch` was invoked. The amended framing is visible on the PR display surface, but the squash commit on main retained the original commit message including the literal PII string `[REDACTED-NAME]-DD-MMM-YYYY-9376` (quoted in the Fix 1 bullet describing what was replaced). Force-push fix was rejected; the deviation was logged in the orchestrator memo and is now codified here as the prevention rule.

### §13.4 — Working-tree scrub ≠ git history scrub (explicit non-goal)

Any PR that scrubs PII from the working tree of files DOES NOT scrub PII from git history. History contains every prior version of every file. Pre-d7e0f2c commits on main retain original PII strings in their tree state, accessible via `git show <pre-d7e0f2c-commit>:<path>`. The squash commit message body of d7e0f2c itself contains literal PII strings (quoted in past-tense as "what was replaced") that are now permanently in the immutable git log on main.

History scrub is fundamentally different work:

- Tooling: BFG repo-cleaner, `git filter-repo`, or `git filter-branch` (deprecated)
- Mechanism: rewrite all commits SHA-by-SHA, replacing string occurrences in tree contents and commit messages
- Side effects: every clone of the repository must re-clone; SHA-by-SHA cross-references in PRs and issues become stale; protected-branch force-push required
- Coordination: requires admin-level git ops, all collaborators notified, all open PRs must be re-based or closed

**Relationship to P2b.** P2b (Phase 2b vault separation) chose Path C — fresh public repo migration — and executed on 2026-04-19. The legacy 2-year history was relocated to `SIRR-archive-v1` (private). The current public repo at `appleeatsapples-lang/SIRR` was born clean post-Path-C. Per `P2B_VAULT_SEPARATION_BRIEF.md` in `SIRR_PRIVATE/Orchestration/Briefs/`, P2b explicitly rejected git-history scrub as a strategy, choosing fresh-repo migration instead. Citing "P2b vault scope" as the place history-scrub work belongs is therefore wrong: P2b's defining choice was *not* to scrub history.

PII accumulating in commit messages on the post-Path-C repo (e.g., PR #34's `d7e0f2c` squash body quoting the scrubbed-from order-id fragment in past tense) is its own concern. There is currently no codified strategy for periodically scrubbing post-Path-C commit messages. If such a strategy is adopted later, it would be either (a) commit-message authoring discipline going forward (preventive), or (b) a one-time `git filter-repo` pass on the post-Path-C history (curative) — both with the side effects above.

**Operational rule until either is codified:** PR briefs and commit messages MUST NOT embed PII strings in commit messages, even in past tense as "old form" examples. Quote the working-tree change without naming the literal old-form string. The §13.3 worked example quotes the SCRUB-V2 PII fragment deliberately as didactic content; that is the only sanctioned exception, and it is covered by the §13.1 exclusion list. PRs that violate this rule (such as `d7e0f2c` itself) are accepted as historical artifacts but the operational rule applies prospectively.

Any PR brief or PR description that uses the phrase "comprehensive PII sweep," "privacy closure complete," or any equivalent must either (i) scope the claim explicitly to the working tree, or (ii) explicitly call out the history non-goal. The original SCRUB-V2 brief did neither; that is the gap §13.4 closes.

### §13.5 — R3 second-handshake firmness

R3 work (per §2 R-label definitions) requires two-handshake protocol: one explicit "go" before the SC-N read-only checks, and a second explicit "go to E-1" (or analogous destructive-op anchor) before any irreversible operation. The second handshake is the deliberate human-in-loop checkpoint that R3's risk class requires.

The second handshake CANNOT be skipped on the basis of:

- "the SC-N results obviously point to go" — Claude Code's reading of "obvious" is exactly the failure mode the second handshake exists to defend against
- "Muhab's first 'go' implicitly authorized the destructive ops" — it didn't; that's why there are two handshakes
- "the operation is well-rehearsed and the brief is detailed" — irrelevant; R3 is defined by risk class, not by orchestrator confidence

If the SC-N results raise any unexpected issue (or, in fact, if they raise no issue at all and "obviously" support proceeding), Claude Code halts and posts the SC-N report. The second handshake comes from Muhab in the chat, in plain text, naming the destructive-op anchor (e.g., "go to E-1"). Anything else is a bypass.

**Worked example:** Phase 3 filesystem reorg (2026-04-25). A Claude Code session executed E-1..E-4 (destructive `mv` and `tar` operations) without an explicit "go to E-1" from Muhab; the implicit authorization was inferred from Muhab's earlier "go to SC-1" plus the SC-1..SC-4 results returning clean. The reorg succeeded operationally, but the second-handshake bypass is a doctrine concern logged in the user's session-resume prompt. §13.5 codifies the bypass as not-allowed; future R3 work that elides the second handshake is a stop condition for the orchestrator.

*Evidence note:* the chat-handshake bypass claim is verified via the orchestrator session-resume prompt at the start of the 2026-04-26 session that wrote this section, not from git history. Git records the operational sequence of the E-1..E-4 commits but does not record whether an explicit "go to E-1" handshake preceded them in the chat surface. Future R3 incidents should leave a more durable evidence trail (e.g., a short orchestrator commit prefix or PR-comment naming the handshake before destructive ops) so this kind of after-the-fact verification doesn't depend on session memory.

### §13 closure note

§13 was added in response to the doctrine deficiencies surfaced by PR #33 → PR #34 + the Phase 3 reorg incident. All five sub-rules (§13.1-§13.5) are now mandatory; closure-sweep tier T7-full applies to any PR that touches §13 itself.

---

## Appendix A — Design exercise summary

This v3 came from a 3-round cross-model design exercise:

- v0 — Claude (chat) solo draft. Self-flagged bias: any proposal expanding "Claude in chat" should be inspected with extra skepticism.
- Codex round 1 — caught the structural critique: "Claude shouldn't decide when own judgment is contested."
- v1 — Claude integration of round 1 critique. Trigger-based auto-G + Codex classification veto.
- Codex round 2 — refinement: label naming clash, expanded triggers, expanded veto list, T7 light/full split, C-lite sequencing fix.
- v2 — Claude integration. Tier and label rename, expanded lists, compression rule.
- Codex round 3 — mechanical edits: path triggers expanded, 4 more T6 triggers, 2 more T5 vetoes, compression-rule discovery-path guard, C-lite confirmed correct.
- v3 — this doc.

Design exercise itself ran the same shape it proposes: cross-model iteration, trigger-class corrections (Codex caught my "convergent class" use during v1), explicit closure when convergence reached.

Working drafts archived at `SIRR_PRIVATE/Orchestration/LANE_DESIGN_v{0,1,2,3}.md`.

---

## Appendix B — Recommended first deployment (P2G PR-1)

Sequence:
1. **Muhab writes neutral problem statement** for P2G PR-1 (order-store row encryption opener)
2. **Claude (chat) produces sketch A** independently
3. **Codex produces sketch B** independently — without seeing sketch A
4. **Muhab compares**, picks one or merges
5. **Claude writes brief pack** (T1) based on chosen sketch
6. **Codex T2** reviews brief pack
7. **Claude Code implements** (T3)
8. **Codex T4 + T5 + T6 compressed** where feasible
9. **Closure sweep T7-full** (P2G is R3 architectural)
10. **Muhab final approval**, merge, deploy, verify

Predicted Codex round count for P2G PR-1: 4-5. Higher than typical, justified by R3 status.

---

*Doc version 3.0 — 2026-04-25 — supersedes LANE_DOCTRINE_v2.md after 3-round cross-model design exercise. Authoritative for SIRR multi-model work going forward.*
