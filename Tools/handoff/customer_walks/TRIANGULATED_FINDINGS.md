# Customer Walk Triangulation
Date: 2026-04-28
Sources: 4 independent walks (Claude + 3 other models, persona-locked as new $49 customer)
Subject: Muhab Akif reading (rendered as PDF from /r/{token}/merged)

## Method
Each model walked the reading sequentially, never seen SIRR before, no domain research. Logged literal next questions per page element. Patterns extracted independently. We then identified what 4/4, 3/4, and 1-2/4 walks caught — confidence weights by overlap.

---

## TIER 1 — Universal findings (4/4 walks caught)
These are the customer-experience launch blockers. Every model saw them. Highest priority.

### 1.1 Element disagreement (Water → Air → Earth)
The reading states three different elements as if each is "yours":
- Page 1: `Element Water` (in YOUR READING band)
- Page 5: `ELEMENT Air · 4 systems · 2 groups` (in convergence)
- Page 6: `Tradition-vote element (4 oracles) Earth`

No reconciliation, no labeling about why these methodologies disagree. Customer hits all three and either disengages ("contradicting itself") or trusts blindly without noticing.

### 1.2 Headline number disagreement (3 → 1 → 2/4/6 → 51)
The reading announces different "primary" numbers across pages:
- Page 1: `Root 3` (synthesis)
- Page 5: convergence "MOST STRONGLY ON: NUMBER 1"
- Page 7: Monte Carlo evidence foregrounds `2`, `4`, and `6`
- Page 7 footer: `COHERENCE 51 · DIVERGENT`

Customer cannot tell which number "is theirs." Same root failure pattern as 1.1.

### 1.3 Jargon avalanche
Specialized terms appear with zero inline definition, requiring constant pause-and-research:
- Pattern level: Barzakh, Sandhi/Sandhya, bifurcated, Split_crown, threshold, liminal
- Numerology: Abjad, Kabir, Soul Urge, Personality, Master Builder, Pinnacle Cycles, Attitude Number, Balance Number
- Names: Mispar Gadol, Mandaean, cognate sum, Gematria, Name Weight
- Astro: ephemeris, Firdaria, Mahadasha, Vimshottari, Profection, Rahu, Shravana, BaZi, Guǐ, Manik, Nakshatra, Mewa
- Convergence: Notarikon, Albam, Dwad, Nine Star Ki, Bazhai, Lo Shu Grid, hidden_passion, luminous_dark, Agrippan, hermetic framing, Swiss Ephemeris

Even readers familiar with one tradition (e.g. tarot) hit walls in adjacent traditions. ~40 unexplained terms surfaced across walks.

### 1.4 Naked numbers without scale
Values shown as decimals or integers without unit, comparison, or interpretation:
- `Chronobiology — modern biological rhythms 73.2`
- `Circadian medicine — birth-hour organ clock 12.0`
- `Barzakh Coefficient 0.7612`
- `SIRR comparative axes (hermetic framing) 8.3`
- `COHERENCE 51`
- `Name Weight 8`

Customer cannot tell if their value is high, low, or average. Reads as engineer-debug values leaked into customer view.

### 1.5 Two BIRTH CARDs labeled identically
Name Intelligence card grid shows:
- XII The Hanged Man — `BIRTH CARD`
- Ace of Clubs — `BIRTH CARD`

Same label, different decks (tarot vs. cartomancy). Either relabel as "TAROT BIRTH CARD" / "CARTOMANCY BIRTH CARD" or merge framing.

### 1.6 "Current luck pillar unknown" exposed to customer
The astro signals list contains:
- `Current luck pillar unknown`
- `BaZi element (Chinese)` (with no value)

Data gap surfaced to the paying customer with no explanation of what's missing or why. If birth time required, the form should have collected it; if optional, the reading should explain what becomes available when added.

### 1.7 Rendering bug — empty parens in Guǐ
`BaZi Four Pillars Guǐ ( ) Yin Water` — parentheses contain no character. Likely missing Chinese character glyph due to font issue. Visible to every reader.

### 1.8 No closing / no next action
Reading ends mid-Monte-Carlo-receipt. No "save this URL," no "what to do with this," no closure, no CTA. Customer doesn't know they got the whole reading or what comes after.

---

## TIER 2 — Multi-source findings (3/4 walks)
High confidence, second priority.

### 2.1 Master number 22 unexplained
`Personality 22 · The Master Builder` — customer asks "is this 22 or does it reduce to 4?" Master numbers are an actual numerology convention (11/22/33 stay unreduced). One sentence inline solves this. Without it, the customer is stuck wondering if there's a typo.

### 2.2 Libra anchor never surfaced; Virgo appears unexplained
Customer born Sept 23 expects "Libra" somewhere. Reading never mentions it. But:
- `Profection · House 6 · 6th House - Work, health, service, daily routine (Virgo)`
introduces Virgo without explanation. Customer asks "Why Virgo when I'm Libra?" — concludes either the reading is wrong OR the system silently uses a different astrology than expected.

### 2.3 Birthday rendered as 5 in one row, 23 in adjacent row
- Numerology grid: `5 · BIRTHDAY · The Liberator`
- Tradition list directly below: `Life Purpose / Birth Day Number 23`

Same concept (the user's birthday), two different numbers shown one after the other, no reconciliation. Should at minimum be labeled "Birthday (reduced)" vs "Birthday (raw)" — or one of them removed.

### 2.4 Hidden signals counts imply collapsed reading
- `SHOW ALL 26 SIGNALS · +20 MORE` (Numerology)
- `SHOW ALL 49 SIGNALS · +43 MORE` (Name Intelligence)
- `SHOW ALL 22 SIGNALS · +16 MORE` (Astro)
- `SHOW ALL 11 SIGNALS · +5 MORE` (Convergence)

108 signals total, 84 hidden. Customer feels they got a teaser. Either: rename to "additional details" / "drill-down" framing, or expand the most important inline.

### 2.5 "These patterns do not conflict" reads defensively
Page 1 paragraph: "These patterns do not conflict — they describe different axes of the same structural architecture." Reads as reassurance for an objection the customer didn't raise. Either the conflict needs to be presented and defended, or the reassurance line should be removed.

---

## TIER 3 — Distinctive lenses (1-2/4 walks, but valuable)

### 3.1 PDF export artifacts leak (UNIQUE: Walk M4)
Browser-print-to-PDF produces visible per-page header containing the production URL, timestamp, and page number "1/7". Not a product bug per se — but customers WILL try to save/share the reading as a PDF. Solution: server-side PDF rendering with branded header/footer instead of relying on browser print.

### 3.2 No dominant archetype reads as system failure (Walk M3)
`Archetype Consensus — SIRR cross-tradition synthesis: No dominant archetype` — customer reads this as the engine giving up. Should reframe: e.g. "Your archetypal pattern is multi-axis rather than singular" with an explanation of when "no consensus" is itself a finding.

### 3.3 Counting units used interchangeably (Walk M2)
"tradition," "system," "group," "family," "engine," "oracle" all appear as countable nouns describing what's converging. Customer cannot tell if 12 systems = 12 traditions = 12 families. Pick one term per granularity level and stick to it.

### 3.4 Visual hierarchy ≠ cognitive hierarchy (Walk M2)
The page LOOKS premium (cards, planets, colors, typography) but customer cannot tell which element is the "main answer." Eye flows to numbers and cards before reaching the synthesis paragraph.

### 3.5 Duplicated sentences across pages (Walk Claude)
"Strong sensitivity to transitions and liminal periods..." appears verbatim on page 1 (in the paragraph) and page 2 (as the Threshold Birth pattern card). Either acknowledge ("as the pattern noted above suggests...") or deduplicate.

---

## Fix categorization

| Tier | Fix | Type | Effort | Leverage |
|------|-----|------|--------|----------|
| 1.1+1.2 | Reconcile elements + headline numbers | Architecture | High | **Highest** |
| 1.3 | Inline glossary / first-use explainers | Content | Medium | High |
| 1.4 | Add scale/units/comparison to naked numbers | Engine + Template | Low-Medium | High |
| 1.5 | Differentiate two BIRTH CARDs | Template | Trivial | Medium |
| 1.6 | Hide or fill "unknown" rows | Engine + Template | Low | Medium |
| 1.7 | Fix Guǐ glyph rendering | Template | Trivial | Low |
| 1.8 | Add closing / next-action / save reminder | Template + Content | Low | High |
| 2.1 | One-line master-number explainer | Content | Trivial | Medium |
| 2.2 | Surface Libra OR explain Virgo | Engine + Content | Low | Medium |
| 2.3 | Reconcile birthday rendering | Template | Trivial | Medium |
| 2.4 | Reframe hidden signals | Content | Low | Low-Medium |
| 2.5 | Remove or reframe "do not conflict" line | Content | Trivial | Low |
| 3.1 | Server-side PDF rendering | Architecture | High | Low (defer) |
| 3.2 | Reframe "no consensus" as a finding | Content | Trivial | Low |
| 3.3 | Pick canonical counting unit | Content | Low | Medium |
| 3.4 | Cognitive hierarchy redesign | UI/UX | High | Medium (defer) |
| 3.5 | Deduplicate threshold-birth sentence | Content | Trivial | Low |
