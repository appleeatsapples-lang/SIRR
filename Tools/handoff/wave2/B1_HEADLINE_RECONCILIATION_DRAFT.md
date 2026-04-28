# B1 — Headline Reconciliation Copy Drafting
Wave 2 work item. Decisions locked in `WAVE_2_DECISIONS_LOCKED.md`. Strawman + structured prompt below.

## LOCKED COPY (2026-04-28)

**Provenance:** hybrid — Draft A's structure for page 1 intro + (Draft A's opener + Draft B's "12 systems converge on 1" example) for convergence + Draft A tightened for Monte Carlo. Total new copy ≈110 words, under the 200-word budget.

**The strawman drafts A/B/C and structured prompt below are preserved as the evidence chain. Do not edit them.**

### Block 1 — Page 1 intro (NEW; placed before the "YOUR READING" band)

> SIRR computes three different kinds of result on your name and birth date.
>
> **Synthesis** pools eight identity axes into one organizing root — the reading's primary headline.
> **Evidence** counts how many independent systems agree on the same value.
> **Tradition voices** let each tradition speak in its own measurement.
>
> You'll see different numbers and elements in each section. They aren't disagreeing — they're answering different questions.

### Block 2 — Convergence section transition (NEW; placed at top of Convergence section, before existing content)

> *Evidence count, not a competing answer.* Where you see "12 systems converge on 1," that means twelve traditions returned 1 — not that your reading is 1.

### Block 3 — Monte Carlo section transition (NEW; placed at top of Monte Carlo section)

> *Receipts for the convergence above.* These rows show raw agreement counts against a 10,000-run random baseline. The numbers 2, 4, 6 aren't "your numbers" — they're the values systems clustered on.

---

## Implementation note — option (iv) augment-not-replace (2026-04-28)

The locked copy above was specced before the actual `unified_view.py` render pipeline was inspected. Scoping pass surfaced three architectural facts that collapse the 3-block plan to 1+1:

1. **The synthesis-first / evidence-second doctrine is already implemented.** The render pipeline (locked spec 61428, 2026-04-17) has an `Underlying Signals` evidence-intro block at `unified_view.py` lines 1485–1493 that already frames the catalog as supporting evidence, not as a competing reading. Block 1's framing slots above this without conflict.
2. **The existing `conv-intro` paragraph (lines 1437–1441) already does ~90% of Block 3.** Current copy: *"Raw counts: how many independent engines landed on the same number, and where that count sits against a 10,000-run random baseline. Evidence behind the synthesis above — not a separate reading."* Calmer than the original Block 3 draft and says the same thing.
3. **Convergence and Monte Carlo are ONE combined section, not two.** Single smallcap label at line 1435: `Numeric Convergence · Monte Carlo Evidence`. There is no separate Monte Carlo section to receive a transition.

### Resolution: option (iv) — augment, don't replace

**Block 1 — ships as written.** New `render_reading_intro()` function inserted in `body_parts` between `render_header` and `render_portrait`. Self-contained section. New CSS class `.reading-intro` modeled on `.evidence-intro`.

**Block 2 — augments existing conv-intro by appending one sentence.** The existing two sentences stay. The "12 systems converge on 1" example sentence from the locked copy is appended as the third sentence. Final form of the conv-intro paragraph (lines 1437–1441 region):

> Raw counts: how many independent engines landed on the same number, and where that count sits against a 10,000-run random baseline. Evidence behind the synthesis above — not a separate reading. Where you see "12 systems converge on 1," that means twelve traditions returned 1 — not that your reading is 1.

**Block 3 — dropped.** The existing "Evidence behind the synthesis above — not a separate reading" sentence already does the work. Adding a separate Monte Carlo transition would be redundant within the same section.

### Why locked copy is preserved as written

The locked copy section above stays unedited as the *decision artifact* — same doctrine as the A/B/C strawman drafts below. Future readers see the spec that was approved AND the implementation translation that ships, not just the post-translation result. If a future architectural change re-separates Convergence from Monte Carlo, the original Block 3 copy is still on file ready to ship.

---

## The problem (recap)
The reading currently shows the customer multiple "headline" values that look like competing answers:
- Page 1: `Root 3 · Element Water` (the synthesis)
- Page 5: `NUMBER 1 · ELEMENT Air` (the convergence)
- Page 6: `Tradition-vote element: Earth`
- Page 7: `2/4/6 across 7 families` (Monte Carlo evidence)
- Page 7 footer: `Coherence 51 · Divergent`

All four customer walks flagged this as the single biggest trust break. Customer cannot tell which value is "theirs."

## The decision (locked)
We do NOT collapse to one canonical value. We keep all values and **separate them by what kind of measurement each one is**:

- **Synthesis Root** = portrait summary (the reading's primary headline)
- **Convergence** = evidence count (how many independent systems agree on a number)
- **Tradition-vote element** = one evidence lane, not a competing answer
- **Coherence score** = meta-statistic about the convergence pattern itself

Customer leaves with: "Synthesis 3 is my reading; convergence 1 is the strongest agreement count; everything else is evidence." Three different kinds of result, not three competing answers.

## The work
Write the customer-facing copy that delivers this distinction. Three places need new copy:

1. **Top of page 1** — a "how to read this reading" intro paragraph that frames the three measurement types BEFORE the customer sees any numbers.
2. **Top of Convergence section** — a brief reframe sentence that says "this is evidence count, not a competing answer."
3. **Top of Monte Carlo section** — a brief reframe that says "these numbers are agreement counts across systems, not a value the reading is calling 'yours.'"

Optional fourth: a small note next to the page 1 `Element Water` line that points the customer at the convergence section ("synthesis-level value; you'll see how each tradition votes below").

---

## STRAWMAN — three drafts to react to

You can pick one, mash them together, or write your own. The goal is the structured prompt below; these are starting points to push against.

### Draft A — Spare and clinical

#### Page 1 intro (NEW — before "YOUR READING" band)
> SIRR computes three different kinds of result on your name and birth date.
>
> **Synthesis** — pools eight identity axes into one organizing root. This is the reading's primary headline.
> **Evidence** — counts how many independent systems agree on the same value.
> **Tradition voices** — lets each tradition speak in its own measurement.
>
> You'll see different numbers and elements in each section. They aren't disagreeing. They're answering different questions.

#### Top of Convergence section (NEW)
> *Evidence count, not a competing answer.* The numbers below show how many independent systems landed on the same value. They tell you where agreement clusters — not which number is "yours."

#### Top of Monte Carlo section (NEW)
> *Receipts for the convergence above.* These rows show the raw agreement counts measured against a 10,000-run random baseline. The numbers 2, 4, 6 are not "your numbers" — they are the values systems most often clustered on.

---

### Draft B — Warmer, more invitation than instruction

#### Page 1 intro (NEW)
> Three things will be different about this reading.
>
> First, you'll see more than one number. Your synthesis is one value; the count of how many systems agree on a value is another; what individual traditions say is a third. None of them is wrong; they answer different questions.
>
> Second, terms will appear that aren't familiar. We define each one the first time it shows up.
>
> Third, the synthesis at the top is the reading's organizing axis. Everything else is the evidence behind it.

#### Top of Convergence section
> *This is the evidence behind your synthesis.* Below: how many independent systems land on the same number. Where you see "12 systems converge on 1," that means twelve different traditions all returned 1 — not that your reading is "1."

#### Top of Monte Carlo section
> *The math behind the math.* Each row counts the systems that landed on a value, compared against a 10,000-run random baseline. This is what makes the convergence above more than a coincidence — and it's why we run the random baseline in the first place.

---

### Draft C — Minimal — only what's strictly necessary

#### Page 1 — small note added under the existing band
Just add one line under the existing `Root 3 · Expression & Synthesis · Element Water`:
> *Synthesis-level value. The convergence section below shows how each tradition votes; values may differ.*

#### Top of Convergence section — single sentence
> *Evidence counts; not "your number."*

#### Top of Monte Carlo section — single sentence
> *Random-baseline comparison for the counts above.*

This is the cheapest fix and stays out of the customer's way. Highest risk: customer still gets confused because the framing doesn't have enough room to teach.

---

## STRUCTURED PROMPT — your version

If none of A/B/C land, write your own. The constraints:

**Must convey** (in any wording):
1. Three different kinds of measurement are at play. They are not competing answers.
2. Synthesis is the primary headline. Customer's "reading" is the synthesis value.
3. Convergence counts agreement across systems. Numbers there are NOT the customer's number.
4. Monte Carlo shows the math behind convergence. Numbers there are NOT the customer's number.

**Must NOT do**:
1. Take a doctrine position on which tradition's element is "right." (Water, Air, and Earth all need to coexist as evidence-lane outputs without ranking.)
2. Apologize for the contradiction. (Defensive framing is what the walks flagged in "These patterns do not conflict.")
3. Use mystic-marketing voice. (Engineer-not-mystic register: factual, calm, no "ancient wisdom.")
4. Promise a specific interpretation outcome. (Customer should leave with curiosity, not a commitment.)

**Voice anchor — what SIRR sounds like**:
- Closer to Stripe's documentation voice than to a horoscope app
- Confident in the engineering, modest about the interpretation
- "Here's what we measured" not "here's who you are"
- Reads like the engineer wrote it, not like marketing wrote it

**Length budget**:
- Page 1 intro: 60-100 words feels right (long enough to teach, short enough not to delay the reading)
- Section transitions: 15-30 words each (a sentence or two, not a paragraph)
- Total new copy across all three: under 200 words

**Test for done**:
A reader who hasn't seen SIRR before should finish the page 1 intro and ALREADY KNOW that they're about to see multiple numbers/elements that aren't competing. The trust break the walks identified should be pre-empted, not papered over.

---

## My pick + reasoning

If forced to pick one of A/B/C without your input:
- **A** if your launch register is "we are precise instruments"
- **B** if your launch register is "we are precise but warm guides"
- **C** only if you want the cheapest possible Wave 2 fix and accept that some customers will still get confused

The walks suggest **B is closest to right**, because:
- Customers who paid $49 want to feel addressed, not lectured
- "First, second, third" structure mirrors how readers absorb new conceptual frames
- The "we define each one the first time it shows up" line in B prefigures the jargon work
- The customer-facing voice still preserves engineer-not-mystic discipline

But B is also the longest. If reading length is a concern, A is fine.

I would NOT ship C. It's structurally insufficient.

---

## What I'd review before locking

- Read each draft top-to-bottom as the customer (same persona as the walks: never seen SIRR, paid $49, slight skeptic)
- Test specifically: does the page 1 intro pre-empt the question "wait, why are there multiple numbers?" without raising the question itself?
- Test the section transition copy: does it require the customer to remember the page 1 intro to make sense, or does it stand alone?
- Compare your final pick against the engineer-not-mystic anchor: does it sound like you wrote it?

When ready, the copy goes into `Engine/web_backend/templates/` (probably as new strings injected into the relevant section render points). That's CC's implementation work, not yours.

Estimated session: 1-2 hours of writing + 30 min editing = your morning's productive output.
