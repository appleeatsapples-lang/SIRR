# B2 Truth Scan — Scholarship Review of Jargon Definitions
Reviewer: Claude
Source: Tools/handoff/wave2/B2_JARGON_DEFINITIONS_DRAFT.md
Method: Re-read each definition against scholarly knowledge; web-verified two highest-confidence claims.

> **Resolution status (as of this commit):** Findings 1, 2 (HIGH) and 3, 4, 5 (MEDIUM) resolved in `B2_JARGON_DEFINITIONS_DRAFT.md`. Finding 6 (LOW) accepted as Wave 2.5 polish, not actioned. Findings 7, 8, 9 deferred pending engineer-input on what each metric actually computes; the open questions stand as written below. Items in "CONFIDENCE-CHECKED" section also remain open for scholarship review.

## How to read this scan
Each finding has a severity (HIGH / MEDIUM / LOW) and a recommended rewrite where appropriate. HIGH means the current definition is factually wrong or misleading enough that a curious customer who researches the term will find we got it wrong, and that damages the engineer-not-mystic credibility. MEDIUM means incomplete in a way that misleads. LOW means could be more precise but not actionable.

I also flag which findings I'm CERTAIN of vs. ones I want to surface to your scholarship eye for verification.

---

## HIGH SEVERITY — definitions that are factually wrong as currently written

### 1. Vine (Celtic) — "Celtic tree calendar"
**Current**: "Celtic tree calendar assigns one of 21 trees to a date range"

**Problem**: The 13-tree Celtic Tree Calendar most commonly referenced was invented by **Robert Graves in his 1948 book *The White Goddess***. It is NOT a historically Celtic system. Graves's own grandfather (Charles Graves, President of the Royal Irish Academy and a leading Ogham scholar) had already dismissed the tree-alphabet calendar idea as spurious. Modern Celtic scholarship (Berresford Ellis, MacAlister, others) is unanimous: the tree calendar is a 20th-century literary construction, beautifully imagined but not pre-modern Celtic.

The Ogham alphabet IS historical (~4th-9th century Irish), and tree associations with letters DO appear in medieval Irish texts — but the calendar mapping is Graves's invention.

**Suggested rewrite**: "Robert Graves's 1948 tree-month calendar (from *The White Goddess*), derived from the medieval Ogham alphabet; popular in modern neo-pagan practice but not historically pre-modern Celtic."

**Why this matters**: A customer who Googles "Celtic Tree Calendar" finds Wikipedia and 30+ pages immediately attributing it to Graves. If our definition pretends it's "the Celtic tree calendar" without acknowledging its modern provenance, we look ignorant. Honest framing is the engineer-not-mystic move.

**Confidence**: VERY HIGH (web-verified just now; well-documented in Celtic scholarship)

---

### 2. Lo Shu Grid / Nine Star Ki / Flying Star / Bazhai — origin lumping
**Current**: "Chinese number-grid traditions that map birth date onto nine cells; each tradition reads the cell pattern differently"

**Problem**: **Nine Star Ki is JAPANESE in its codified form**, not Chinese. It was developed/consolidated in 1924 by Shinjiro Sonoda in Japan, drawing on Chinese metaphysical roots (Lo Shu, Five Elements, Eight Trigrams). Calling it Chinese is partially right (roots) and partially wrong (codification). Practitioners and scholars distinguish them.

The other three (Lo Shu, Flying Star, Bazhai) are Chinese.

**Suggested rewrite** — split into separate definitions:
- **Lo Shu Grid** — a 3×3 Chinese magic square that maps numbers onto a nine-cell pattern; foundation for several feng shui systems
- **Nine Star Ki** — a Japanese system codified by Shinjiro Sonoda in 1924, drawing on Chinese metaphysical principles; reads birth date through a nine-cell grid with three personality numbers
- **Flying Star** — a Chinese feng shui timing system that rotates Lo Shu numbers through space and time
- **Bazhai** — "Eight Mansions" Chinese feng shui that maps a person's birth direction to spatial energy

**Confidence**: VERY HIGH (web-verified just now)

---

## MEDIUM SEVERITY — definitions that mislead by omission

### 3. Barzakh — credit attribution
**Current**: "Arabic for 'isthmus' or 'between-state'; the term appears in Ibn Arabi's *Futuhat* as a metaphysical category for liminal phases"

**Problem**: Barzakh appears in the **Quran first** (three occurrences: 23:100, 25:53, 55:20). Ibn Arabi developed it philosophically, but he didn't introduce the term. Crediting only Ibn Arabi is a meaningful omission for a customer who knows the Quran or who'd recognize the term from Islamic theology before encountering Ibn Arabi.

**Suggested rewrite**: "a Quranic term (3 occurrences) meaning isthmus or between-state; philosophically developed in Ibn Arabi's *Al-Futuhat al-Makkiyya* as a metaphysical category for liminal phases."

**Confidence**: HIGH (well-documented in Quranic and Sufi scholarship; verifiable)

---

### 4. Notarikon vs Albam — grouping is loose
**Current**: "Hebrew cipher transformations (acronyms / letter swap); applied here to Arabic input as a modern method"

**Problem**: Notarikon and Albam are different KINDS of operations:
- **Notarikon** — a Kabbalistic technique that treats words as abbreviations or acronyms (each letter standing for the initial of another word)
- **Albam** — a letter-substitution cipher (specifically: split the alphabet in half, swap pairs)

Calling them both "cipher transformations" obscures the difference. Notarikon isn't really a cipher in the substitution sense — it's an acronym/expansion method.

**Suggested rewrite** — separate them:
- **Notarikon** — a Kabbalistic acronym/expansion method that reads letters as initials of other words
- **Albam** — a Hebrew letter-substitution cipher (alphabet-half pairing)
- For both, "applied here to Arabic input as a modern method" remains accurate.

**Confidence**: HIGH (standard Kabbalistic distinction; Charles Manekin and other scholars treat them as distinct categories)

---

### 5. Shadow Card — overstating the tradition
**Current**: "a second tarot card paired with the birth card; one tradition reads it as compensatory pattern"

**Problem**: "Shadow Card" as a paired-birth-card concept is a **modern tarot practice**, primarily associated with Mary Greer and Angeles Arrien (both 20th/21st century). Calling it "one tradition" suggests historical lineage that doesn't exist. The Jungian shadow archetype is much older, but its application as a tarot pairing is recent.

**Suggested rewrite**: "a modern tarot practice (popularized by Mary Greer's work in the 1980s-90s); pairs with the birth card and is read as a compensatory archetype."

**Confidence**: MEDIUM-HIGH (Greer's work is well-documented; whether others independently coined "shadow card" is less certain)

---

## LOW SEVERITY — could be more precise

### 6. Abjad Kabir — "most common"
**Current**: "the most common ('greater') Abjad numbering scheme"

**Problem**: "Most common" is regionally variable. Eastern (Mashriqi) and Western (Maghrebi) Arabic traditions use **different letter orderings** for Abjad numerology. Both call themselves "Kabir" in their respective regions. The numerical assignments diverge for some letters.

**Suggested rewrite**: "the larger ('Kabir') Abjad numbering scheme, which assigns values 1 through 1000; letter ordering varies between Mashriqi (Eastern) and Maghrebi (Western) Arabic traditions."

**Confidence**: HIGH for the existence of regional variation; MEDIUM about whether to surface that complexity in a customer-facing definition.

---

### 7. Hermetic framing (axes) — too vague
**Current**: "a SIRR comparative metric scoring placement on a hermetic correspondence axis"

**Problem**: "Hermetic correspondence axis" is too vague to be useful. Hermeticism uses correspondences (as above so below; macrocosm-microcosm) but those aren't typically called "axes." If this is a SIRR-coined metric, it should be labeled SIRR composite explicitly. If it draws from a specific hermetic source (Three Books of Occult Philosophy? Kybalion?), name it.

**Suggested rewrite (if SIRR composite)**: "a SIRR composite that scores your reading on axes derived from Hermetic correspondence principles (macrocosm-microcosm pairings)."

**Surface-back to engineer**: what specifically does this metric compute? The current definition can't be tightened without that input.

**Confidence**: HIGH that the definition is too vague; uncertain about how to fix without engineer input.

---

### 8. Daily cycle index — "modern cycle theory"
**Current**: "a single-day number from a modern cycle theory; 'neutral' means your day's value sits at the midpoint"

**Problem**: "Modern cycle theory" is too vague. Could mean biorhythms (Fliess, ~1900), Personal Day numerology (varies), or a specific contemporary framework. The customer can't research this.

**Suggested action**: Either name the specific framework SIRR uses, or label it as a SIRR composite if it's our own.

**Surface-back to engineer**: which specific cycle theory does this signal compute?

**Confidence**: HIGH that the definition is too vague to be useful.

---

### 9. Birth Ruler — vague between Vedic concepts
**Current**: "the planet a given Vedic tradition treats as your dominant ruler at birth"

**Problem**: This could mean:
- **Lagnesha** / Ascendant ruler (the planet ruling the rising sign)
- **Atmakaraka** (the planet with the highest degree in the chart, "soul indicator")
- **Janma Nakshatra Lord** (the planet ruling the moon's nakshatra at birth)

These are different concepts. "Birth Ruler" as a label is ambiguous.

**Suggested action**: Determine which of the three SIRR is computing and name the specific concept.

**Surface-back to engineer**: which ruler-concept is computed?

**Confidence**: HIGH that the term is ambiguous in Vedic context.

---

## CONFIDENCE-CHECKED — flagged for your scholarship eye

The following I'm somewhat confident about but would value your verification on:

- **Profection** definition: I have it as "advances one house per year" — correct in Hellenistic terms, but Vedic profection (if SIRR uses Vedic) might compute differently. Verify.

- **Firdaria** definition: I described it as "medieval Persian-Arabic." It traces to Hellenistic-era sources but was systematized in Persian/Arabic medieval astrology. The "medieval" framing is defensible but you may have a more precise lineage view.

- **In Joy** definition: I have "Sun's joy is the 9th house" — this is Hellenistic. Other planets' joys (Moon 3rd, Mercury 1st, Venus 5th, Mars 6th, Jupiter 11th, Saturn 12th) are standard Hellenistic doctrine. Verify SIRR uses the standard table.

---

## SUMMARY

**9 findings total**:
- 2 HIGH severity — should fix before shipping (Celtic Tree Calendar, Nine Star Ki origin)
- 3 MEDIUM severity — improve before shipping (Barzakh, Notarikon/Albam, Shadow Card)
- 4 LOW severity — could improve (Abjad Kabir regional variation, Hermetic framing, Daily cycle, Birth Ruler)

**Findings requiring engineer input** (you, not me): items 7, 8, 9 — what specifically does each compute?

**Net assessment**: The draft is more carefully calibrated than I expected. Most definitions are correct or correct-enough for first-launch. The HIGH-severity findings are recoverable in 5-10 min of edits. The MEDIUM ones add nuance without breaking flow. The LOW ones can be addressed in a Wave 2.5 polish pass after launch.

The biggest single risk is the Celtic Tree Calendar item — that's a popular myth in modern spirituality circles, and customers who research it will find we leaned on it without honesty. Worth fixing before any of this goes into the rendered reading.
