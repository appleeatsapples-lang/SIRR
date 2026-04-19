"""
SIRR Unified View Renderer
==========================
Produces the product-surface HTML for a single profile.
Takes the enriched output dict from server.py _enrich_output (with unified_filter=True)
and returns a self-contained HTML string.

Aesthetic: editorial-archival. Cream background, warm near-black text, rust accent.
Instrument Serif display + Newsreader body + JetBrains Mono for data.

This is deliberately distinct from the v12.1 artifact (legacy showcase), which is
dark/glassmorphic/obsidian. The product surface and the showcase are different
visual worlds.
"""
from __future__ import annotations
from typing import Dict, Any, List
import html as htmllib

# Shared presentation filter — canonical source of display logic.
# unified_view re-exports the symbols it uses so existing callers don't break.
from presentation import (
    HIDE_EXACT_VALUES as _HIDE_EXACT_VALUES,
    ALWAYS_HIDE_IDS as _ALWAYS_HIDE_IDS,
    ID_LABEL_REWRITES as _ID_LABEL_REWRITES,
    ID_VALUE_BUILDERS as _ID_VALUE_BUILDERS,
    REWRITE_RULES as _REWRITE_RULES,
    PATTERN_DOMAIN_REWRITES as _PATTERN_DOMAIN_REWRITES,
    META_SKIP,
    clean_value as _clean_value,
    _is_name_echo,
    format_primary_value as _format_value,
    resolve_display as _resolve_display,
)


# ── Domain display metadata ──

DOMAIN_LABELS = {
    "numerology": "Numerology",
    "name_intelligence": "Name Intelligence",
    "astro_timing": "Astro Timing",
    "convergence": "Convergence",
}

DOMAIN_SUBTITLES = {
    "numerology": "birth + name as numeric structure",
    "name_intelligence": "your name read through multiple letter-value systems + Arabic linguistics",
    "astro_timing": "real ephemeris · when things activate",
    "convergence": "where independent families agree",
}

DOMAIN_ORDER = ["numerology", "name_intelligence", "astro_timing", "convergence"]


def _esc(s) -> str:
    """HTML-escape a value, safely handle None."""
    if s is None:
        return ""
    return htmllib.escape(str(s))



# All presentation filter symbols are now imported from presentation.py above.
# Local aliases preserved for backward compatibility with existing callers.



# ── CSS tokens (inline for single-file HTML) ──

CSS = """
:root {
  --bg: #f5f1ea;
  --bg-alt: #ebe4d5;
  --bg-deep: #e3dbc8;
  --fg: #1a1814;
  --fg-soft: #3d3831;
  --muted: #8a8178;
  --muted-faint: #b5ac9f;
  --accent: #a8482d;
  --accent-soft: #c77a4a;
  --line: rgba(26, 24, 20, 0.12);
  --line-strong: rgba(26, 24, 20, 0.25);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html { background: var(--bg); }

body {
  background: var(--bg);
  color: var(--fg);
  font-family: 'Newsreader', Georgia, 'Times New Roman', serif;
  font-weight: 300;
  line-height: 1.6;
  font-size: 17px;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.container {
  max-width: 920px;
  margin: 0 auto;
  padding: 56px 48px 120px;
}

@media (max-width: 720px) {
  .container { padding: 32px 24px 80px; }
}

/* ─── Typography primitives ─── */

.display {
  font-family: 'Instrument Serif', 'Newsreader', Georgia, serif;
  font-weight: 400;
  letter-spacing: -0.01em;
}

.mono {
  font-family: 'JetBrains Mono', ui-monospace, 'SF Mono', monospace;
  font-weight: 400;
}

.smallcap {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-size: 10px;
  color: var(--muted);
  font-weight: 500;
}
"""


CSS += """
/* ─── Header ─── */

header {
  border-bottom: 1px solid var(--line);
  padding-bottom: 20px;
  margin-bottom: 80px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
  flex-wrap: wrap;
}

header .brand {
  font-family: 'Instrument Serif', serif;
  font-size: 28px;
  line-height: 1;
  color: var(--fg);
}

header .brand .ar {
  margin-right: 12px;
  color: var(--accent);
}

header .meta {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  line-height: 1.65;
  color: var(--muted);
  text-align: right;
  letter-spacing: 0.03em;
}

header .meta strong {
  color: var(--fg);
  font-weight: 500;
}

/* ─── Coherence hero ─── */

.coherence {
  display: grid;
  grid-template-columns: minmax(0, 340px) minmax(0, 1fr);
  gap: 64px;
  margin-bottom: 96px;
  padding-bottom: 72px;
  border-bottom: 1px solid var(--line);
  align-items: start;
}

@media (max-width: 720px) {
  .coherence { grid-template-columns: 1fr; gap: 32px; }
}

.coherence .score-block {
  position: relative;
}

.coherence .score-number {
  font-family: 'Instrument Serif', serif;
  font-size: clamp(140px, 22vw, 220px);
  line-height: 0.85;
  font-weight: 400;
  color: var(--accent);
  letter-spacing: -0.06em;
  margin-left: -10px;
  margin-top: 12px;
}

.coherence .score-tier-tag {
  position: absolute;
  top: 8px;
  right: 0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.18em;
}
"""


CSS += """
.coherence .detail {
  padding-top: 20px;
}

.coherence .score-label {
  font-family: 'Instrument Serif', serif;
  font-size: 40px;
  font-style: italic;
  color: var(--fg);
  line-height: 1.15;
  margin-bottom: 20px;
}

.coherence .blurb {
  font-family: 'Newsreader', serif;
  font-size: 16px;
  color: var(--fg-soft);
  line-height: 1.65;
  max-width: 440px;
  margin-bottom: 32px;
}

.coherence .score-components {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--muted);
  border-top: 1px solid var(--line);
  padding-top: 16px;
  display: grid;
  gap: 5px;
  letter-spacing: 0.02em;
}

.coherence .score-components span.val {
  color: var(--fg);
}

/* ─── Tension pull quote ─── */

.tension {
  margin: 0 0 96px;
  padding: 56px 56px 56px 40px;
  background: var(--bg-alt);
  border-left: 2px solid var(--accent);
  position: relative;
}

.tension::before {
  content: "\\201C";
  position: absolute;
  left: 20px;
  top: -8px;
  font-family: 'Instrument Serif', serif;
  font-size: 120px;
  color: var(--accent);
  opacity: 0.22;
  line-height: 1;
}

.tension .label {
  margin-bottom: 16px;
}

.tension .sentence {
  font-family: 'Instrument Serif', serif;
  font-size: clamp(22px, 3.6vw, 30px);
  font-style: italic;
  line-height: 1.35;
  color: var(--fg);
  letter-spacing: -0.005em;
}

.tension.aligned {
  border-left-color: var(--muted);
}

.tension.aligned::before {
  color: var(--muted);
}
"""


CSS += """
/* ─── Domain sections ─── */

.domain {
  margin-bottom: 80px;
}

.domain-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 28px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 12px;
}

.domain-header h2 {
  font-family: 'Instrument Serif', serif;
  font-weight: 400;
  font-size: 30px;
  color: var(--fg);
  letter-spacing: -0.01em;
}

.domain-header .subtitle {
  font-family: 'Newsreader', serif;
  font-size: 14px;
  font-style: italic;
  color: var(--muted);
  margin-top: 4px;
}

.domain-header .count {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  white-space: nowrap;
}

.domain table {
  width: 100%;
  border-collapse: collapse;
}

.domain td {
  padding: 13px 12px 13px 0;
  border-bottom: 1px solid var(--line);
  vertical-align: baseline;
  font-size: 15px;
}

.domain tr:last-child td {
  border-bottom: none;
}

.domain td.name {
  font-family: 'Newsreader', serif;
  font-weight: 400;
  color: var(--fg);
  letter-spacing: 0.005em;
}

.domain td.value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--accent);
  text-align: right;
  white-space: nowrap;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.domain-empty {
  font-family: 'Newsreader', serif;
  font-style: italic;
  color: var(--muted);
  font-size: 14px;
  padding: 12px 0;
}

/* Signal preamble — sits above the first domain section to frame the
   structural-signal nature of the rows that follow. */
.signal-preamble {
  margin: -48px 0 64px;
  padding: 0;
  max-width: 600px;
}
.signal-preamble p {
  font-family: 'Newsreader', serif;
  font-style: italic;
  font-size: 15px;
  line-height: 1.7;
  color: var(--muted);
}
"""


CSS += """
/* ─── Convergences section ─── */

.convergences {
  margin: 96px -32px 80px;
  padding: 48px 32px;
  background: var(--bg-deep);
  border-radius: 2px;
}

.convergences .label {
  margin-bottom: 12px;
}

.convergences .conv-intro {
  font-family: 'Newsreader', serif;
  font-style: italic;
  font-weight: 300;
  font-size: 13.5px;
  line-height: 1.7;
  color: var(--muted);
  max-width: 620px;
  margin-bottom: 24px;
}

.conv-list {
  display: grid;
  gap: 0;
}

.conv-item {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr) auto;
  gap: 28px;
  padding: 20px 0;
  border-bottom: 1px solid var(--line);
  align-items: baseline;
}

.conv-item:last-child {
  border-bottom: none;
}

.conv-item .num {
  font-family: 'Instrument Serif', serif;
  font-size: 54px;
  color: var(--accent);
  line-height: 0.9;
  letter-spacing: -0.04em;
}

.conv-item .detail-block {
  font-family: 'Newsreader', serif;
}

.conv-item .detail-block .headline {
  font-size: 16px;
  color: var(--fg);
  margin-bottom: 4px;
}

.conv-item .detail-block .systems {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--muted);
  line-height: 1.6;
  letter-spacing: 0.02em;
}

.conv-item .stats {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  text-align: right;
  white-space: nowrap;
}

.conv-item .stats .pct {
  color: var(--accent);
  display: block;
  font-size: 11px;
  margin-top: 4px;
}

/* ─── Footer ─── */

footer {
  margin-top: 120px;
  padding-top: 32px;
  border-top: 1px solid var(--line);
  font-family: 'JetBrains Mono', monospace;
  font-size: 9.5px;
  color: var(--muted);
  text-align: center;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  line-height: 1.8;
}

footer a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid var(--line);
}

footer a:hover {
  border-bottom-color: var(--accent);
}

/* ─── Row interpretation disclosure (expandable rows) ─────────────
   Rows with engine-provided interpretation text become <details> elements.
   Closed state is visually indistinguishable from the current table row;
   open state reveals a full-width subordinate panel beneath.

   Design intent per locked spec:
   - summary row looks almost identical to a regular <tr>
   - affordance subtle but clear (faint caret, soft hover)
   - open panel is typographically quieter than the row itself
   - editorial, not app-accordion
*/

.domain details.row {
  border-bottom: 1px solid var(--line);
}

.domain details.row[open] {
  background: var(--bg-alt);
}

.domain details.row > summary {
  display: grid;
  grid-template-columns: 1fr auto 16px;
  gap: 12px;
  padding: 13px 12px 13px 0;
  cursor: pointer;
  list-style: none;
  vertical-align: baseline;
  align-items: baseline;
  transition: background 120ms ease;
}

.domain details.row > summary::-webkit-details-marker { display: none; }

.domain details.row > summary:hover {
  background: var(--bg-alt);
}

.domain details.row > summary .name {
  font-family: 'Newsreader', serif;
  font-weight: 400;
  color: var(--fg);
  letter-spacing: 0.005em;
  font-size: 15px;
}

.domain details.row > summary .value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--accent);
  text-align: right;
  white-space: nowrap;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.domain details.row > summary .caret {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--muted-faint);
  text-align: right;
  transition: transform 160ms ease, color 160ms ease;
  user-select: none;
  line-height: 1.4;
}

.domain details.row[open] > summary .caret {
  transform: rotate(90deg);
  color: var(--accent);
}

.domain details.row > .interp-panel {
  padding: 4px 24px 20px 24px;
  margin: 0;
  font-family: 'Newsreader', serif;
  font-weight: 300;
  font-size: 14px;
  line-height: 1.7;
  color: var(--fg-soft);
  max-width: 680px;
}

/* Non-expandable rows (no interpretation) still render as plain rows.
   They share summary-row geometry but do not carry the disclosure affordance. */
.domain .plain-row {
  display: grid;
  grid-template-columns: 1fr auto 16px;
  gap: 12px;
  padding: 13px 12px 13px 0;
  border-bottom: 1px solid var(--line);
  align-items: baseline;
}

.domain .plain-row .name {
  font-family: 'Newsreader', serif;
  font-weight: 400;
  color: var(--fg);
  font-size: 15px;
}

.domain .plain-row .value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--accent);
  text-align: right;
  white-space: nowrap;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.domain .plain-row .caret-placeholder {
  /* Keeps column alignment with expandable rows. */
}

/* Signal-preamble second sentence — orientation only. Same subdued voice
   as the first sentence; a single semicolon-separated clause would feel
   pinched, so we use a short follow-on sentence instead. */
.signal-preamble p + p {
  margin-top: 8px;
}

/* ─── Synthesis layer (synthesis-first patch 2026-04-17) ─────────
   The reading is the product. The module catalog is the receipts.
   These blocks sit above the evidence layer and carry the primary
   buyer-facing synthesis. All content comes from existing structured
   engine output — no invented prose in the renderer. */

.portrait {
  margin: 0 0 64px;
  padding: 0;
  max-width: 640px;
}

.portrait .label {
  margin-bottom: 20px;
}

.portrait .axis-line {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.08em;
  margin-bottom: 24px;
  line-height: 1.6;
}

.portrait .axis-line strong {
  color: var(--fg);
  font-weight: 500;
  letter-spacing: 0.04em;
}

.portrait .descriptor {
  font-family: 'Instrument Serif', serif;
  font-size: clamp(22px, 3.2vw, 28px);
  font-style: italic;
  line-height: 1.35;
  color: var(--fg);
  margin-bottom: 24px;
  letter-spacing: -0.005em;
}

.portrait .reading {
  font-family: 'Newsreader', serif;
  font-weight: 300;
  font-size: 17px;
  line-height: 1.7;
  color: var(--fg-soft);
}

/* ─── Hierarchy triangle (single synthesis visual) ─────────────
   Shows the three anchor numbers and their relationship:
   synthesis at top, birth bottom-left, name bottom-right.
   Triangles for portrait. Squares for proof. */

.portrait .hierarchy {
  margin: 28px 0 28px;
  padding: 24px 0;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  max-width: 540px;
}

.portrait .hierarchy-svg {
  display: block;
  width: 100%;
  max-width: 460px;
  height: auto;
  margin: 0 auto 18px;
}

.portrait .hierarchy .h-link {
  stroke: var(--line-strong);
  stroke-width: 1;
  fill: none;
}

.portrait .hierarchy .h-link-base {
  stroke-dasharray: 3 4;
  opacity: 0.6;
}

.portrait .hierarchy .h-node {
  stroke: var(--line-strong);
  stroke-width: 1;
  fill: var(--bg);
}

.portrait .hierarchy .h-synth {
  fill: var(--bg-alt);
  stroke: var(--accent);
  stroke-width: 1.5;
}

.portrait .hierarchy .h-num {
  font-family: 'Instrument Serif', serif;
  font-weight: 400;
  fill: var(--fg);
  letter-spacing: -0.02em;
}

.portrait .hierarchy .h-num-synth {
  font-size: 36px;
  fill: var(--accent);
}

.portrait .hierarchy .h-num-axis {
  font-size: 22px;
}

.portrait .hierarchy .h-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 500;
  fill: var(--muted);
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.portrait .hierarchy-caption {
  font-family: 'Newsreader', serif;
  font-style: italic;
  font-weight: 300;
  font-size: 14px;
  line-height: 1.7;
  color: var(--fg-soft);
  max-width: 520px;
  margin: 0 auto;
  text-align: center;
}

.portrait .hierarchy-caption strong {
  font-style: normal;
  font-weight: 500;
  color: var(--accent);
}

@media (max-width: 560px) {
  .portrait .hierarchy-svg { max-width: 100%; }
  .portrait .hierarchy-caption { font-size: 13px; text-align: left; }
}

/* Demoted coherence — sits under the portrait as a small metric, not a hero */
.coherence-stat {
  margin: 0 0 72px;
  padding: 14px 0;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: baseline;
  gap: 20px;
  flex-wrap: wrap;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  color: var(--muted);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.coherence-stat .score {
  font-family: 'Instrument Serif', serif;
  font-size: 22px;
  color: var(--accent);
  letter-spacing: 0;
  text-transform: none;
  font-style: normal;
}

.coherence-stat .lbl {
  font-family: 'Newsreader', serif;
  font-size: 13px;
  font-style: italic;
  color: var(--fg-soft);
  letter-spacing: 0;
  text-transform: none;
}

.coherence-stat .arch {
  margin-left: auto;
  color: var(--muted-faint);
  font-size: 10px;
}

/* Patterns detected — each pattern is a quiet block, not a card */
.patterns {
  margin: 0 0 72px;
}

.patterns .label {
  margin-bottom: 24px;
}

.patterns .pattern {
  padding: 20px 0;
  border-bottom: 1px solid var(--line);
}

.patterns .pattern:last-child {
  border-bottom: none;
}

.patterns .pattern .name {
  font-family: 'Instrument Serif', serif;
  font-size: 22px;
  color: var(--fg);
  margin-bottom: 4px;
  letter-spacing: -0.01em;
}

.patterns .pattern .domain {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  margin-bottom: 10px;
}

.patterns .pattern .descriptor {
  font-family: 'Newsreader', serif;
  font-weight: 300;
  font-size: 15px;
  line-height: 1.7;
  color: var(--fg-soft);
  margin-bottom: 10px;
  max-width: 680px;
}

.patterns .pattern .lineage {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9.5px;
  color: var(--muted-faint);
  letter-spacing: 0.04em;
  line-height: 1.6;
}

/* Civilizational theses — three quiet columns, stack below 720px */
.theses {
  margin: 0 0 72px;
}

.theses .label {
  margin-bottom: 24px;
}

.theses .grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 32px;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: 24px 0;
}

@media (max-width: 720px) {
  .theses .grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .theses .grid > div:not(:last-child) {
    padding-bottom: 24px;
    border-bottom: 1px solid var(--line);
  }
}

.theses .thesis .tradition {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.18em;
  margin-bottom: 10px;
}

.theses .thesis .frame {
  font-family: 'Newsreader', serif;
  font-style: italic;
  font-size: 15px;
  line-height: 1.55;
  color: var(--fg);
  margin-bottom: 10px;
}

.theses .thesis .signal {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.04em;
  line-height: 1.6;
}

/* Evidence-layer intro — replaces the old signal-preamble framing */
.evidence-intro {
  margin: 96px 0 48px;
  padding-top: 32px;
  border-top: 1px solid var(--line);
  max-width: 640px;
}

.evidence-intro .label {
  margin-bottom: 16px;
}

.evidence-intro p {
  font-family: 'Newsreader', serif;
  font-style: italic;
  font-size: 15px;
  line-height: 1.7;
  color: var(--muted);
}

.evidence-intro p + p {
  margin-top: 8px;
}
"""



# ── Render functions ──

def render_header(profile: Dict[str, Any]) -> str:
    subject = _esc(profile.get("subject", "")).title()
    dob = _esc(profile.get("dob", ""))
    location = _esc(profile.get("location", ""))
    today = _esc(profile.get("today", ""))

    return f"""
    <header>
      <div class="brand"><span class="ar">سِرّ</span>SIRR</div>
      <div class="meta">
        <strong>{subject}</strong><br>
        {dob}{' · ' + location if location else ''}<br>
        Computed {today}
      </div>
    </header>
    """


def render_coherence(unified: Dict[str, Any]) -> str:
    """Demoted coherence — small stat-line under the portrait.

    Synthesis-first restructure (2026-04-17): coherence is a QC metric, not
    the reading. It no longer occupies the visual hero. When score is 0 or
    missing, this section is skipped entirely rather than rendering a
    semantically-empty region.
    """
    coh = unified.get("coherence", {}) or {}
    score = coh.get("score")
    label = coh.get("label")

    # Skip when data is absent or placeholder
    if not score or not isinstance(score, (int, float)) or score <= 0:
        return ""
    if not label or str(label).strip() in ("", "—", "None"):
        return ""

    arch = coh.get("name_architecture", {}) or {}
    arch_cat = arch.get("category") or ""
    arch_words = arch.get("word_count")
    arch_note = ""
    if arch_cat and arch_words:
        arch_note = f'{arch_words}-word · {arch_cat}'

    return f"""
    <section class="coherence-stat">
      <span>Coherence</span>
      <span class="score">{int(score)}</span>
      <span class="lbl">{_esc(label)}</span>
      {f'<span class="arch">{_esc(arch_note)}</span>' if arch_note else ''}
    </section>
    """


def render_tension(unified: Dict[str, Any]) -> str:
    """Primary tension / structural alignment pull-quote.

    Synthesis-first restructure: skipped entirely when the tension sentence
    is absent or empty, so we never render an empty hero quote.
    """
    ten = unified.get("tension", {}) or {}
    sentence_raw = ten.get("sentence") or ""
    sentence_raw = sentence_raw.strip() if isinstance(sentence_raw, str) else ""
    if not sentence_raw or sentence_raw in ("—", "None"):
        return ""

    sentence = _esc(sentence_raw)
    is_aligned = ten.get("primary") is None
    cls = "tension aligned" if is_aligned else "tension"
    heading = "Structural Alignment" if is_aligned else "Primary Tension"

    return f"""
    <section class="{cls}">
      <div class="smallcap label">{heading}</div>
      <div class="sentence">{sentence}</div>
    </section>
    """



# ─────────────────────────────────────────────────────────────────
# Synthesis-layer render functions (synthesis-first patch 2026-04-17)
#
# Governing rule: render existing structured synthesis only. No authored
# prose in the renderer. If a field is missing or empty, the block is
# skipped — the renderer does not fabricate synthesis.
# ─────────────────────────────────────────────────────────────────

def _hierarchy_triangle_svg(life_path, expression, cross_root) -> str:
    """Single synthesis visual: the reading's three anchor numbers as a triangle.

    Top vertex (larger):    cross_root — the axis all eight semantic axes
                            return to when pooled. This is what the reading
                            leads with.
    Bottom-left vertex:     life_path — what birth alone says.
    Bottom-right vertex:    expression — what the name alone says.

    The visual makes the hierarchy of the reading legible at a glance:
    birth and name ask different questions; synthesis is what emerges
    from pooling all traditions together — it is not a fourth number,
    it is the answer to a broader question.

    Triangles for portrait. Squares for proof. 
    Grounded entirely in existing engine values — no fabricated data.
    """
    # Guard — if any number is missing, skip the visual
    if life_path is None or expression is None or cross_root is None:
        return ""
    try:
        lp_s  = str(int(life_path))
        ex_s  = str(int(expression))
        cr_s  = str(int(cross_root))
    except (ValueError, TypeError):
        return ""

    return f"""
    <div class="hierarchy">
      <svg viewBox="0 0 460 260" xmlns="http://www.w3.org/2000/svg"
           class="hierarchy-svg" role="img"
           aria-label="Hierarchy triangle: synthesis {cr_s}, birth {lp_s}, name {ex_s}">
        <!-- Connecting lines (quiet, schematic — not decorative) -->
        <line x1="230" y1="72"  x2="90"  y2="198" class="h-link"/>
        <line x1="230" y1="72"  x2="370" y2="198" class="h-link"/>
        <line x1="90"  y1="198" x2="370" y2="198" class="h-link h-link-base"/>
        <!-- Synthesis node (top, larger — the reading's primary axis) -->
        <circle cx="230" cy="72" r="38" class="h-node h-synth"/>
        <text x="230" y="82" class="h-num h-num-synth" text-anchor="middle">{cr_s}</text>
        <text x="230" y="22" class="h-tag" text-anchor="middle">SYNTHESIS · CROSS-ROOT</text>
        <!-- Birth node (bottom-left) -->
        <circle cx="90" cy="198" r="26" class="h-node h-axis"/>
        <text x="90" y="206" class="h-num h-num-axis" text-anchor="middle">{lp_s}</text>
        <text x="90" y="245" class="h-tag" text-anchor="middle">BIRTH · LIFE PATH</text>
        <!-- Name node (bottom-right) -->
        <circle cx="370" cy="198" r="26" class="h-node h-axis"/>
        <text x="370" y="206" class="h-num h-num-axis" text-anchor="middle">{ex_s}</text>
        <text x="370" y="245" class="h-tag" text-anchor="middle">NAME · EXPRESSION</text>
      </svg>
      <p class="hierarchy-caption">
        Birth alone gives you <strong>{lp_s}</strong>.
        Name alone gives you <strong>{ex_s}</strong>.
        When eight semantic axes are pooled across all traditions,
        the axis the reading returns to is <strong>{cr_s}</strong> — the
        synthesis above them both.
      </p>
    </div>
    """


def render_portrait(output: Dict[str, Any]) -> str:
    """First real reading on the page.

    Assembled from structured fields already computed by the engine:
      - semantic_reading.dominant_cross_root           (int)
      - semantic_reading.dominant_cross_element        (str)
      - psychological_mirror.dominant_root_translation.{descriptor, domain}
      - psychological_mirror.convergence_reading       (str)
      - profile.core_numbers.{life_path, expression}   (int, int)

    The hierarchy triangle (added 2026-04-17) makes the relationship between
    the three root numbers legible: birth-only, name-only, and synthesis
    across all axes are three different answers to three different questions.
    This prevents the buyer from asking "am I a 1, a 3, or an 11?" by
    showing the answer: all three, at different scales of the computation.

    Verified reliable across 5+ profiles.
    Block is skipped if the critical fields are absent.
    """
    sr = output.get("semantic_reading", {}) or {}
    pm = output.get("psychological_mirror", {}) or {}
    core = (output.get("profile", {}) or {}).get("core_numbers", {}) or {}

    cross_root = sr.get("dominant_cross_root")
    cross_elem = sr.get("dominant_cross_element")
    drt = pm.get("dominant_root_translation", {}) or {}
    descriptor = drt.get("descriptor") or ""
    domain = drt.get("domain") or ""
    conv_reading = pm.get("convergence_reading") or ""
    life_path = core.get("life_path")
    expression = core.get("expression")

    # Require at least a dominant-root translation. Without it the portrait
    # has no substance.
    if not descriptor or not isinstance(descriptor, str):
        return ""
    descriptor = descriptor.strip()
    conv_reading = conv_reading.strip() if isinstance(conv_reading, str) else ""
    if not descriptor:
        return ""

    # Build the axis line — cross_root + domain + cross_element
    axis_parts = []
    if cross_root is not None and domain:
        axis_parts.append(f'Root <strong>{_esc(cross_root)}</strong> · {_esc(domain)}')
    elif cross_root is not None:
        axis_parts.append(f'Root <strong>{_esc(cross_root)}</strong>')
    if cross_elem:
        axis_parts.append(f'Element <strong>{_esc(cross_elem)}</strong>')
    axis_line_html = " &nbsp; · &nbsp; ".join(axis_parts)

    # The hierarchy triangle — single synthesis visual. Skipped if any of
    # the three numbers is missing; the rest of the portrait still renders.
    triangle_html = _hierarchy_triangle_svg(life_path, expression, cross_root)

    # Reading paragraph — convergence_reading only rendered if present
    reading_html = ""
    if conv_reading:
        reading_html = f'<p class="reading">{_esc(conv_reading)}</p>'

    return f"""
    <section class="portrait">
      <div class="smallcap label">Your Reading</div>
      {f'<div class="axis-line">{axis_line_html}</div>' if axis_line_html else ''}
      {triangle_html}
      <div class="descriptor">{_esc(descriptor)}</div>
      {reading_html}
    </section>
    """


def render_patterns(output: Dict[str, Any]) -> str:
    """Render fired structural patterns.

    Source: psychological_mirror.fired_patterns — verified reliable across
    all 6 benchmark profiles (semantic_reading.meta_patterns_fired misses
    Ibn Khaldun, so we use the psych-mirror version which has richer fields
    anyway: classical_root lineage + Arabic + keywords).

    Each pattern renders with: name (title-cased from pattern_id), domain
    (tag line), descriptor (prose), classical_root (muted lineage line).
    Nothing invented — only shipped fields.
    """
    pm = output.get("psychological_mirror", {}) or {}
    fired = pm.get("fired_patterns", []) or []
    if not fired or not isinstance(fired, list):
        return ""

    items = []
    for fp in fired:
        if not isinstance(fp, dict):
            continue
        pid = fp.get("pattern_id") or ""
        name = pid.replace("_", " ").title() if pid else fp.get("name", "")
        domain_raw = fp.get("domain") or ""
        # Apply presentation-layer rewrite: schema labels → plain language.
        # Falls through to the raw domain if not in the rewrite table.
        domain = _PATTERN_DOMAIN_REWRITES.get(domain_raw, domain_raw)
        descriptor = fp.get("descriptor") or ""
        classical = fp.get("classical_root") or ""

        if not name or not descriptor:
            continue

        lineage_html = ""
        if classical and isinstance(classical, str) and classical.strip():
            lineage_html = f'<div class="lineage">Classical lineage · {_esc(classical)}</div>'

        domain_html = ""
        if domain and isinstance(domain, str) and domain.strip():
            domain_html = f'<div class="domain">{_esc(domain)}</div>'

        items.append(f"""
        <div class="pattern">
          <div class="name">{_esc(name)}</div>
          {domain_html}
          <div class="descriptor">{_esc(descriptor)}</div>
          {lineage_html}
        </div>
        """)

    if not items:
        return ""

    return f"""
    <section class="patterns">
      <div class="smallcap label">Patterns Detected</div>
      {"".join(items)}
    </section>
    """


def render_theses(output: Dict[str, Any]) -> str:
    """Three civilizational theses — Islamic, Kabbalistic, Chinese.

    Source: semantic_reading.theses — verified reliable across all 6 profiles.
    Each thesis has {frame, element, core_signal}. Renders as 3-column grid
    (single column on narrow layouts via CSS).

    Skipped if fewer than 2 theses have a usable frame string.
    """
    sr = output.get("semantic_reading", {}) or {}
    theses = sr.get("theses", {}) or {}
    if not theses or not isinstance(theses, dict):
        return ""

    order = ["islamic", "kabbalistic", "chinese"]
    cols = []
    for key in order:
        t = theses.get(key)
        if not isinstance(t, dict):
            continue
        frame = t.get("frame") or ""
        if not isinstance(frame, str) or not frame.strip():
            continue
        signal = t.get("core_signal")
        if isinstance(signal, (list, tuple)):
            signal_line = " · ".join(str(s) for s in signal if s)
        elif isinstance(signal, str):
            signal_line = signal
        else:
            signal_line = ""

        tradition_label = key.capitalize()
        cols.append(f"""
        <div class="thesis">
          <div class="tradition">{_esc(tradition_label)}</div>
          <div class="frame">{_esc(frame.strip())}</div>
          {f'<div class="signal">{_esc(signal_line)}</div>' if signal_line else ''}
        </div>
        """)

    if len(cols) < 2:
        return ""  # not enough thesis frames to justify a block

    return f"""
    <section class="theses">
      <div class="smallcap label">Three Civilizational Lenses</div>
      <div class="grid">
        {"".join(cols)}
      </div>
    </section>
    """


def render_domain(domain_id: str, results: List[Dict[str, Any]], subject: str = "", subject_ar: str = "", max_rows: int = 12) -> str:
    """Render one domain section with a compact table of its top results.

    Rows are passed through the presentation filter — values like "primary",
    "comparative", "natal_chart_data required", full-name echoes (Latin or
    Arabic script), and raw booleans are hidden from the first view. max_rows
    is applied AFTER filtering, so the visible rows are always meaningful.
    """
    label = DOMAIN_LABELS[domain_id]
    subtitle = DOMAIN_SUBTITLES[domain_id]
    domain_results = [r for r in results if r.get("domain") == domain_id]

    # Sort by tier (HERO → STANDARD → COMPRESSED), then by ID for stability
    tier_order = {"HERO": 0, "STANDARD": 1, "COMPRESSED": 2}
    domain_results.sort(key=lambda r: (
        tier_order.get(r.get("tier", "COMPRESSED"), 3),
        r.get("id", "")
    ))

    rows = []
    for r in domain_results:
        display_value = _resolve_display(r, subject, subject_ar)
        if display_value is None:
            continue  # hidden by presentation filter
        rid = r.get("id", "")
        # Label override → plain-English for jargon-heavy modules
        if rid in _ID_LABEL_REWRITES:
            name = _ID_LABEL_REWRITES[rid]
        else:
            name = r.get("name", rid)
            # Strip trailing Arabic parenthetical for compactness
            if " (" in name and name.endswith(")"):
                name = name.split(" (", 1)[0]
        # Readability cleanup on value (underscores → spaces for short tokens)
        display_value = _clean_value(display_value)
        value_html = _esc(display_value)

        # Controlled disclosure — render <details> only when the module ships
        # non-trivial interpretation text. This is the pre-existing
        # `interpretation` field on every engine result. We do NOT synthesize
        # fallback prose; rows without interpretation render as plain rows.
        interp = r.get("interpretation")
        if isinstance(interp, str):
            interp_clean = interp.strip()
        else:
            interp_clean = ""
        has_interp = bool(interp_clean) and interp_clean.lower() != "none" and len(interp_clean) >= 20

        if has_interp:
            rows.append(
                f'<details class="row">'
                f'<summary>'
                f'<span class="name">{_esc(name)}</span>'
                f'<span class="value">{value_html}</span>'
                f'<span class="caret" aria-hidden="true">›</span>'
                f'</summary>'
                f'<div class="interp-panel">{_esc(interp_clean)}</div>'
                f'</details>'
            )
        else:
            rows.append(
                f'<div class="plain-row">'
                f'<span class="name">{_esc(name)}</span>'
                f'<span class="value">{value_html}</span>'
                f'<span class="caret-placeholder" aria-hidden="true"></span>'
                f'</div>'
            )
        if len(rows) >= max_rows:
            break

    if not rows:
        body = '<div class="domain-empty">No signals to surface in this domain yet.</div>'
    else:
        # Rows are a mix of <details> and <div.plain-row>. No <table> wrapper —
        # the CSS grid on each row/summary keeps columns aligned.
        body = "".join(rows)

    return f"""
    <section class="domain">
      <div class="domain-header">
        <div>
          <h2>{label}</h2>
          <div class="subtitle">{subtitle}</div>
        </div>
      </div>
      {body}
    </section>
    """


def render_convergences(synth: Dict[str, Any], top_n: int = 3) -> str:
    """Render the top N strongest cross-system number convergences."""
    convs = synth.get("number_convergences", []) or []
    # Rank by independence groups (the real signal), then system count
    convs_sorted = sorted(
        convs,
        key=lambda c: (c.get("group_count", 0), c.get("system_count", 0)),
        reverse=True,
    )
    top = convs_sorted[:top_n]

    if not top:
        return ""

    items = []
    for c in top:
        num = c.get("number", "?")
        groups = c.get("group_count", 0)
        sys_count = c.get("system_count", 0)
        pct = c.get("baseline_percentile", None)
        systems = c.get("systems", [])
        sys_display = ", ".join(systems[:8])
        if len(systems) > 8:
            sys_display += f" + {len(systems)-8} more"

        pct_line = f'<span class="pct">p{pct}</span>' if pct is not None else ""
        items.append(f"""
        <div class="conv-item">
          <div class="num">{num}</div>
          <div class="detail-block">
            <div class="headline">{sys_count} systems converge on {num} across {groups} independent families</div>
            <div class="systems">{_esc(sys_display)}</div>
          </div>
          <div class="stats">
            {groups} groups<br>
            {sys_count} systems
            {pct_line}
          </div>
        </div>
        """)

    return f"""
    <section class="convergences">
      <div class="smallcap label">Numeric Convergence &middot; Monte Carlo Evidence</div>
      <p class="conv-intro">
        Raw counts: how many independent engines landed on the same number,
        and where that count sits against a 10,000-run random baseline.
        Evidence behind the synthesis above &mdash; not a separate reading.
      </p>
      <div class="conv-list">
        {"".join(items)}
      </div>
    </section>
    """



def render_unified_html(output: Dict[str, Any]) -> str:
    """
    Main entry point. Takes the full /api/analyze response (unified=True view)
    and returns a complete HTML document as a string.

    Synthesis-first page order (locked spec 61428, 2026-04-17):
      1. Header
      2. Portrait              — the reading, assembled from engine synthesis
      3. Coherence stat        — demoted; skipped if score=0/empty
      4. Patterns detected     — fired meta-patterns with classical lineage
      5. Civilizational theses — Islamic / Kabbalistic / Chinese agree
      6. Primary tension       — skipped if empty
      7. Evidence intro        — reframes the catalog as supporting evidence
      8. Domain catalog        — existing expandable rows
      9. Convergence counts    — Monte-Carlo receipts
      10. Footer

    The reading comes first. The module catalog is the receipts.
    """
    profile = output.get("profile", {})
    unified = output.get("unified", {}) or {}
    synth = output.get("synthesis", {})
    results = output.get("results", []) or []
    subject = profile.get("subject", "") or ""
    subject_ar = profile.get("arabic", "") or ""

    # ── Synthesis layer (top of page) ──
    body_parts = [
        render_header(profile),
        render_portrait(output),
        render_coherence(unified),
        render_patterns(output),
        render_theses(output),
        render_tension(unified),
    ]

    # ── Evidence-layer transition ──
    # Frames the catalog below as supporting evidence, not the product answer.
    body_parts.append(
        '<section class="evidence-intro">'
        '<div class="smallcap label">Underlying Signals</div>'
        '<p>The reading above is assembled from many traditions computing in '
        'parallel. Below is each tradition\'s own verdict, in its own '
        'vocabulary — the receipts for the synthesis.</p>'
        '<p>Open any row to see how that tradition reads the signal.</p>'
        '</section>'
    )

    # ── Evidence layer (domain catalog) ──
    for domain_id in DOMAIN_ORDER:
        body_parts.append(render_domain(domain_id, results, subject=subject, subject_ar=subject_ar))
    body_parts.append(render_convergences(synth))

    subject_title = _esc(subject).title()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SIRR · {subject_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital,wght@0,400;1,400&family=Newsreader:ital,wght@0,300;0,400;0,500;1,300;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
  <main class="container">
    {"".join(body_parts)}
    <footer>
      SIRR ENGINE · SWISS EPHEMERIS · MONTE CARLO BASELINE N=10,000
    </footer>
  </main>
</body>
</html>
"""
