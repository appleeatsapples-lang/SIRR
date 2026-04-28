# Wave 2 Decisions — Locked 2026-04-28

After triangulating 4 customer walks and 3 advisor reviews, the following Wave 2 decisions are locked. We do not re-litigate these without new evidence.

## 2.D1 — Headline reconciliation (1.1 + 1.2)
**Decision: NOT option (a). Choose (b) + (c) hybrid.**

Keep all values. Stop presenting them as peer headlines. Separate by type:
- **Synthesis Root** = portrait summary (the "axis the reading returns to"). Primary customer-facing headline.
- **Convergence** = evidence count (how many independent systems agree on a number)
- **Tradition-vote element** = one evidence lane, not a competing answer
- **Coherence score** = meta-statistic about the convergence pattern itself

Implementation requires section-transition copy that explicitly tells the customer what kind of result each section is. Synthesis paragraph at the top, then "the evidence behind it" framing for everything that follows. Numbers like 1, 2, 4, 6 are not "your number" — they are systems-agreement counts.

This is a copy + template restructuring task. No engine changes. Estimated 1-2 days.

## 2.D2 — Jargon handling (1.3)
**Decision: option (d) — inline parenthetical first mention.**

Format: `Mahadasha (a Vedic life period that runs ~18 years)` on first occurrence in any section. Subsequent mentions in the same section do not need re-defining.

Rejected:
- (a) tooltips — break in PDF and on mobile
- (b) footnotes — visual clutter on long scroll
- (c) end glossary — terrible completion rate

Glossary drawer at bottom may be added LATER as a v2 enhancement, but the source copy must already carry the inline definition. Drawer is additive, not load-bearing.

Estimated: ~40 terms × 2 min/term = 80 min copy + template review. ~1 day.

## 2.D3 — Birth time / data gaps (1.6)
**Decision: option (c) — hide unknown rows for launch.**

Rejected for launch:
- (a) required collection at checkout — adds friction, customers don't always know birth time
- (b) optional with progress framing — "87% complete" implies the reading is incomplete, which becomes a marketing/expectation problem

For Wave 1 we hide rows that contain `unknown`, blank values, or empty-glyph slots. We compute everything we can with date alone and present that as the complete reading.

Revisit threshold: post-100 customers. If a meaningful fraction asks "where is my luck pillar / time-gated reading?", we add optional birth-time UX. Until then, do not surface what we don't have.

Estimated: 0 days (handled by Wave 1 row suppression).
