# Seven Chapter Prototype

**Status:** Monday review prototype, not production route.
**Date frozen:** 2026-05-02
**Path:** `Engine/web/prototypes/seven_chapter_prototype/index.html`

## What this is

A single-file HTML prototype demonstrating a customer-facing SIRR profile rendered as **seven self-contained chapters**, one per tradition. Each chapter has its own lineage paragraph, computation block, reading paragraph, per-chapter limits, and a distinct accent color and signature glyph.

Chapter order:

1. **علم الأسماء** — Arabic abjad / science of letters (deep ochre)
2. **Πυθαγόρειος** — Pythagorean numerology (verdigris)
3. **Chaldean** — alternative letter mapping (bronze)
4. **Hellenistic** — chart-based, tropical zodiac (muted indigo)
5. **ज्योतिष** — Jyotiṣa / Vedic, sidereal zodiac (terracotta-saffron)
6. **八字** — BaZi / Four Pillars of Destiny (slate-blue)
7. **גימטריה** — Hebrew gematria, counter-chapter on cognate-mapping (olive)

A light four-bullet appendix follows the chapters: *touched / disagreed / fell silent / held its weight*. The chapters carry the weight; the appendix is editorial cross-reference only.

A right-rail chapter navigator (visible at viewport widths > 1180px) shows all seven chapters with color swatches and native-script labels. Click any entry to scroll smoothly to that chapter.

## How to open

This is a **single-file HTML prototype; no server or build step; external Google Fonts dependency.** Open it directly in any modern browser:

```bash
open ~/dev/SIRR/REPO/Engine/web/prototypes/seven_chapter_prototype/index.html
```

Or double-click `index.html` in Finder.

## What is intentionally not wired yet

- **No input form.** The page shows a fixed synthetic profile (`Sara Khalid · 1990-03-15 · Cairo, Egypt`) for demonstration; users cannot submit their own name + birth data.
- **No engine connection.** The prototype does not call `Engine/web_backend/server.py`; all values shown are hand-computed.
- **No Arabic-language flip.** The Arabic toggle in the header is decorative (`EN / ع`); RTL layout and Arabic-language copy are not implemented.
- **No methodology page.** Footer links labeled *Methodology / Honest limits / Contact* are placeholders (`href="#"`).
- **No beta application form.** The "Request a beta profile" CTA is decorative.
- **No payment flow.** Pricing was deliberately removed in favor of a free-during-beta posture; no Lemon Squeezy or other checkout is wired.

## Synthetic data — important

The profile shown (`Sara Khalid`, born 1990-03-15 14:30 Cairo) is **synthetic**, marked as such in a visible badge on the page. Computational values shown:

- Pythagorean / Chaldean / abjad numerology values are correctly hand-computed.
- Hellenistic Sun position (24°17′ Pisces) is approximated from astronomical tables.
- Vedic sidereal correction (Lahiri ayanāṃśa ≈ 23°43′ for 1990) is approximated.
- BaZi Year and Month pillars are correctly looked up from the Tang/Song-dynasty `jiazi` cycle; Day pillar is intentionally left as "(requires ephemeris)" to avoid unverified numbers.

These values are illustrative of what each chapter would contain, not authoritative outputs from the live SIRR engine.

## Dependencies

**External (network required on first load):**

- **Google Fonts:** Cormorant Garamond, EB Garamond, JetBrains Mono, Amiri, Noto Sans Devanagari, Noto Sans SC, Noto Sans Hebrew. Fonts load from `fonts.googleapis.com` and `fonts.gstatic.com`.

**Local:** none. No images, no scripts beyond inline CSS and a small inline `onclick` handler.

If network is unavailable on first open, the page still renders but falls back to system fonts; non-Latin scripts may render less consistently across OSes without the Noto fallback.

## Visual grammar

- **Dark editorial-scholarly aesthetic.** Off-black background (`#0e0d0b`), warm cream text (`#f4ede0`), accents per chapter.
- **Per-chapter accent color.** Each chapter has its own CSS custom property `--chapter-accent` driving the chapter number underline, derivation block left border, and big result number.
- **Native-script chapter numbers.** The chapter-num bar at the top of each chapter uses the tradition's native script in its native font where applicable (e.g., `علم الأسماء`, `ज्योतिष`, `八字`, `גימטריה`).
- **Result block signatures.** Numerology chapters end on a number; Hellenistic on `♓`; Vedic on `मीन`; Chinese on `庚午`; Hebrew on `1` with a red `cognate` flag.

## Why this is not production route

Three reasons:

1. **No backend.** Production must compute against `Engine/web_backend/server.py`, not display fixed synthetic values.
2. **No PDF / no checkout.** Per the §X.4 R5 + PDF-scope decisions (see `MENA_RECON_AND_DECISIONS_2026-05-02.md` in PRIVATE), the production launch posture is web-only / no module counts / free beta — the prototype reflects that posture but does not implement the customer flow.
3. **Pricing posture is "free during beta."** The page shows the beta language as a placeholder; no actual access mechanism is wired.

## Status language (use these phrasings)

- ✅ "Single-file HTML prototype; no server or build step; external Google Fonts dependency."
- ❌ Don't say "fully self-contained" — Google Fonts is external.
- ✅ "Demonstrates the seven-chapter customer-facing structure."
- ✅ "Monday review artifact, not the production route."

## Scratch reference

A scratch copy of the same file lives at `/tmp/sirr_prototype/index.html` from the build session of 2026-05-02. The repo path here is the durable reference; the `/tmp/` copy will be cleaned up on next macOS restart.
