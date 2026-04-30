# §X Doctrine — Lock Record

**Version:** v0.1.1 (surgical extension of v0.1)
**Locked:** v0.1 — 2026-04-30; v0.1.1 — 2026-04-30
**Locked by:** Claude orchestrator with operator approval
**Synthesis source:** `Tools/handoff/doctrine_X_drafts/SYNTHESIS_X_DRAFT.md`
**Surgical amendments source (v0.1.1):** `Tools/handoff/doctrine_X_drafts/X_V0_1_1_SURGICAL_AMENDMENTS.md`

## Audit trail

| Stage | Date | Verdict | Notes |
|---|---|---|---|
| T1 — bundle authoring | 2026-04-30 | Operator approved | 522-line bundle, 11 sections, zero direct PII |
| T1.5 — parallel drafting | 2026-04-30 | Both drafts complete | Claude (~3,580 words, prose-led) + ChatGPT (~4,200 words, table-led); NotebookLM declined drafting role, repurposed to verifier |
| T1.7 — synthesis | 2026-04-30 | 5 operator-approved positions | Recursion top-level; convergence demoted; affirmative claim kept; vocab strict; prose-led with tables for §X.4/§X.5/§X.8 |
| T1.8 — NotebookLM grounding | 2026-04-30 | 8 STRONG / 3 ADEQUATE / 0 WEAK / 0 contradictions | All "novel" items classified as operational implementation of bundle intent |
| T2 R1 — Codex audit | 2026-04-30 | PASS-WITH-FOLLOWUPS | 4 findings: §X.1 prestige leak, §X.7 self-report dependency, §X.8 visual coverage gap, §X.10 anomaly-deferral readability |
| T1.9 — amend in synthesis | 2026-04-30 | Self-audit clean | All 4 findings amended single-round; +750 words; cross-references intact |
| T2 R2 — Codex re-audit | 2026-04-30 | **PASS** | All 4 amendments PASS; no new findings; routing recommendation: lock as v0.1 and proceed to T3 |
| v0.1.1 — specialist pre-pass | 2026-04-30 | 36 findings classified | 3 synthetic specialists (religious-ethics, consumer-protection, cognitive-bias); 26 blocking-pre-launch |
| v0.1.1 — specialist triage | 2026-04-30 | Operator selected option C (split) | 4 §X-internal blockers patched here; 12 → §X-Trad; 11 → §X-Legal; 7 → §X v0.2; 2 → engineering/business |
| v0.1.1 — orchestrator surgical draft | 2026-04-30 | 4 amendments drafted | Spec 3 F1 (Barnum) + Spec 3 F4 (closure) + Spec 3 F5 (claim-of-insight) + Spec 2 F1 (legal-disclosure pointer) |
| v0.1.1 — ChatGPT counter-critique | 2026-04-30 | 4 revisions integrated | A1 Barnum auditable-form swap; A2 closure load-bearing home moved §X.6 → §X.8 with §X.6 cross-reference; A3 claim-of-insight synonym additions; A4 §X.10 launch-gate cleanup + §X.11 consistency alignment |
| v0.1.1 — Codex T2 R1 audit | 2026-04-30 | PASS-WITH-FOLLOWUPS | 1 follow-up: §X.8 #17 rendered-surface evidence requirement |
| v0.1.1 — follow-up integration | 2026-04-30 | Integrated into Amendment 2 | Evidence-requirement clause added to §X.8 #17 proposed text; §X.6 #9 cross-reference unchanged (inherits transitively); no Codex re-audit per Codex routing recommendation |
| v0.1.1 — operator approval | 2026-04-30 | Approved | Lock patch authorized after dry-run review |
| v0.1.1 — lock patch applied | 2026-04-30 | **LOCKED** | `SYNTHESIS_X_DRAFT.md` patched (8 edits); this record updated |

## What v0.1 contains

11 numbered rules (§X.1 - §X.11):
- §X.1 — what SIRR claims (affirmative, with reservation tied to §X.5)
- §X.2 — what SIRR denies (5 explicit denials in customer-readable language)
- §X.3 — six operators + architectural rule (no operator hard-coded as headline)
- §X.4 — convergence claim constraints (S3-grounded)
- §X.5 — three-bucket tradition / CMMA / synthesis distinction + scholarship fidelity
- §X.6 — generated prose rules + strict vocabulary translation
- §X.7 — recursion hedge (counterfactual + external decision artifact)
- §X.8 — claims ledger (extended for visual / structural claims; 16 violations enumerated)
- §X.9 — counts come from current build
- §X.10 — deferrals (with hard gate on anomaly), monitoring cadence, amendment process
- §X.11 — doctrine version, ownership, dependencies

## What v0.1.1 contains

Surgical extension of v0.1; v0.1's 11 numbered rules preserved unchanged. Four amendments + one post-Codex follow-up:

- **Amendment 1 (Spec 3 F1, Barnum):** §X.6 Hard rule #8 — generated prose may not produce sentences that feel specific to the customer but apply to most people. Auditable form: specificity must derive from computed marks, methods, inputs, or structural features of the reading.
- **Amendment 2 (Spec 3 F4, report-level closure prevention):** §X.8 violation #17 (load-bearing) + §X.6 Hard rule #9 (cross-reference). Forbids reading-as-a-whole closure surfaces (prose, template, visual hierarchy, share asset) that integrate the six operators into a single verdict about the customer. Position-independent.
- **Post-Codex T2 R1 follow-up (integrated into Amendment 2):** §X.8 #17 Evidence-requirement clause — claims ledger entries for surface changes must include rendered-surface evidence (HTML, screenshot, fixture, share asset, PDF/export); code/templates alone are not sufficient. §X.6 #9 cross-reference unchanged (inherits transitively).
- **Amendment 3 (Spec 3 F5, claim-of-insight):** §X.1 forbidden grammar item 7 + audit test second sentence. Forbids framing SIRR or the reading as deliverer of self-knowledge / self-discovery / hidden truths / insight into the customer. Covers verbs (discover, reveal, show, uncover, expose, illuminate) and noun-phrase evasions (personal truth, inner truth, true self, who you really are).
- **Amendment 4 (Spec 2 F1, legal-disclosure pointer):** §X.10 new "Live-paid-checkout launch gate" subsection + §X.11 Adjacent-doctrines line extended. §X self-restraint: §X-governed surfaces may not activate in live paid checkout or paid post-payment delivery until §X-Legal exists in approved form. Static informational, sample readings, and test-mode flows may proceed under §X audit alone.

Routing record (36/36 findings accounted for): 4 patched in v0.1.1; 12 → §X-Trad; 11 → §X-Legal; 7 → §X v0.2; 2 → engineering/business/post-launch.

## Next pipeline stage: T3

CC implements §X as a repo doctrine document. Most likely path: new file `Docs/operations/CLAIMS_DOCTRINE_X.md` referenced from `LANE_DOCTRINE_v3.md`. Standard doctrine PR pipeline T3 → T5 → T6 → T7-light → merge.

## Artifacts on disk (full audit trail preserved)

- `SIRR_DOCTRINE_X_CONTEXT_BUNDLE.md` — evidence base (T1)
- `DRAFT_CLAUDE.md` + `DRAFTER_NOTES_CLAUDE.md` — Claude's parallel draft
- `DRAFT_CHATGPT.md` + `DRAFTER_NOTES_CHATGPT.md` — ChatGPT's parallel draft
- `SYNTHESIS_X_DRAFT.md` — locked v0.1
- `SYNTHESIS_NOTES.md` — synthesis decisions explained
- `NOTEBOOKLM_GROUNDING_PROMPT_SHORT.md` + `NOTEBOOKLM_VERIFICATION_REPORT.md` — grounding pass
- `CODEX_T2_OPENER.md` — R1 audit opener
- `CODEX_T2_R2_OPENER.md` — R2 audit opener (post-amendment)
- `LOCK_RECORD.md` — this file
