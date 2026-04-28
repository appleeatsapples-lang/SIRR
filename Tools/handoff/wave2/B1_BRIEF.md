# Wave 2 — B1 Headline Reconciliation PR

## Frame
This PR is strictly **headline reconciliation copy** to address the trust break flagged across all four customer walks: customers cannot tell which of the multiple "headline" values (Synthesis Root, Convergence Number, Tradition-vote element, Monte Carlo evidence counts) is "theirs."

The fix is **not** to collapse to one canonical value. It is to teach the customer that three different kinds of measurement are in play — synthesis (the headline), evidence (counts of agreement), tradition voices (per-tradition outputs) — and that they're answering different questions, not competing.

**Do not** change render order. **Do not** modify engine logic. **Do not** touch numeric values in the catalog. **Do not** invent doctrine for any tradition. **Do not** rewrite the existing `Underlying Signals` evidence-intro block (lines 1485–1493) — it already does its job.

This is option (iv) — augment-not-replace. Block 1 ships as a new self-contained section above the portrait. Block 2 augments the existing `conv-intro` paragraph by appending one sentence. Block 3 (Monte Carlo transition) is dropped because the existing `conv-intro` already does that work.

## Source documents
- **Locked copy + implementation note:** `Tools/handoff/wave2/B1_HEADLINE_RECONCILIATION_DRAFT.md` (read the "LOCKED COPY (2026-04-28)" section AND the "Implementation note — option (iv) augment-not-replace" section before starting)
- **Customer-walk evidence:** `Tools/handoff/customer_walks/TRIANGULATED_FINDINGS.md`
- **Wave 2 decisions:** `Tools/handoff/customer_walks/WAVE_2_DECISIONS_LOCKED.md`

## Scope — 3 items

### 1. Add `render_reading_intro()` (Block 1)

**File:** `Engine/unified_view.py`

**New render function** placed alongside the other synthesis-layer render functions (after `render_header`, before `render_portrait` would be the natural alphabetical/order-of-call location, but anywhere in the synthesis-layer cluster is fine). Function signature mirrors the existing render functions:

```python
def render_reading_intro() -> str:
    """Page-1 framing block. Teaches the customer that they will see
    multiple kinds of measurement (synthesis / evidence / tradition voices)
    and that these are not competing answers.

    Wave 2 B1 — added to address the headline-reconciliation trust break
    flagged across all four customer walks (TRIANGULATED_FINDINGS.md).
    """
    return """
    <section class="reading-intro">
      <p>SIRR computes three different kinds of result on your name and birth date.</p>
      <p><strong>Synthesis</strong> pools eight identity axes into one organizing root &mdash; the reading's primary headline.<br>
      <strong>Evidence</strong> counts how many independent systems agree on the same value.<br>
      <strong>Tradition voices</strong> let each tradition speak in its own measurement.</p>
      <p>You'll see different numbers and elements in each section. They aren't disagreeing &mdash; they're answering different questions.</p>
    </section>
    """
```

**Insert call into `body_parts` assembly** (currently around line 1476–1483):

```python
    body_parts = [
        render_header(profile),
        render_reading_intro(),     # ← NEW
        render_portrait(output),
        render_coherence(unified),
        render_patterns(output),
        render_theses(output),
        render_tension(unified),
    ]
```

**Add CSS class `.reading-intro`** in the CSS block. Model on the existing `.evidence-intro` class (currently at lines 929–950). Differences:

- `margin` should be top-of-page appropriate (e.g. `0 0 48px` instead of the existing `96px 0 48px` which is for mid-page transition).
- `border-top` should be omitted (no upstream content to separate from).
- Font / size / color / max-width can match `.evidence-intro` for visual consistency.
- The `<strong>` labels (Synthesis / Evidence / Tradition voices) should render with appropriate weight; verify they're visible against the italic Newsreader paragraph font.

Verify line numbers before editing — main may drift:
```bash
grep -n 'class="smallcap label">Your Reading' Engine/unified_view.py    # Block 1 marker
grep -n 'render_portrait(output),' Engine/unified_view.py                # Insertion point
grep -n '\.evidence-intro {' Engine/unified_view.py                      # CSS model location
```

### 2. Augment the `conv-intro` paragraph (Block 2)

**File:** `Engine/unified_view.py`

**Current paragraph** (around lines 1437–1441):

```html
<p class="conv-intro">
  Raw counts: how many independent engines landed on the same number,
  and where that count sits against a 10,000-run random baseline.
  Evidence behind the synthesis above &mdash; not a separate reading.
</p>
```

**New paragraph** — append one sentence with the concrete example. Final form:

```html
<p class="conv-intro">
  Raw counts: how many independent engines landed on the same number,
  and where that count sits against a 10,000-run random baseline.
  Evidence behind the synthesis above &mdash; not a separate reading.
  Where you see &ldquo;12 systems converge on 1,&rdquo; that means twelve traditions returned 1 &mdash; not that your reading is 1.
</p>
```

Use HTML entities (`&ldquo;` `&rdquo;` `&mdash;`) to match existing style in this section. Do not introduce raw Unicode quote/dash characters. No CSS changes — `.conv-intro` (line 418) handles this paragraph already.

Verify line numbers before editing:
```bash
grep -n 'class="conv-intro"' Engine/unified_view.py
grep -n 'Evidence behind the synthesis above' Engine/unified_view.py
```

### 3. Add regression test guards

**File:** `Engine/tests/test_merged_view.py`

Add two new assertion-based tests guarding the new copy. Pattern to mirror: the existing `test_convergence_monte_carlo_still_rendered` regression guard at line ~104 (which asserts `"Monte Carlo Evidence" in html`).

**Test 1 — Block 1 framing presence:**

```python
def test_reading_intro_block_renders(synthetic_output):
    """B1 Wave 2 regression guard — page-1 reading intro must render
    the three-measurements framing copy."""
    from unified_view import render_unified_html
    html = render_unified_html(synthetic_output)
    assert "three different kinds of result" in html
    assert "answering different questions" in html
    assert 'class="reading-intro"' in html
```

**Test 2 — Block 2 augmentation presence:**

```python
def test_conv_intro_includes_concrete_example(synthetic_output):
    """B1 Wave 2 regression guard — convergence section intro must
    include the concrete '12 systems converge on 1' example."""
    from unified_view import render_unified_html
    html = render_unified_html(synthetic_output)
    assert "12 systems converge on 1" in html
    assert "twelve traditions returned 1" in html
```

Both tests must use `render_unified_html` (not `render_merged_html`) since merged_view inherits via import — testing the source is sufficient. Optionally add a third guard against the merged view to be safe; not required.

**Existing assertions that MUST continue passing** (preservation under option (iv)):
- Line 81: `">Convergence</h2>" in html`
- Line 109: `"Monte Carlo Evidence" in html`
- Line 182: `"Monte Carlo Evidence" in html`
- Line 229: `'class="evidence-intro"' not in top` (this is checking absence in a specific scope; verify scope hasn't shifted)
- Line 291: `"Monte Carlo Receipts" in html`
- Line 298: `"Monte Carlo Evidence" in html`
- Line 322: `'class="evidence-intro"' in html or "Underlying Signals" in html`

Option (iv) preserves all of these by construction. If any break, stop and report — something architectural shifted.

## Out of scope for this PR
- Birth time UX (Wave 2 — separate decision: hide unknown rows)
- Inline jargon parenthetical for ~75 terms (Wave 2 B2 — separate brief, blocked on findings 7-9 engineer-input)
- Splitting Convergence and Monte Carlo into two distinct rendered sections (option iii — explicitly rejected)
- Changing `.evidence-intro` Underlying Signals copy
- Server-side PDF render parity (Wave 3)
- Any change to the values shown in the synthesis portrait, convergence rows, or Monte Carlo receipts

## Acceptance check
After PR ships, the next customer walk by an independent model should:
- Read the page-1 intro and not flag "wait, why are there multiple numbers/elements?" as a trust break
- Read the convergence section and not interpret "12 systems converge on 1" as "your reading is 1"
- Continue to flag the jargon coverage gap (B2 work, expected)
- Not surface any new defects introduced by Block 1's CSS or layout

Visual check on `/view/demo` after deploy:
- Block 1 renders above the portrait with appropriate spacing — no stacked-collision with the header
- The three `<strong>` labels (Synthesis / Evidence / Tradition voices) are visually distinguishable from the surrounding italic body
- The augmented conv-intro paragraph reads as a single flowing paragraph, not as a stitched-on sentence

## Pre-flight
- Repo state: `git log -1 --oneline main` (expect `fd73bf3` or newer)
- Pytest baseline: `pytest -q` (expect 241 passing)
- Branch from main: `git checkout -b wave2-b1-headline-reconciliation`
- All changes in **two files only**: `Engine/unified_view.py` and `Engine/tests/test_merged_view.py`
- No engine logic changes. No changes outside these two files unless a CSS variable definition genuinely needs adding (verify with grep first).
- Verify line numbers with the grep commands listed in each scope item before editing — main may have drifted.

**Path correction from Wave 1 brief:** Wave 1's pre-flight said *"All changes should be in `Engine/web_backend/templates/`, `Engine/web_backend/unified_view.py`, or `Engine/web_backend/html_reading.py`"*. None of those paths exist. The actual reading render file is `Engine/unified_view.py` at the repo's Engine root. Do not create a `templates/` directory or move the file.

## Estimated effort
1.5–2.5 hours implementation + Codex audit round (~1 round, light doctrine — option (iv) is well-specified, low surprise area).

## Round shape
**R1: Codex audit** for: copy fidelity to locked source, CSS isolation (no leak into `.evidence-intro` or `.conv-intro`), test coverage of both blocks, that no existing test breaks. Doctrine backfill probably not required; this is template-clarity work, not a doctrine change.

---

## Paste-ready CC opener

```
Wave 2 — B1 Headline Reconciliation PR.

Brief location: Tools/handoff/wave2/B1_BRIEF.md
Locked copy + implementation note: Tools/handoff/wave2/B1_HEADLINE_RECONCILIATION_DRAFT.md
(Read both before starting. The implementation note section is load-bearing — it explains why this collapsed from a 3-block plan to 1+1.)

Repo state anchor:
  - HEAD: fd73bf3 on main (verify: git log -1 --oneline main)
  - pytest baseline: 241 passing (verify: pytest -q)
  - Production: HTTP 200 healthy on https://web-production-ec2871.up.railway.app/

Lane: CC (engine + Python + commits)
Rounds: R1 minimum (Codex audit on copy fidelity + CSS isolation + test coverage)
Estimated effort: 1.5–2.5h

Mandatory pre-flight before any edits:
  1. git checkout main && git pull origin main
  2. git checkout -b wave2-b1-headline-reconciliation
  3. pytest -q  (must show 241 passing)
  4. grep -n 'class="smallcap label">Your Reading' Engine/unified_view.py     # Block 1 marker
  5. grep -n 'render_portrait(output),' Engine/unified_view.py                # Insertion point
  6. grep -n 'class="conv-intro"' Engine/unified_view.py                      # Block 2 marker
  7. grep -n '\.evidence-intro {' Engine/unified_view.py                      # CSS model location

Approach summary:
  - Add new render_reading_intro() function + .reading-intro CSS class. Insert call between render_header and render_portrait in body_parts.
  - Append ONE sentence to existing conv-intro paragraph. Use HTML entities to match existing style.
  - Add 2 regression guards in Engine/tests/test_merged_view.py.
  - All edits in Engine/unified_view.py and Engine/tests/test_merged_view.py only. No engine logic changes.

Doctrine reminder: engineer-not-mystic register. The new copy is factual and calm — no "ancient wisdom," no defensive framing, no apologetic transitions. Convergence is never announced; pattern accumulates in the user, not on the page.

Verify after R1: pytest 243 passing (241 + 2 new regression guards), all existing assertions in test_merged_view.py still pass (lines 81, 109, 182, 229, 291, 298, 322).
```
