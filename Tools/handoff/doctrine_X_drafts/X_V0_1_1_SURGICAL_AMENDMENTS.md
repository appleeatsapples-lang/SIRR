# §X v0.1.1 — Surgical Amendments

**Status:** Draft 2026-04-30 by Claude orchestrator. Revised 2026-04-30 post-ChatGPT counter-critique (4 revisions: A1 Barnum auditable-form swap, A2 closure rule load-bearing home moved to §X.8, A3 claim-of-insight synonym additions, A4 §X.10 legal-substance cleanup). Codex T2 R1 audit returned PASS-WITH-FOLLOWUPS 2026-04-30; single follow-up (§X.8 #17 rendered-surface evidence requirement) integrated into Amendment 2 per operator ruling. Awaiting operator approval to patch `SYNTHESIS_X_DRAFT.md` and lock as v0.1.1.

**Origin:** Specialist triage (`SPECIALIST_TRIAGE.md`, 2026-04-30) classified 36 findings across three independent specialists. Operator selected option C (split): patch only doctrine-breaking blockers that are genuinely §X-internal, route the rest to §X-Trad / §X-Legal / future §X v0.2.

**Relationship to v0.1 lock:** v0.1 was locked after multi-model synthesis + NotebookLM grounding + Codex T2 R1 PASS-WITH-FOLLOWUPS + Codex T2 R2 PASS. v0.1.1 is a surgical extension that does not re-open settled rules. The four amendments below add to existing sections without rewriting them.

---

## Hard scope

**In scope (this file):**

1. Spec 3 F1 — Barnum-effect rule for generated prose
2. Spec 3 F4 — report-level narrative-closure prevention
3. Spec 3 F5 — claim-of-insight framing rule
4. Spec 2 F1 — legal-disclosure pointer only

**Explicitly out of scope (route elsewhere):**

- All Spec 1 findings (12) → §X-Trad (separate doctrine arc, real-tradition-consultant gated where flagged)
- Spec 2 F2–F14 → §X-Legal (external compliance artifact, KSA-licensed-lawyer-gated)
- Spec 3 F2, F3, F6, F7, F8, F9, F10 → §X v0.2 (future psychological-safety amendments after §X-Trad locks)
- Any tradition-specific judgment, legal opinion, product/UX redesign beyond claim-framing

**Boundary rule (operator-imposed):** if any proposed amendment requires tradition-specific judgment, legal advice, or product design beyond claim-framing, it is out of scope for v0.1.1 and must be routed elsewhere. Each amendment below carries an explicit boundary check.

---

## Amendment 1 — Spec 3 F1: Barnum rule for generated prose

### Source finding

Spec 3 F1 (BLOCKING, HIGHEST-PRIORITY): "Generality-disguised-as-specificity not addressed." A sentence can pass §X.1 (no essence claim) and §X.6 (no identity verdict, no directive, no prediction) and still be Barnum — i.e., feel personally diagnostic to the customer because it applies to most people. Predictable failure mode named in the verdict: *"a reading can be §X-compliant and still feel personally diagnostic because the customer supplies the meaning."*

Specialist confidence: HIGH.

### Exact doctrine section affected

§X.6 — Generated prose, Hard rules subsection. Add as Hard rule #8 (existing rules 1–7 retained verbatim).

### Proposed text

Insert after §X.6 Hard rule #7, before "Subordination of existing constitutional rules":

> **8. No Barnum sentences.** A sentence is Barnum when it would feel specific to the customer reading it but applies to most people who would ever read a SIRR reading. Generated prose must not produce Barnum sentences regardless of whether they pass rules 1–7. The auditable form: a reviewer takes any sentence in the generated prose and asks, *"does the sentence derive its specificity from the customer's computed marks, named methods, submitted inputs, or structural features of this reading?"* If not, and the sentence would plausibly feel personally descriptive to many unrelated customers, the sentence is Barnum and §X.6 is violated.
>
> The constraint is positive, not just negative: generated prose that names a computed mark, a method, an axis, a value, or a structural feature of the customer's specific data is permitted; prose whose specificity comes from emotional or psychological generality common to most people is not.
>
> *Worked examples.*
> "Your chart returns repeated fire signatures across the Hellenistic, Vedic, and elemental axes." — passes. Specificity is computational. ✓
> "You feel pulled in two directions when others see you as decisive." — fails. Specific in feeling, general in fact; passes essence-rewrite test, fails Barnum test. ✗
> "The Bazi reading returns a Yang-Wood day-master with the lineage pattern surfacing on the maternal side." — passes. Specificity is computational. ✓
> "There is a part of you that holds back, even from people who know you well." — fails. Universal-feeling generalization. ✗

### Why this belongs in §X (not §X-Trad / §X-Legal / future §X v0.2)

§X.6 already governs what generated prose may and may not say. It has seven hard rules covering essence, directive, prediction, confidence, contradiction, sacred authority, hidden limitation. Barnum is a separate failure mode of the same surface — generated prose — and belongs structurally where the existing rules live. It is auditable yes/no per §X's audit principle. It does not require tradition-specific judgment (boundary check ✓), legal advice (boundary check ✓), or product redesign beyond claim-framing (boundary check ✓).

Routing this to §X v0.2 instead means the LLM ships generating Barnum prose in the interim, and §X.6 remains incomplete on the specialists' highest-priority finding.

### Risk if omitted

The reading clears every §X.1 and §X.6 audit and still produces felt-personal-but-actually-universal sentences. The customer experiences the system as deeply seeing them; the system has computed nothing of the sort. This is the central psychological-safety failure mode the specialists identified. Without the rule, §X.6 audits cannot detect it because the existing rules don't ask the Barnum question.

---

## Amendment 2 — Spec 3 F4: report-level narrative-closure prevention

### Source finding

Spec 3 F4 (BLOCKING if reading ends with unified synthesis): "§X.6 covers prose-level smoothing, not report-level/structural narrative closure." A reading composed of §X-compliant individual sentences may still end with a closing surface — a synthesis paragraph, an "insight summary," a final card — that converts the six computed operators into a single unified verdict about the customer. The closure is the violation, not any single sentence.

Specialist confidence: HIGH.

### Exact doctrine section affected

Two coordinated touches (load-bearing home moved from §X.6 to §X.8 per ChatGPT counter-critique):

1. **§X.8 — The claims ledger, violation list.** Add as new violation #17 (existing 1–16 retained verbatim). This is the load-bearing home: closure can be produced by prose, template, visual hierarchy, summary card, share asset, screenshot composition, or any structurally equivalent surface — making it a visual/structural claim under §X.8's existing scope. The earlier draft placed this rule in §X.6, but the failure mode is structural rather than text-only; §X.8 is the correct doctrinal home.
2. **§X.6 — Generated prose, Hard rules subsection.** Add as Hard rule #9 (after Amendment 1's new rule #8) — but only as a brief cross-reference redirecting to §X.8 #17. The operative rule lives in §X.8.

### Proposed text

**(a) Insert in §X.8 violation list as new violation #17 (after the existing #16):**

> 17. The reading as a whole produces closure that reduces the six operators of §X.3 to a single unified verdict about the customer. The closure may be produced by prose (LLM-generated paragraph, "summary," "what this means," "your reading in one line"), by template (final hero card synthesizing the operators, share image with a single archetype label, sticky summary block, default-expanded summary panel), by visual hierarchy (an "Insight" or "Verdict" section dominating the layout regardless of position), or by any structurally equivalent surface anywhere in the rendered reading — beginning, middle, end, or share asset. The closure is the violation, not its position. A surface that names the operators, restates that they disagreed where they disagreed, and hands the reading back to the customer is permitted. A surface that integrates them into a single statement about who the customer is, is not.
>
> Report-level closure is the report-scale form of the identity-verdict prohibition (§X.1) and the no-smoothing-of-contradiction rule (§X.6 rule 5), applied at the surface level §X.8 already governs. The architectural commitment in §X.3 (no operator as headline) and the visual re-elevation rule in §X.8 violation #15 apply jointly: closure may not be re-introduced through prose, layout, template, or share surface.
>
> The auditable form: a reviewer scans the entire rendered reading — top, body, closing, hero cards, summary blocks, share assets, default-expanded panels, screenshot composition — and asks, *"does any single surface tell the customer what the reading means as one integrated statement about them?"* If yes, §X is violated under §X.8 #17. Position is not a defence: a closure surface in the first 20% of the reading violates as fully as one in the last.
>
> *Permitted patterns.* "These are the marks the reading produced. They agree here, they disagree there, they are quiet on this axis. The reading is yours to hold." — names the operators, holds the tension, hands back. ✓
>
> *Forbidden patterns.* "Across all six operators, the reading reveals…" / "What this all comes down to is…" / "Your reading in one sentence:…" / a final hero card that synthesizes the six operators into a single archetype, name, or verdict / a sticky-summary block at the top of the reading that does the same / a share-image with a single integrated label / a "Verdict" or "Synthesis" panel that dominates the layout. ✗
>
> *Evidence requirement (added post-Codex-T2-R1 follow-up).* For any PR or surface change that adds, removes, reorders, expands, collapses, summarizes, screenshots, exports, or otherwise modifies a claim-bearing reading surface, the §X.8 claims ledger must include a rendered-surface evidence reference sufficient for review: rendered HTML, screenshot, fixture output, share asset, PDF/export artifact, or equivalent representative artifact. If the surface is data-conditioned, the evidence must include at least one representative fixture that triggers the condition. Code/templates alone are not sufficient evidence for §X.8 #17 compliance.

**(b) Insert in §X.6 Hard rules as new rule #9 (after Amendment 1's rule #8):**

> **9. Closure cross-reference.** Generated prose must also obey the report-level closure prohibition in §X.8 #17. A prose paragraph that integrates the six operators into a single statement about the customer violates §X.8 #17 regardless of where it appears in the reading; it also violates §X.6 because it is generated prose making an identity claim §X.6 rule 1 forbids.

### Why this belongs in §X (not §X-Trad / §X-Legal / future §X v0.2)

§X.8 already owns the principle that claims are made through visual/structural prominence, not just words — it covers section ordering, badge placement, hierarchy, screenshot composition, "primary" labels. Closure surfaces are exactly the kind of structural claim §X.8 was extended to cover at T2 R1. §X.3 supplies the architectural basis (no operator as headline) and §X.6 retains a cross-reference because closure can also be produced by generated prose. The load-bearing rule belongs in §X.8 because the failure mode is structural, not text-only.

Boundary check: tradition-specific judgment ✗ — it's about claim-shape, not tradition. Legal advice ✗ — it's not a regulatory rule. Product redesign beyond claim-framing ✗ — it constrains what closure surfaces may say or imply, not how the reading is laid out otherwise.

Routing this to §X v0.2 means readings ship with surface-level closures that no §X rule formally catches, even though every individual sentence may be §X.6-compliant.

### Risk if omitted

The most predictable shape of the failure: an LLM-generated final paragraph that reads "Across these six lenses, what emerges is a portrait of someone who…" — Barnum at report scale, identity-verdict at report scale, headline-elevation at report scale, all in one closing surface. Each individual sentence may pass §X.6 rules 1–8. The reading still tells the customer who they are. Without §X.8 #17, the §X audit cannot reject the closure — and the failure can also appear at the top of the reading, in a sidebar, or in a share image, none of which a prose-only rule would cover.

---

## Amendment 3 — Spec 3 F5: claim-of-insight framing rule

### Source finding

Spec 3 F5 (BLOCKING for landing/checkout/hero): "No rule against claim-of-insight / self-knowledge-delivered." §X.1 forbids "SIRR sees you," "SIRR knows who you are," "SIRR identifies the customer's destiny / rank / calling / hidden nature / spiritual status / role." It does not forbid framings in which SIRR or the reading is positioned as the *deliverer of self-knowledge, self-discovery, hidden truths about the customer, or insight into the customer*. The marketing-funnel surfaces (landing, checkout, hero, post-payment confirmation, social copy) are where this framing reliably appears.

Specialist confidence: HIGH.

### Exact doctrine section affected

§X.1 — What SIRR is and what SIRR claims. Forbidden claim grammar subsection. Add as forbidden item 7 (existing items 1–6 retained verbatim). The audit test in §X.1 is extended by one sentence to cover the new item.

### Proposed text

Insert as forbidden grammar item 7 (after existing item 6):

> 7. **Any framing in which SIRR or the reading is the deliverer of self-knowledge, self-discovery, hidden truths about the customer, or insight into the customer.** The reading may be a structured mirror, an instrument, a comparison across symbolic methods (per the affirmative claim above). It may not be the source from which the customer learns who they are. "Discover what the symbolic systems say about you" is forbidden. "See what the system reveals about your hidden nature" is forbidden. "Get insight into who you really are" is forbidden. The forbidden frame is *system-as-revealer-of-self*, regardless of whether the verb is "discover," "reveal," "show," "uncover," "expose," "illuminate," or any synonym. The same prohibition applies to noun-phrase evasions such as "personal truth," "inner truth," "true self," or "who you really are" — phrases that frame the reading as the source of an unstated self.

Extend the §X.1 audit test (after the existing "Replace the subject of any customer-facing sentence with 'the engine's computation'" sentence, before the worked examples):

> A second test applies to the new forbidden item 7. For any customer-facing sentence whose grammatical structure is *"\<system\> \<verb\> \<self-knowledge\> \<to / about / of\> \<customer\>,"* check whether the verb implies the system is the source of the knowledge. If yes, the sentence violates §X.1 forbidden item 7 even if it passes the first audit test. *"The reading reveals patterns in your data" — passes (data, not self). "The reading reveals who you are" — fails. "SIRR shows you the agreements across methods" — passes (agreements, not self). "SIRR shows you yourself" — fails.*

### Why this belongs in §X (not §X-Trad / §X-Legal / future §X v0.2)

§X.1 already governs the affirmative claim and the forbidden grammar. The new forbidden item is a strict extension of items 1–6: items 1, 2, 3 cover the system-claims-about-customer's-essence axis; the new item 7 covers the system-as-source-of-self-knowledge axis. Same surface (every customer-facing surface), same auditable form, same audit test pattern.

Boundary check: tradition-specific judgment ✗ — about claim-frame, not tradition. Legal advice ✗ — not a disclosure rule. Product redesign beyond claim-framing ✗ — directly about claim-framing, which is the §X scope.

Routing this to §X v0.2 means the marketing funnel ships with insight-framing copy that contradicts the §X.1 affirmative claim ("a structured mirror; an instrument the customer uses to ask questions of themselves") even as the reading-page copy complies.

### Risk if omitted

The reading itself may be §X.6-compliant; the surfaces *around* the reading sell self-knowledge. The customer arrives at the reading already framed to expect insight, then mentally supplies the insight (per the Barnum and confirmation-bias dynamics named in Spec 3). The §X audit catches the reading and misses the funnel. The marketing-funnel surfaces are exactly where Spec 3 named this failure mode as blocking.

---

## Amendment 4 — Spec 2 F1: legal-disclosure pointer only

### Source finding

Spec 2 F1 (BLOCKING pre-launch for any paid flow): "Denials need legal classification (ad / contract / safety) and pre-payment placement." Currently §X.2's denials are required to appear in customer-readable language inside the reading body. Inside-the-reading is post-payment. For a paid flow, the legal exposure (FTC-equivalents, KSA Anti-Cyber Crime, KSA e-commerce, refund/chargeback) requires those denials — or substantively equivalent disclosures — to appear *pre-payment*. §X v0.1 has no rule about pre-payment disclosure placement.

Specialist confidence: HIGH (on FTC/disclosure/refund/GDPR-minors). LOW (on KSA-specific legal treatment) — Spec 2 explicitly flagged that resolving this requires a Saudi-licensed lawyer.

### Exact doctrine section affected

Two minimal touches:

1. §X.10 — Deferrals, monitoring, amendment. Add a new launch-gate subsection between "Items §X explicitly defers" and "Monitoring cadence."
2. §X.11 — Doctrine version, ownership, dependencies. Extend the "Adjacent doctrines" line to mention §X-Legal as required-but-not-yet-existing.

### Proposed text

**(a) Insert in §X.10 as a new subsection, between "Items §X explicitly defers" and "Monitoring cadence":**

> ### Live-paid-checkout launch gate
>
> §X governs claim language. It does not govern legal disclosures, refund terms, jurisdictional compliance, minors handling, bilingual legal parity, or transaction terms. Those domains belong to a separate lawyer-authored doctrine, §X-Legal. Until §X-Legal exists in approved form, no §X-governed surface may be activated in live paid checkout or paid post-payment delivery. Static informational surfaces, sample readings, and test-mode flows may proceed under §X audit alone. This is a §X self-restraint, not legal advice and not a substitute for counsel.

**(b) Replace the §X.11 "Adjacent doctrines" line with:**

> - **Adjacent doctrines:** §13 (privacy) governs PII handling; §X (this) governs claim language; §X-Trad (forthcoming) will govern source-tradition relations; §X-Legal (forthcoming, lawyer-authored) will govern legal disclosures, refund terms, jurisdictional compliance, minors handling, bilingual legal parity, and transaction terms. Where any two could conflict on overlapping ground, the doctrine whose primary jurisdiction the conflict falls under wins, and the other amends to accommodate. §X-Legal is a hard launch-gate dependency for live paid checkout per §X.10.

### Why this belongs in §X (not §X-Trad / §X-Legal / future §X v0.2)

The amendment is *strictly* a self-imposed launch gate authored from inside §X. It does not author §X-Legal content. It does not specify what disclosures must say, where exactly they must appear pre-payment, or what refund framework is correct. Those are lawyer questions, lawyer-authored, in §X-Legal.

What the amendment does is internal to §X: it commits §X to refuse activation of §X-governed surfaces into a paid flow without the adjacent doctrine present. That commitment is a claim-doctrine decision (§X surfaces cannot pretend to be sufficient for live commerce alone), not a legal opinion. It belongs in §X because §X is the doctrine being constrained by it.

Boundary check: tradition-specific judgment ✗. Legal advice ✗ — explicitly defers all substantive legal content to a lawyer-authored §X-Legal. Product redesign beyond claim-framing ✗ — does not specify checkout flow, only refuses activation of §X surfaces into one without the adjacent doctrine.

Routing this to §X-Legal directly is incoherent: §X-Legal does not exist, will not exist until a lawyer authors it, and even when it does exist it cannot impose a self-restraint on §X — only §X can. Routing to v0.2 means the launch gate is unwritten while paid checkout is being prepared.

### Risk if omitted

§X v0.1.1 ships, the four §X-internal psychological-safety amendments harden the claim-doctrine, and the path to live paid checkout has no §X-internal speed bump for the missing legal-disclosure framework. The operator activates Lemon Squeezy live mode (currently blocked on National ID back-side, per memory — the gate is operationally live within weeks), and §X surfaces enter paid commerce without §X-Legal in place. Spec 2 F1 named this as the central pre-launch consumer-protection failure mode. Without an internal launch gate referencing it, the §X audit cannot block the activation.

---

## How the four amendments interact

Amendments 1, 2, 3 harden customer-claim safety in three different surfaces:

- Amendment 1 (Barnum) → at the sentence level inside generated prose
- Amendment 2 (no closure synthesis) → at the report level across all surfaces
- Amendment 3 (no insight framing) → at the marketing-funnel level around the reading

Together they close the gap the verdict named: *"§X is engineering-robust and claims-robust, not yet psychologically robust."* They do not make §X psychologically *complete* — that is §X v0.2's scope — but they patch the three failure modes the specialist classified as BLOCKING and structurally §X-internal.

Amendment 4 (legal-disclosure pointer) is operationally orthogonal: it does not change what §X surfaces say, it changes when they may go live.

No amendment requires re-auditing v0.1's existing rules. Each is additive, with cross-references to existing rules where applicable. The synthesis quality earned at v0.1 lock is preserved.

---

## Audit chain expected before lock

Per operator-imposed required process (and per LANE_DOCTRINE: solo authority on doctrine is the failure mode):

1. **ChatGPT counter-draft or critique** on the four proposed amendments. Specifically: does any amendment over-reach beyond claim-framing into product/tradition/legal scope? Does any proposed text contradict an existing §X v0.1 rule? Is any rule unauditable per §X's yes/no audit principle?
2. **Codex-style audit** on the four amendments and their cross-section integration. Specifically: §X.1 forbidden item 7 cross-references; §X.6 rules 8–9 cross-references; §X.10 launch gate / §X.11 adjacent doctrine alignment; no regression on existing T2 R1 amendments (§X.1 prestige leak, §X.7 external decision artifact, §X.8 visual coverage, §X.10 anomaly hard gate).
3. **Operator approval** on the audited amendments (with any audit-driven revisions integrated).
4. **Patch `SYNTHESIS_X_DRAFT.md`** with the approved amendments in place. Update the trailing version footer to v0.1.1 LOCKED and append amendment list to the existing T2 R1 amendment record.
5. **Update `LOCK_RECORD.md`** with the v0.1.1 audit trail row(s).

Only after step 4 does v0.1.1 exist as a locked artifact. Until then, this file is a proposal, not doctrine.

---

## Out-of-scope inventory (routing record)

For audit-trail completeness, the findings deferred from this surgical patch and their routing destination:

| Finding | Specialist | Routing | Reason |
|---|---|---|---|
| F1–F12 | Spec 1 (religious ethics) | §X-Trad doctrine arc | Tradition-specific judgment, not §X claim-framing |
| F2 (backward-remediation) | Spec 2 | §X-Legal | Legal-doctrine territory |
| F3 (refund/chargeback) | Spec 2 | §X-Legal | Legal-doctrine territory |
| F4 (KSA Anti-Cyber Crime) | Spec 2 | §X-Legal | KSA-licensed-lawyer-gated |
| F5 (KSA prohibited claims) | Spec 2 | §X-Legal | KSA-licensed-lawyer-gated |
| F6 (authoritative-language) | Spec 2 | §X-Legal | Bilingual legal parity, lawyer-gated |
| F7 (reliance-risk) | Spec 2 | §X-Legal / §X v0.2 | Disclaimer-paradox overlap; defer until §X v0.2 |
| F8 (minors rule) | Spec 2 | §X-Legal | Legal-doctrine territory |
| F9 (pre-payment denial placement) | Spec 2 | §X-Legal (substance); §X v0.1.1 Amendment 4 references the gate | Substantive rule is lawyer-authored; the gate is §X-internal |
| F10 (entertainment-only matrix) | Spec 2 | §X-Legal | Jurisdictional, lawyer-gated |
| F11 (legal evidence trail) | Spec 2 | §X-Legal | Legal-doctrine territory |
| F12 (PDPL cross-reference) | Spec 2 | §X-Legal / §13 | Privacy + legal overlap |
| F13 (LLM regression testing) | Spec 2 | Engineering arc | Product/QA, not doctrine |
| F14 (market segmentation) | Spec 2 | Business decision | Operator-level, not doctrine |
| F2 (Barnum-gradient) | Spec 3 | §X v0.2 | Gradient beyond binary Barnum rule; second-pass refinement |
| F3 (testimonials) | Spec 3 | §X v0.2 | Marketing-evidence rule; not yet claim-framing scope |
| F6 (disclaimer-paradox) | Spec 3 | §X v0.2 | Acknowledgment-of-limitation amendment; medium-confidence |
| F7 (visual saturation) | Spec 3 | §X v0.2 | Product/UX surface design; partly claim-framing, partly UI |
| F8 (stopping rules) | Spec 3 | Post-launch | Design-evolution; only blocking if subscription/recurring features added |
| F9 (external reviewer for §X.7) | Spec 3 | §X v0.2 | Recursion-bias second-order amendment |
| F10 (customer-pressure refusal) | Spec 3 | §X v0.2 | Support-copy rule; partly claim-framing, partly operations |

Total findings handled or routed: 36/36.
- Patched in v0.1.1: 4
- Routed to §X-Trad: 12
- Routed to §X-Legal: 11
- Routed to §X v0.2: 7
- Routed to engineering / business / post-launch: 2

---

*Drafted 2026-04-30 by Claude orchestrator. Revised 2026-04-30 post-ChatGPT counter-critique (4 revisions: A1 Barnum auditable-form swap; A2 closure rule load-bearing home moved to §X.8 with §X.6 cross-reference and broadened audit form past final-20% loophole; A3 claim-of-insight synonym additions for noun-phrase evasions; A4 §X.10 launch-gate subsection cleanup to remove legal-substance phrasing; §X.11 adjacent-doctrines line aligned to A4 phrasing for internal consistency). Codex T2 R1 audit 2026-04-30 returned PASS-WITH-FOLLOWUPS with one finding (§X.8 #17 auditability of data-conditioned rendered surfaces); follow-up integrated into Amendment 2 §X.8 #17 proposed text as an Evidence-requirement clause per operator ruling that the doctrine must first state the evidence requirement before LANE_DOCTRINE can mechanically enforce it. §X.6 #9 cross-reference unchanged — it inherits the evidence requirement transitively via its redirect to §X.8 #17. F2 (Barnum-gradient) and F3 (testimonials, grep-confirmed clean 2026-04-30) remain deferred to §X v0.2. Awaiting operator approval to patch `SYNTHESIS_X_DRAFT.md` and lock as v0.1.1; no Codex re-audit needed per Codex's routing recommendation (follow-up scope stays inside rendered-artifact coverage).*
