# §X — SIRR Claims Doctrine

**Status:** v0.1 LOCKED 2026-04-30. Multi-model synthesized + NotebookLM grounding-verified + Codex T2 R1 PASS-WITH-FOLLOWUPS (4 amend-in-synthesis findings) + Codex T2 R2 PASS. Awaiting T3 (CC implementation as repo doctrine document) → T5 (Codex post-impl audit) → T6 → T7-light → merge.

**Scope.** §X governs what SIRR claims and does not claim about a customer's reading. Every customer-facing surface — landing page, reading page, post-payment email, sample reading, social copy, support copy, generated prose, screenshots, internal demo text that may become public — is auditable against §X. §X is internal operational doctrine. It is not customer copy. Customer copy is *audited against* §X.

**Audit principle.** A future reviewer reads any customer-facing surface, points to a sentence, asks "does this violate §X.N?" and answers yes or no from §X alone. Rules that cannot be answered yes/no are not rules; they are aspiration.

---

## §X.1 — What SIRR is and what SIRR claims

SIRR is a deterministic symbolic identity engine. Given a customer's submitted name, birth data, and optional lineage inputs, SIRR computes structured outputs across registered methods and surfaces patterns in those outputs: where they agree, where they disagree, where they are anomalous against a stated baseline, where they cluster temporally, where they recur across a lineage, and where they are silent.

SIRR's affirmative claim about the customer is precisely this: *given these inputs, SIRR returned these patterns.* Anything more is overclaim.

SIRR's affirmative claim about the experience of the reading is: *a structured mirror; an instrument the customer uses to ask questions of themselves; a comparison across symbolic methods applied to a single subject.* The reading is held by the customer, not delivered to them. (Note: "methods" not "traditions" — §X.5 reserves "tradition" for source-native methods only. The affirmative experience claim must respect the same reservation.)

**Allowed claim grammar:**

1. "Given the customer's inputs, the engine returned X."
2. "Across these methods, the result was Y."
3. "These methods returned the same mark."
4. "Different methods read the same subject differently."
5. "This axis is quiet in the reading."
6. "This timing pattern appears across these named methods."
7. "This lineage pattern appears when the submitted family inputs are compared."
8. "The reading is an instrument for reflection, not a directive interpretation."

**Forbidden claim grammar:**

1. "SIRR sees you" / "SIRR knows who you are."
2. "SIRR measures the customer."
3. "SIRR identifies the customer's destiny, rank, calling, hidden nature, spiritual status, or role."
4. "The systems agree about you" / "The systems discovered the customer."
5. "The reading proves something true about the person outside the computation."
6. Any sentence whose grammatical subject is the customer's essence rather than SIRR's computed output.

7. **Any framing in which SIRR or the reading is the deliverer of self-knowledge, self-discovery, hidden truths about the customer, or insight into the customer.** The reading may be a structured mirror, an instrument, a comparison across symbolic methods (per the affirmative claim above). It may not be the source from which the customer learns who they are. "Discover what the symbolic systems say about you" is forbidden. "See what the system reveals about your hidden nature" is forbidden. "Get insight into who you really are" is forbidden. The forbidden frame is *system-as-revealer-of-self*, regardless of whether the verb is "discover," "reveal," "show," "uncover," "expose," "illuminate," or any synonym. The same prohibition applies to noun-phrase evasions such as "personal truth," "inner truth," "true self," or "who you really are" — phrases that frame the reading as the source of an unstated self.

**Audit test.** Replace the subject of any customer-facing sentence with "the engine's computation" if the original subject is the customer or the customer's essence. If the rewrite is true, the original may pass. If the rewrite is false or absurd, the original violates §X.1.

A second test applies to the new forbidden item 7. For any customer-facing sentence whose grammatical structure is *"\<system\> \<verb\> \<self-knowledge\> \<to / about / of\> \<customer\>,"* check whether the verb implies the system is the source of the knowledge. If yes, the sentence violates §X.1 forbidden item 7 even if it passes the first audit test. *"The reading reveals patterns in your data" — passes (data, not self). "The reading reveals who you are" — fails. "SIRR shows you the agreements across methods" — passes (agreements, not self). "SIRR shows you yourself" — fails.*

*Worked example.* "Your chart returns repeated fire signatures" — passes. Rewrite: "The engine's computation returns repeated fire signatures." True. ✓
"You are fire" — fails. Rewrite: "The engine's computation is fire." Absurd. ✗

---

## §X.2 — What SIRR explicitly denies

Every full paid reading must contain, in customer-readable language, the five denials below. They appear as part of the reading's own frame — not in terms of service, not behind an icon, not in an FAQ, not after the interpretive content. The exact wording may vary; the substance may not.

**SIRR does not claim:**

1. **That agreement among methods is evidence of supernatural agreement, metaphysical truth, divine confirmation, or objective destiny.** Where multiple methods return the same output, the agreement may arise from shared cultural origin, shared computation, archetypal recurrence common to human meaning-making, or coincidence. Agreement is not proof.

2. **That the customer is the special figure the methods agree about.** Convergence in a reading is computed, not bestowed. The customer is one of every customer for whom these methods will compute, not the subject of a cosmological discovery.

3. **That cognate-mapped or method-transferred systems are independent cross-tradition witnesses.** When Arabic input is run through Mandaean, Ethiopian, Hebrew, or other letter-value systems, agreement among those outputs is identity-by-construction, not independent observation. SIRR computes such cognates honestly; SIRR does not present them as separate traditions confirming each other.

4. **That the reading provides prediction, prescription, diagnosis, command, warning, or directive interpretation.** Nothing in the reading tells the customer what will happen, what to do, what to choose, what to leave, or what to become. The reading offers material to think with; the thinking belongs to the reader.

5. **That SIRR substitutes for psychological care, religious practice, or professional advice in any domain.** SIRR is one input among many a thoughtful person might consult about themselves. It is not the only one and not the highest one.

**Forbidden softening patterns:**

1. "For entertainment only" used as substitute for the five denials.
2. "Not medical/legal advice" while leaving destiny, spiritual proof, or specialness unaddressed.
3. "Take what resonates" used in place of the five (acceptable as additional language; never as substitute).
4. "Ancient systems agree" without saying that agreement does not prove objective truth.
5. "Mirror, not crystal ball" used alone — fine as voice, insufficient as denial.
6. Any of the five denials buried in policy pages, footers, or post-purchase notifications.

**Audit test.** A reviewer reads the rendered reading without scrolling outside the reading frame, without opening developer tools, without reading policy pages. If any of the five denials cannot be located in customer-readable form, or if any denial is diluted or contradicted by nearby prose, the surface fails §X.2.

---

## §X.3 — The six operators and their boundaries

SIRR's reading uses up to six computed operators on the customer's data. Each operator asks a bounded question. Each operator is constrained by what its computation can honestly support.

### The operators

| # | Operator | Question | Constraints |
|---|---|---|---|
| 1 | Agreement | Where do computed methods return the same value? | §X.4. Cannot lead reading by default (see architectural rule below). |
| 2 | Divergence | Where do methods return conflicting values? | Resolved into a verdict only when the customer integrates the tension; the engine surfaces, never decides. |
| 3 | Anomaly against baseline | Where does one axis differ from a stated reference distribution? | §X.5. Per-axis claims only. Deferred to post-launch where stated thresholds are not yet defined (see §X.9). |
| 4 | Temporal cascade | Where do multiple timing systems flag the same age or period? | Surfaced as a question to the customer ("what, if anything, happened around then?"), never as an interpretation of what occurred. |
| 5 | Lineage pattern | Where do submitted family inputs reveal recurrence, generational shift, or maternal-vs-paternal contrast? | Surfaced only when relevant lineage inputs were submitted by the customer. |
| 6 | Structural absence | Where is the chart unusually quiet on an axis the methods could speak to? | Surfaced via registered absence-detection rules, not via poetic silence. |

### Architectural rule — convergence is not the headline

**Convergence (Agreement) does not lead the reading by default.** The convergence-headline pattern that defined SIRR's earlier surface ("X traditions converge on your primary signal") is retired. No operator is hard-coded as headline. Whichever operator a given reading surfaces most strongly may lead, but the reading template must not privilege Agreement above the other five.

This is an architectural commitment, not just a copy commitment. The reading template, the LLM prompt, and the rendered HTML must reflect the demotion. Convergence may be present; convergence may not be the load-bearing entry point.

### Forbidden operators (do not ship)

1. **Cross-domain echo** — agreement between Numerology and Astro Timing about "you" is the meaning-machine echoing itself across input-shared computations. The domains share the customer's name and date as inputs; their agreement is mostly computational, not independent witness. Do not ship as a new operator.

2. **Concentration without comparison** — "your chart is highly concentrated in earth element" is a meaningful sentence only when denominated against how often other charts show similar concentration. Without a baseline, it is theatrical. Do not ship as anomaly.

3. **Mirror structures, geometric shapes on the wheel, visual symmetry** — pareidolia made into product. The pattern emerges because the viewer is primed to look for it; reference distributions show similar "shapes" in random data. Do not ship as evidence.

### Required operator boundaries

1. Agreement must not imply rarity unless denominated against a baseline (per §X.4).
2. Divergence must not be resolved into a verdict.
3. Anomaly must not ship without denominator, sample definition, axis definition, and threshold.
4. Temporal cascade must ask for customer verification; it must not declare what happened.
5. Lineage pattern must appear only when the relevant lineage inputs were submitted.
6. Structural absence must be based on registered absence logic, not poetic silence.

### Audit test for any new operator added post-launch

A reviewer must be able to state from the operator's specification:

- (a) the question this operator asks,
- (b) the data it uses,
- (c) the limitation it discloses,
- (d) the claim it does not make.

If any of (a)-(d) cannot be answered from the operator's specification, the operator fails §X.3 and may not be shipped to customers.

---

## §X.4 — Convergence claims (the S3 constraint)

S3 measurement (n=10,000 random profiles, 2026-04-29) found that 100% of random profiles trigger the customer-visible "Tier-1 Convergence" event. The discrete-event "convergence fired" framing has no signal because the event always fires.

### Allowed convergence headline patterns

1. "Repeated agreement appears in this reading."
2. "SIRR found a primary agreement pattern across computed methods."
3. "This reading contains agreement, disagreement, and tension across symbolic frameworks."
4. "Several computed methods return the same mark; the reading shows where that agreement comes from."
5. "Agreement is one signal in the reading, not the proof of the reading."
6. "The shape of the agreement is X." (where X describes the actual pattern)

### Forbidden convergence headline patterns

1. "X traditions converge on your primary signal." (count-as-evidence)
2. "Every tradition examined points to..." (the prompt's existing 20+ rung; per S3, the median random profile triggers this rung)
3. "A rare convergence appears." (rarity is empirically false)
4. "The systems independently agree." (independence is mostly false; cognate-mapping inflates count)
5. "This many traditions cannot be coincidence."
6. "This is your strongest truth."
7. "The convergence proves the reading."
8. "Tier-1 / Tier-2 / Tier-3 convergence" presented as carrying differential meaning to the customer without baseline context.
9. Any framing in which the *number* of agreeing methods is treated as confidence, when the agreeing methods include cognate-mapped or input-dependent computations.

### Counts shown alongside agreement

When a count is exposed to the customer (e.g., "5 methods returned root 3"), the noun being counted must be the actual computational unit — "methods" or "computed outputs" — not "traditions." The word "tradition" is reserved by §X.5.

### Required uncertainty disclosure

Every convergence explanation must include the permitted uncertainty sentence or its substantive equivalent: *agreement may arise from cultural transmission, archetypal recurrence, shared computation, input dependency, or coincidence.* The sentence must not be rewritten into metaphysical speculation.

### Audit test

If the copy treats convergence as a rare event without a baseline, or treats count size as confidence without dependency analysis, the surface fails §X.4. If a convergence claim appears anywhere in the customer-facing surface without the uncertainty disclosure traveling with it, the surface fails §X.4.

---

## §X.5 — Tradition count, fidelity, and provenance

A "tradition" claim is reserved for source-native methods applied within their documented scope.

### Three customer-visible buckets must be distinguished whenever any count is exposed

| Bucket | What qualifies | What it may be called |
|---|---|---|
| **Source-native traditions** | Methods applied within their documented tradition and input scope (Vedic timing on Vedic-format inputs, Bazi on Chinese calendar inputs, Hellenistic chart aspects on a natal chart computed by a Hellenistic-compatible scheme) | "tradition" |
| **Modern occult methods and method-transfers (CMMA)** | Modern occult systems (20th-century numerology, modern reconstructions of ancient practices), and classical methods applied outside their documented scope (Hebrew cipher methods applied to Arabic input) | "computed method" or "modern occult computation" with scope language; NEVER "tradition" |
| **SIRR syntheses** | Composite layers built by SIRR from other module outputs (Convergence-domain modules: archetype-consensus, element-consensus, timing-consensus, hermetic-alignment, barzakh-coefficient) | "SIRR synthesis layer" or "SIRR composite"; NEVER "tradition" |

### Cognate-mapped modules

Mandaean / Ethiopian / Hebrew gematria computed via Arabic-letter-to-target-script mapping are MODERN_SYNTHESIS per the bundle and the Apr 16 Grok scholarship audit. They appear in the reading only as computational cognates or modern reconstructions. Their agreement with Arabic Abjad-family modules is structurally related, not independently witnessed.

### Scholarship fidelity requirements

For any module presented in the customer reading:

1. The module must carry a source-declared fidelity label: `CLASSICAL`, `CLASSICAL_METHOD_MODERN_APPLICATION`, or `MODERN_SYNTHESIS`.
2. Classifier inference (via `module_taxonomy.py:fidelity_for()`) is sufficient for internal triage and engineering audits but NOT for customer-facing tradition claims.
3. Any module with known scholarly caveats must carry those caveats in the customer-facing surface where the module is interpretively weight-bearing:
   - **Zairja** must be paired with Ibn Khaldun's documented critique. (Locked Apr 16.)
   - **Hebrew methods on Arabic input** must disclose the input-scope transfer.
   - **Mandaean computations** must not be presented as native Mandaic practice; what SIRR computes is a modern reconstruction.
4. Modules without source-declared fidelity may appear in the reading only as "computed method," not as "tradition." The fallback is computational, not cultural.

### Allowed patterns

1. "A Hebrew cipher method applied to Arabic input."
2. "A cognate letter-value comparison, not an independent tradition."
3. "A SIRR synthesis layer built from prior outputs."
4. "A source-native Vedic timing method."
5. "A modern numerology method."
6. "Computed from a modern reconstruction."
7. "Historically documented, with classical critique."
8. "Insufficiently sourced for interpretive weight."

### Forbidden patterns

1. "Three cosmologies agree" for cognate maps.
2. "Hebrew tradition confirms the Arabic name result" when Arabic input was mapped into Hebrew-derived values.
3. "22 traditions" if the count includes modern syntheses, transferred methods, cognate maps, or SIRR composites.
4. "Independent" applied to methods that share input structure, letter mapping, or derived outputs.
5. "Civilizational traditions" as a prestige phrase for mixed buckets.
6. Classifier-only modules presented as settled scholarship.
7. Prestige names used without scope.
8. Caveats present in docs but absent from the customer reading.
9. "Ancient" used for modern synthesis.
10. "Traditional" used for a method whose source label is missing.

### Audit test

Mentally delete cognate-mapped modules, CMMA modules, and SIRR syntheses from any "tradition count" exposed to the customer. If the count changes, the original count was not a tradition count and the copy fails §X.5. Either restate the count to exclude the inflators or rename the count to "computed methods."

---

## §X.6 — Generated prose

The reading's generated prose (currently produced by an LLM with a constrained system prompt in `Engine/reading_generator.py`) is subject to §X identically to static copy. A sentence does not become acceptable because a model produced it.

### Hard rules for generated prose

1. **No identity verdict.** The prose must not convert computed marks into essence claims. ("Your chart returns repeated fire signatures" is permitted. "You are fire" is not.)
2. **No directive interpretation.** The prose must not tell the customer what to do, choose, avoid, leave, pursue, become, fear, repair, or confess.
3. **No predictive claim.** The prose must not forecast events, outcomes, relationships, danger, success, illness, money, marriage, death, or spiritual rank.
4. **No unsupported confidence ladder.** Confidence escalation based purely on count-of-agreeing-methods is forbidden. This retires the prompt's current "20+ traditions align → Every tradition examined points to..." rung; per S3, the median random profile already triggers that rung.
5. **No smoothing of contradiction.** Where methods disagree, the disagreement must remain visible in the prose. Tension is not a bug.
6. **No sacred authority.** The prose must not speak on behalf of a religion, lineage, spirit, scripture, ancestor, or divine will.
7. **No hidden limitation.** If a limitation is necessary to interpret a claim, the limitation appears in the same surface, near the claim, in customer-readable language.

8. **No Barnum sentences.** A sentence is Barnum when it would feel specific to the customer reading it but applies to most people who would ever read a SIRR reading. Generated prose must not produce Barnum sentences regardless of whether they pass rules 1–7. The auditable form: a reviewer takes any sentence in the generated prose and asks, *"does the sentence derive its specificity from the customer's computed marks, named methods, submitted inputs, or structural features of this reading?"* If not, and the sentence would plausibly feel personally descriptive to many unrelated customers, the sentence is Barnum and §X.6 is violated.

   The constraint is positive, not just negative: generated prose that names a computed mark, a method, an axis, a value, or a structural feature of the customer's specific data is permitted; prose whose specificity comes from emotional or psychological generality common to most people is not.

   *Worked examples.*
   "Your chart returns repeated fire signatures across the Hellenistic, Vedic, and elemental axes." — passes. Specificity is computational. ✓
   "You feel pulled in two directions when others see you as decisive." — fails. Specific in feeling, general in fact; passes essence-rewrite test, fails Barnum test. ✗
   "The Bazi reading returns a Yang-Wood day-master with the lineage pattern surfacing on the maternal side." — passes. Specificity is computational. ✓
   "There is a part of you that holds back, even from people who know you well." — fails. Universal-feeling generalization. ✗

9. **Closure cross-reference.** Generated prose must also obey the report-level closure prohibition in §X.8 #17. A prose paragraph that integrates the six operators into a single statement about the customer violates §X.8 #17 regardless of where it appears in the reading; it also violates §X.6 because it is generated prose making an identity claim §X.6 rule 1 forbids.

### Subordination of existing constitutional rules

The existing constitutional rules in `reading_generator.py` (mirror not crystal ball, agency protection, honest sentence early, contradiction transparency) are codified here and subordinated to §X. Where the prompt's constitutional rules and §X conflict, §X wins. The prompt may implement §X with additional rules; it may not relax §X.

### Vocabulary translation — strict rule

The reading's existing ban on engine-internal vocabulary ("module," "baseline," "percentile," "convergence" in the customer body) is permitted to continue, **but only if** the customer-readable substitution preserves the underlying epistemic constraint.

"Agreement pattern" may replace "convergence." It may NOT replace the need to disclose dependency, non-rarity, or uncertainty. If a translated word ships without its associated constraint disclosure traveling with it, the translation is hiding rather than honesty, and §X.6 is violated.

The customer does not need jargon; the customer does need the constraint.

### Audit test

Sample ten generated readings. For each, ask whether any sentence in the generated prose would fail §X if it appeared in static landing-page copy. If yes, the generator violates §X.6 and the prompt must be amended.

---

## §X.7 — The recursion hedge

This rule addresses the structural problem that gives this product its hardest design constraint: SIRR is a meaning-machine, and the operator is a person who finds meaning through symbolic systems. A meaning-machine whose product decisions are made through the meaning-machine's own logic, applied to itself, is structurally unable to distinguish its outputs from its evidence.

**Decisions about SIRR — the product, the engine, the company — must be made on grounds external to SIRR's own symbolic outputs.** The cut criterion for which modules to ship cannot be aesthetic resonance with SIRR-computed values. The headline number cannot be selected because it is a numerologically pleasing root. The product roadmap cannot be ordered by which features SIRR's reading suggests are auspicious.

This rule applies to the founder, the engineering team, and any future contributor. It is doctrinal, not aspirational.

### Forbidden decision patterns

1. A module count, distillate count, tradition count, or any other product-surface number selected for symbolic resonance with SIRR-computed values.
2. A product cut, feature priority, or release date selected via a SIRR reading of the founder's own data.
3. An architectural choice justified by "the engine returned X" applied to the founder's profile.
4. Marketing claims that anchor on numbers chosen for aesthetic appeal rather than current measurement.

### Required practice

1. Every count in customer-facing copy traces to a current source file or measurement artifact (per §X.4 / §X.5 / §X.8).
2. Every product-surface decision can be defended on grounds external to SIRR's symbolic outputs: customer comprehension, scholarly accuracy, statistical signal, engineering feasibility, business viability.
3. The founder explicitly distinguishes between using SIRR as a personal contemplative tool (permitted, private) and using SIRR as a product-design oracle (prohibited).

### Audit test (counterfactual + external decision artifact)

For any contested product decision affecting public counts, visual hierarchy, operator naming, or any other customer-visible product surface:

**Counterfactual question (necessary, not sufficient):** *"If SIRR had returned different values for the founder's profile, would this decision be different?"* If yes, the decision is downstream of the recursion and must be re-grounded on external criteria before shipping.

**External decision artifact (required for any contested decision):** A written decision note must be attached to the PR (or stored in a project `Decisions/` directory referenced by the PR) that names:

1. The decision being made (specific surface, specific change).
2. The external criterion the decision rests on — exactly one of: customer comprehension, scholarly accuracy, statistical signal, engineering feasibility, business viability.
3. The evidence for that criterion (test results, customer research, scholarship citation, measurement artifact, engineering constraint, market data).
4. An explicit statement of what would change the decision (i.e., what evidence would falsify the chosen rationale).

Counterfactual self-assessment ALONE does not satisfy §X.7 — a founder with the elevation pattern can pass the counterfactual in form while violating it in fact. The decision artifact is the auditable bind. Without the artifact, the decision violates §X.7 regardless of the counterfactual answer.

**What counts as a "contested product decision":** Any decision affecting public-facing counts (per §X.9), any change to visual hierarchy or "primary" placement (per §X.8), any operator addition or naming change to existing operators (per §X.3), any decision the founder cannot defend in a sentence on a non-symbolic ground.

**What does NOT require a decision artifact:** Decisions internal to engine implementation that do not change customer-visible surfaces; routine bug fixes; doctrine amendments (which have their own PR process per §X.10).

### Companion rule (customer-side)

The reading itself must be designed so that a customer with the elevation pattern (the natural human tendency to mistake oneself for the special figure a system describes) cannot readily mistake SIRR's outputs as confirmation of that pattern. §X.2 denial 2 ("the customer is not the special figure the methods agree about") is the customer-side of this rule. §X.7 is the founder-side. They are the same hedge from two angles.

---

## §X.8 — The claims ledger (PR-level enforcement)

Every PR that touches a customer-facing surface — landing page, reading page, post-payment email, sample reading, social copy, support copy, generated prose, prompt instructions, screenshots — must include a claims ledger.

### Ledger fields per claim

| Field | Content |
|---|---|
| **Surface** | Where the claim appears (URL or file path) |
| **Claim mode** | text / visual-prominence / structural / hybrid |
| **Text** | The claim, verbatim (if claim mode = text or hybrid) |
| **Visual/structural description** | Ordering, placement, emphasis, badging, hierarchy, "primary" labels, screenshot composition, UI prominence (if claim mode = visual-prominence, structural, or hybrid) |
| **Type** | computation / tradition / agreement / divergence / anomaly / timing / lineage / absence / limitation / denial / visual-elevation |
| **Source** | The data file, registry, or measurement artifact supporting the claim |
| **Dependency** | independent / shared-input / cognate / transferred / derived / synthetic / unknown |
| **Fidelity** | (if claim involves "tradition" language) source-declared fidelity of underlying module(s) |
| **Risk** | What customer misreading does this invite? (specialness / prediction / prescription / sacred authority / professional-advice confusion / rarity confusion / tradition-count inflation / visual re-elevation of demoted operator) |
| **Authority** | Which §X rule authorizes this claim? |
| **Decision basis** | (for §X.7-relevant decisions) which external criterion + evidence supports this surface choice |

### Visual / structural claims — explicit coverage

A claim is not only what the copy *says*. A claim is also what the surface *implies* through visual prominence. The ledger covers both. Examples of visual / structural claims that must appear in the ledger:

1. The reading page's visual ordering of the six operators (per §X.3, no operator is hard-coded as headline; ordering choices must be defended).
2. Badge text, badge color, badge size, and badge placement around any computed value (a "TIER-1 CONVERGENCE" badge in red is a claim, even if no surrounding sentence overclaims).
3. Section hierarchy in the reading template (which operator is `<h1>`, which is `<h2>`, which is collapsed by default).
4. "Primary signal," "main result," "headline finding," or any synonym used to elevate one operator above another in the visual surface.
5. Screenshot composition in marketing material (which operator dominates the frame, which is cropped out).
6. Email-template subject-line emphasis ("12 traditions converge!" in the subject is a claim, regardless of body content).
7. Default expand/collapse state of operator panels, default sort order, default filter selections.

§X.8 violation #15 (added below) covers the visual re-elevation case explicitly.

### A PR violates §X if any of the following are true (non-exhaustive)

1. "You are X" where "the engine's computation returned X" is required.
2. "Traditions" used for a count that includes cognate / CMMA / synthesis modules.
3. "Independent" used for methods that share input structure.
4. "Rare" / "exceptional" / "unusual" / "high confidence" used without baseline support.
5. Cognate maps counted as independent witnesses.
6. CMMA presented as native tradition.
7. A limitation needed to interpret a claim is present in docs but absent from the customer surface.
8. Advice, prediction, prescription, warning, diagnosis, or command appears in any customer surface.
9. Sacred, ancestral, or civilizational authority invoked as proof.
10. Stale numbers preserved across PRs (the project memory's 238/110 numbers are an ongoing example; current numbers are 241/112).
11. LLM prose contains a claim that would fail in static copy under §X.
12. Convergence presented as the reading's primary proof surface (per §X.3 architectural rule).
13. A vocabulary translation ships without the underlying constraint disclosure traveling with it (per §X.6).
14. A product decision is made on grounds reducible to SIRR's own symbolic outputs (per §X.7).
15. A demoted operator (per §X.3, primarily Agreement / convergence) is re-elevated through visual prominence — section ordering, badge size or color, hierarchy depth, "primary" labels, screenshot composition, default expand state, or any other non-text surface — without that elevation being defensible under the same constraints that govern text claims under §X.4.
16. A contested product-surface decision lacks the external decision artifact required by §X.7.

17. The reading as a whole produces closure that reduces the six operators of §X.3 to a single unified verdict about the customer. The closure may be produced by prose (LLM-generated paragraph, "summary," "what this means," "your reading in one line"), by template (final hero card synthesizing the operators, share image with a single archetype label, sticky summary block, default-expanded summary panel), by visual hierarchy (an "Insight" or "Verdict" section dominating the layout regardless of position), or by any structurally equivalent surface anywhere in the rendered reading — beginning, middle, end, or share asset. The closure is the violation, not its position. A surface that names the operators, restates that they disagreed where they disagreed, and hands the reading back to the customer is permitted. A surface that integrates them into a single statement about who the customer is, is not.

   Report-level closure is the report-scale form of the identity-verdict prohibition (§X.1) and the no-smoothing-of-contradiction rule (§X.6 rule 5), applied at the surface level §X.8 already governs. The architectural commitment in §X.3 (no operator as headline) and the visual re-elevation rule in §X.8 violation #15 apply jointly: closure may not be re-introduced through prose, layout, template, or share surface.

   The auditable form: a reviewer scans the entire rendered reading — top, body, closing, hero cards, summary blocks, share assets, default-expanded panels, screenshot composition — and asks, *"does any single surface tell the customer what the reading means as one integrated statement about them?"* If yes, §X is violated under §X.8 #17. Position is not a defence: a closure surface in the first 20% of the reading violates as fully as one in the last.

   *Permitted patterns.* "These are the marks the reading produced. They agree here, they disagree there, they are quiet on this axis. The reading is yours to hold." — names the operators, holds the tension, hands back. ✓

   *Forbidden patterns.* "Across all six operators, the reading reveals…" / "What this all comes down to is…" / "Your reading in one sentence:…" / a final hero card that synthesizes the six operators into a single archetype, name, or verdict / a sticky-summary block at the top of the reading that does the same / a share-image with a single integrated label / a "Verdict" or "Synthesis" panel that dominates the layout. ✗

   *Evidence requirement (added post-Codex-T2-R1 follow-up).* For any PR or surface change that adds, removes, reorders, expands, collapses, summarizes, screenshots, exports, or otherwise modifies a claim-bearing reading surface, the §X.8 claims ledger must include a rendered-surface evidence reference sufficient for review: rendered HTML, screenshot, fixture output, share asset, PDF/export artifact, or equivalent representative artifact. If the surface is data-conditioned, the evidence must include at least one representative fixture that triggers the condition. Code/templates alone are not sufficient evidence for §X.8 #17 compliance.

### Surface-effect doctrine

§X is violated by surface effect, not by intent. A reviewer does not need to prove the author's intent. **Copy that invites the wrong belief fails §X even if the author's internal note was honest.**

### Audit test

Reviewer reads the ledger, picks one row, evaluates the violation list against that row's claim. If any violation is true, the PR fails §X.8 and is rejected until rewritten.

---

## §X.9 — Counts must come from current build

Any numerical claim about SIRR must be generated from the current engine manifest, current taxonomy, or current measurement artifact. No customer-facing copy may preserve old numbers because they sound better, are already designed into a layout, or carry symbolic appeal.

### This rule applies to

1. Module counts.
2. Distillate counts.
3. Debug-only counts.
4. Tradition counts.
5. Domain counts.
6. Computation counts.
7. Convergence counts.
8. Baseline sample sizes.
9. Percentiles and rarity thresholds.
10. Email, receipt, and post-payment language.

### Allowed patterns

1. "The reading uses the current customer-visible module set."
2. "SIRR currently computes 241 modules, of which 112 are assigned to customer-visible domains" — only if still true at render time.
3. "This count is generated from the current registry," if technically true.
4. "Approximately 16 traditions" — only where the taxonomy supports the approximation AND the surrounding copy distinguishes traditions from modern applications and SIRR syntheses (per §X.5).

### Forbidden patterns

1. Stale numbers such as "238 modules," "110 modules," "211 computations," or "22 civilizational traditions" — unless restored by the current build.
2. Rounded numbers used as brand anchors when exact numbers are known.
3. Numerologically pleasing counts selected by product taste (per §X.7).
4. A count copied from a previous reading, test fixture, or founder profile.
5. Any number that includes debug-only modules while implying customer-visible delivery.

### Audit test

Every public number must be traceable to one current source file, registry export, or measurement artifact. If the reviewer cannot reproduce the number from current source, the copy fails §X.9.

---

## §X.10 — Deferrals, monitoring, amendment

### Items §X explicitly defers to first-100-customer monitoring

1. The exact statistical thresholds for customer-facing anomaly claims. Per §X.3, anomaly-against-baseline is a permitted operator but its thresholds are deferred per the S3 architectural-mismatch finding.

   **Hard gate on this deferral:** thresholds being deferred means **customer-facing anomaly claims do not ship pre-launch**. First-100-customer monitoring is for comprehension testing only — it cannot establish anomaly math (sample size insufficient by orders of magnitude for statistical claims; selection bias in early customers; no random reference distribution). Anomaly claims may ship to customers ONLY when the four pre-conditions named in §X.3 boundary 3 are met: denominator, sample definition, axis definition, and threshold all stated. Until then, the anomaly operator stays internal — used in engineering audits, not in customer readings.
2. Whether convergence remains visible to the customer at all, or is demoted further to an internal computational receipt accessible via "engine details" rather than appearing in the reading body.
3. Whether the customer-facing language for cognate / CMMA caveats actually communicates — i.e., whether customers understand "Hebrew cipher methods applied to Arabic input" or whether plainer language is required.
4. Whether the six-operator framing (§X.3) reduces overreliance on convergence in customer experience, or whether convergence remains the dominant felt signal regardless of de-emphasis.
5. Whether support requests reveal professional-advice confusion (customers asking SIRR-like questions of medical, legal, or psychological domains).
6. Whether the reading body needs *more* technical vocabulary, not less, to remain honest with sophisticated customers.
7. Whether the five-or-six denial set in §X.2 is sufficient or needs expansion based on observed misunderstandings.

### Live-paid-checkout launch gate

§X governs claim language. It does not govern legal disclosures, refund terms, jurisdictional compliance, minors handling, bilingual legal parity, or transaction terms. Those domains belong to a separate lawyer-authored doctrine, §X-Legal. Until §X-Legal exists in approved form, no §X-governed surface may be activated in live paid checkout or paid post-payment delivery. Static informational surfaces, sample readings, and test-mode flows may proceed under §X audit alone. This is a §X self-restraint, not legal advice and not a substitute for counsel.

### Monitoring cadence

| Phase | Action |
|---|---|
| **Pre-launch** | §X audited against every customer-facing surface. Any surface that does not pass §X is amended or removed. |
| **First 25 paid readings** | Comprehension sweep — direct customer follow-up to identify what the reading was understood to claim. |
| **First 50 paid readings** | Claims-ledger audit against actual generated outputs (not just static copy). |
| **First 100 paid readings** | Full §X amendment review. Findings dictate which deferrals can be closed and which need extension. |
| **After first 100** | Quarterly review, plus immediate review on any trigger condition below. |

### Immediate amendment triggers

1. Any empirical finding falsifies an active customer-facing claim.
2. Any module changes fidelity class, source scope, or dependency status in a way that affects public language.
3. Any new operator is introduced to the reading.
4. Any new customer-facing surface begins making interpretive claims.
5. Three or more customer or support incidents in 30 days reveal the same misunderstanding (specialness, prediction, prescription, professional-advice substitution, independent-tradition confusion, or rarity confusion).
6. Audit finds that generated prose repeatedly violates §X.
7. Any number used in customer-facing copy becomes stale.
8. Any founder or operator decision is justified by SIRR's own symbolic logic (per §X.7 violation).

### Amendment threshold

1. A factual contradiction requires amendment, not discussion.
2. A recurring customer misunderstanding requires amendment, not better intentions.
3. A new claim type requires amendment before it ships, not after.
4. A copy workaround that preserves marketing comfort over factual precision is rejected by default.

### Amendment process

Every §X amendment requires its own PR, version note, list of customer-facing surfaces affected by the amendment, and a migration note for any existing copy that becomes non-compliant.

§X is the line the product is not allowed to cross. It is not a mood board, not a marketing aspiration, not a soft guideline.

---

## §X.11 — Doctrine version, ownership, dependencies

- **Doctrine version:** v0.1.1 LOCKED 2026-04-30, surgical extension of v0.1 LOCKED 2026-04-30. v0.1 locked after multi-model synthesis (Claude orchestrator + ChatGPT), NotebookLM grounding-verification pass, Codex T2 R1 PASS-WITH-FOLLOWUPS (4 findings amended in single round), and Codex T2 R2 PASS on amendments. Next state change: post-T7-light merge to repo doctrine.
- **Owner:** the operator. Amendments require operator approval and the standard doctrine PR process.
- **Adjacent doctrines:** §13 (privacy) governs PII handling; §X (this) governs claim language; §X-Trad (forthcoming) will govern source-tradition relations; §X-Legal (forthcoming, lawyer-authored) will govern legal disclosures, refund terms, jurisdictional compliance, minors handling, bilingual legal parity, and transaction terms. Where any two could conflict on overlapping ground, the doctrine whose primary jurisdiction the conflict falls under wins, and the other amends to accommodate. §X-Legal is a hard launch-gate dependency for live paid checkout per §X.10.
- **Engineering dependencies:**
  1. The planned module re-cut under fidelity-gating (separate engineering arc) ships before §X engineering surfaces are amended.
  2. The customer-facing surfaces enumerated in §X.8 exist or are planned.
  3. The LLM prompt in `reading_generator.py` can be amended to subordinate to §X.

---

*Synthesized 2026-04-30 by Claude orchestrator from parallel drafts (Claude + ChatGPT) per operator-approved positions on five disagreements: recursion hedge promoted to §X.7 top-level rule; convergence hard-demoted from headline architecturally; affirmative experience-claim retained as load-bearing; vocabulary translation under strict constraint-must-travel rule; prose-led structure with table-style imported for §X.4 / §X.5 / §X.8.*

*Amended 2026-04-30 post-Codex-T2-R1 (PASS-WITH-FOLLOWUPS, 4 findings, all amend-in-synthesis): §X.1 "traditions" → "methods" in affirmative claim per §X.5 reservation; §X.7 external decision artifact requirement added alongside counterfactual; §X.8 ledger extended to cover visual/structural claims with new claim-mode field, new visual-elevation type, and new violations #15-16; §X.10 hard gate added on anomaly-threshold deferral (anomaly claims do not ship pre-launch).*

*v0.1.1 amendment 2026-04-30 (post-specialist-triage, 4 surgical amendments + 1 post-Codex follow-up): §X.1 forbidden grammar item 7 (claim-of-insight framing) + audit test second sentence; §X.6 Hard rule #8 (Barnum sentences) and Hard rule #9 (closure cross-reference); §X.8 violation #17 (report-level narrative closure prevention, with Evidence-requirement clause integrating Codex T2 R1 follow-up); §X.10 Live-paid-checkout launch gate subsection; §X.11 Adjacent-doctrines line extended to name §X-Trad and §X-Legal as forthcoming, §X-Legal as hard launch-gate dependency. Source: `X_V0_1_1_SURGICAL_AMENDMENTS.md`. Audit chain: specialist triage → orchestrator draft → ChatGPT counter-critique (4 revisions) → Codex T2 R1 PASS-WITH-FOLLOWUPS (1 follow-up integrated into Amendment 2) → operator approval.*

*Status: v0.1.1 LOCKED 2026-04-30. v0.1.1 is a surgical extension of v0.1 (preserved unchanged). v0.1 audit chain: Codex T2 R2 PASS. v0.1.1 audit chain: Codex T2 R1 PASS-WITH-FOLLOWUPS, follow-up integrated into Amendment 2, no re-audit required per Codex routing recommendation. Locked for T3 (CC implementation as repo doctrine document).*
