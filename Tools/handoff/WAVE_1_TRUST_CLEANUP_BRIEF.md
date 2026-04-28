# Wave 1 — Customer Trust Cleanup PR

## Frame
This PR is strictly **template clarity, label honesty, null suppression, and visible trust cleanup**. It is the first deliverable in response to the customer-walk triangulation (`Tools/handoff/customer_walks/TRIANGULATED_FINDINGS.md`).

**Do not** touch the engine. **Do not** resolve the number/element headline reconciliation. **Do not** invent explanatory doctrine for traditions. **Do not** decide birth-time UX. Those are Wave 2 (`Tools/handoff/customer_walks/WAVE_2_DECISIONS_LOCKED.md`).

This PR fixes things every customer-walk participant noticed but is NOT a content rewrite.

## Scope — 11 items

### Label / structure fixes
1. **Relabel duplicate `BIRTH CARD`** in Name Intelligence cards section. Change to `TAROT BIRTH CARD` and `CARTOMANCY BIRTH CARD` (or equivalent that differentiates the decks).
2. **Replace section header `HOW EACH TRADITION READS THIS`** with `SIGNALS BEHIND THIS SECTION`. The term "tradition" is inaccurate — many rows are computed metrics, modern constructs, or composites. Apply everywhere this label appears.
3. **Reconcile Birthday rendering**. Numerology grid shows `5 · BIRTHDAY · The Liberator`. Adjacent row shows `Life Purpose / Birth Day Number 23`. Same concept, two values. Pick one of:
   - Drop the `Life Purpose / Birth Day Number 23` row
   - OR label one as `Birthday (reduced)` and the other as `Birthday (raw)`
   - Whichever is lower-touch in the template.

### Copy fixes
4. **Master number 22 explainer**. On the `22 · PERSONALITY · The Master Builder` card, add a tiny inline note: `(master number — kept unreduced)` or similar. ~6 words. No tradition justification — just signal intent.
5. **Remove or reframe `These patterns do not conflict`**. The current line reads as defensive (refuting an unstated objection). Either delete it OR rewrite to be additive (e.g. `Together, these patterns describe two axes of the same picture.`). If unsure, delete.
6. **Reframe `No dominant archetype`**. Currently reads as system failure. Change to `Multi-axis archetypal pattern` or `No single archetype dominates — your reading distributes across several.` Same data, framed as a finding.
7. **Deduplicate threshold-birth sentence**. The sentence "Strong sensitivity to transitions and liminal periods — identity formation tied to threshold moments" appears verbatim on page 1 (intro paragraph) and page 2 (Threshold Birth pattern card). Keep one. Suggested: keep on page 2 where it's a labeled pattern; drop from page 1 paragraph (rewrite to lead with a different sentence).
8. **Light rename of hidden-signal teaser labels**. Current: `SHOW ALL 26 SIGNALS · +20 MORE`. Change to: `View 20 additional signals` or `Expand full detail (+20 signals)`. Reduces "I got a teaser" feeling. Apply to all four occurrences (26, 49, 22, 11 signal blocks).

### Spacing/rendering defects
9. **Spacing bugs**. Fix the following text-rendering defects (likely whitespace handling in template):
   - `language,relational synthesis,expressive processing` → add spaces after commas
   - `You wantchange` → `You want change`
   - `NameIntelligence` → `Name Intelligence`
   Search for similar defects nearby; fix any found.
10. **Null/unknown suppression**. Hide rows where the value is `unknown`, blank, or contains an empty glyph placeholder. Specifically:
    - `BaZi Four Pillars Guǐ ( ) Yin Water` → render as `Guǐ Yin Water` (drop empty parens). If the empty parens come from a missing Chinese-character substitution, do NOT chase the font issue in this PR — just suppress the empty parens for now.
    - `BaZi element (Chinese)` row with no value → hide entirely
    - `Current luck pillar unknown` row → hide entirely
    - Audit nearby rows for similar patterns; hide them.

### Closing
11. **Add closing block** at the end of the reading. Exact copy:
    > **Your reading is complete.**
    > Save this private link — you can return to it anytime.

    Single block, two lines. Do NOT add email promises, retention guarantees, or "computed fresh each time" language. Do NOT add a "share this" CTA in this PR. Closing block ends the reading cleanly without making policy commitments.

## Out of scope for this PR (Wave 2 or later)
- Element reconciliation note (Water/Air/Earth) — Wave 2 architecture
- Number reconciliation (3/1/2/4/6/51) — Wave 2 architecture
- Inline jargon parenthetical for ~40 terms — Wave 2 content pass
- Birth time collection UX — Wave 2 (decision: defer)
- Counting-unit standardization across codebase — defer unless trivially centralized
- Server-side PDF rendering — Wave 3
- Cognitive hierarchy redesign — Wave 3

## Acceptance check
After PR ships, the next customer walk by an independent model should:
- Not flag duplicate BIRTH CARD labels
- Not flag empty parens or "unknown" rows
- Not flag the spacing defects
- Not flag the master number 22 confusion
- Not flag the duplicated threshold sentence
- Not flag "no dominant archetype" as a failure
- Land on a closing line, not on a Monte Carlo receipt mid-page
- Still flag the element/number disagreement (Wave 2) and the jargon (Wave 2) — these remain by design until Wave 2 ships

## Pre-flight
- Check repo state: `git log -1 --oneline main` (expect 18945c9 or newer)
- Run `pytest -q` baseline (expect 240 passing)
- Branch from main: `git checkout -b wave1-trust-cleanup`
- All changes should be in `Engine/web_backend/templates/`, `Engine/web_backend/unified_view.py`, or `Engine/web_backend/html_reading.py` (whichever owns the affected sections). No engine logic changes.

## Estimated effort
2-3 hours implementation + Codex audit round (~1 round, no doctrine to backfill).
