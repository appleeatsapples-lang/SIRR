# SIRR Privacy Architecture — Four-Tier Data Model

**Spec reference:** `Tools/handoff/DECISIONS_LOCKED.md §16` (internal, not shipped publicly)

This document describes how SIRR structurally separates user data into four tiers, each with different retention, encryption, and access postures. The goal is structural — not procedural — privacy: leaks should require deliberate code changes, not willpower.

---

## Tier 1 — Identity & Payment (third-party)

**Handler:** Lemon Squeezy (merchant of record, PCI-compliant)

SIRR never touches card numbers, billing addresses, or tax IDs. Lemon Squeezy issues a transaction confirmation with an opaque order ID; SIRR stores only that ID plus the customer email (needed to deliver the reading).

**Retention:** Per Lemon Squeezy's own policy — outside SIRR's direct control.

---

## Tier 2 — Reading Input & Output (encrypted, short-lived)

**Handler:** SIRR's own server, on-disk under `Engine/web_backend/orders/` and `Engine/web_backend/readings/`.

Contents:

- Submitted profile (name, DOB, time, place, mother's name)
- Computed engine output (JSON, one per order)
- Rendered reading HTML (legacy + unified view)

**Retention:** 30 days from order creation. Enforced by `Engine/web_backend/retention.py::sweep_tier2_expired()`, which walks the directories and deletes any file whose mtime is older than the cutoff.

**Access model:**

- URL tokens are AES-256-GCM AEAD-encrypted (post-P2F-PR1, 2026-04-19) using `SIRR_ENCRYPTION_KEY` via crypto.py's HKDF-derived per-context key. The payload (order_id + expiry) is opaque to the client — the entire blob is base64url-encoded ciphertext with no readable JSON. See `Engine/web_backend/tokens.py`. The earlier HMAC-signed format (`SIRR_TOKEN_SECRET`) is obsolete; the env var is harmless to leave set, surfaces a deprecation INFO log on startup.
- Reading endpoints (`/r/{token}`, `/r/{token}/unified`, `/r/{token}/merged`) resolve the token to an order ID server-side, never echoing the ID back in URLs.
- Legacy `/reading/{order_id}` and `/api/order-status/{order_id}` routes return **410 Gone** (P2D + P2F-PR1) — no grandfather fallback.

**Encryption (enforced, post-P2F-PR2):**

Per-record envelope encryption using a key derived from `HKDF(master_secret, salt=order_id, info="sirr-tier2-v1")`. At rest, the JSON and HTML files (output, legacy, unified, merged) AND the order row's PII fields (`name_latin`, `name_arabic`, `dob`, `birth_time`, `birth_location`) are AES-256-GCM-encrypted; decryption happens only within the running request that produced or requested them. Production deployments **fail-fast** at startup if `SIRR_ENCRYPTION_KEY` is unset (detected via `RAILWAY_DEPLOYMENT_ID`). Encryption failures atomically delete any plaintext residue (P2F-PR2 FIX E pattern, extended to the row layer in P2G) and mark `status="failed"`.

**Deletion flow:**

`POST /api/delete` accepts either an encrypted token or `(order_id, email)` for authentication. On success it unlinks Tier 2 reading files (engine output, legacy/unified/merged HTML), marks the order row `status="deleted"` and nulls `profile`, `email_hash`, `reading_url`, `error`, and the five PII fields (`name_latin`, `name_arabic`, `dob`, `birth_time`, `birth_location`), then queues the `order_id` for Tier 3 removal. The handler is idempotent: a repeat call against an already-deleted row returns the same response shape without re-running the unlink/update/queue path. Closed under the P2G arc (2026-04-27); see [`SIRR_MASTER_REGISTRY.md`](../engine/SIRR_MASTER_REGISTRY.md) §16.5 for closure details.

---

## Tier 3 — Aggregate Analytics (planned)

**Handler:** SIRR's own server (not yet implemented as of v1 release).

Contents (design):

- Hashed pseudonym per user: `HMAC(email, salt=tier3_salt)`
- Archetype tags, convergence counts, meta-pattern firings
- Module distribution, element balances, numerical categories
- **Never:** raw names, dates, places, mother's names, or any identifying string

**Access rules:**

- k-anonymity: no query returns a result unless ≥5 users share the pattern
- Differential privacy noise added to all published aggregates
- No join key connects Tier 3 rows back to Tier 2 records

**Deletion flow:**

User-requested deletions append the order_id to `deletion_queue.txt`. `retention.py::drain_tier3_deletion_queue()` drains the queue and removes the pseudonymous row matching the derived hash. Must complete within 30 days of request (§16.6 commitment).

---

## Tier 4 — Operator Vault (local-only)

**Handler:** Founder's local machine. Never cloud-synced.

Contents: founder's own reference data, frozen showcase artifacts, internal docs, pre-launch drafts. Lives entirely in a local encrypted directory with a separate encrypted backup.

**Rule:** Tier 4 never enters any third-party platform. Not ChatGPT, not Grok, not Gemini, not Midjourney. The only thing that may be pasted into external AI for debugging is the synthetic demo profile (Tier 0, public).

---

## Zero-knowledge operator posture (§16.3)

The operator is structurally unable to read individual production readings:

- No admin console that surfaces reading content
- Production database credentials live only in the deployed service
- Support escalations surface as metadata-only (timestamp, error category, order ID) — never content
- To debug a specific reading, the user must re-submit in ephemeral debug mode; there is no standing key to their stored record

This is liability reduction, not just privacy discipline. If the operator cannot read the data, they cannot leak it, be compelled to produce it, or be held responsible for its contents.

---

## What's enforced today vs. what's planned

| Control | Status |
|---|---|
| Encrypted URL tokens for reading access (AES-256-GCM AEAD) | Shipped — P2F-PR1 (`tokens.py`) |
| Age gate 18+ at checkout | Shipped |
| Privacy Policy + Terms of Service | Shipped (`/privacy`, `/terms`) |
| Right-to-delete endpoint | Shipped (`POST /api/delete`) |
| Retention purge job (Tier 2) | Shipped as scaffold, awaits cron wire-up |
| Tier 3 deletion queue | Stub (drains no-op until Tier 3 store lands) |
| Log hygiene (no PII in stdout, hash_oid for correlation) | Shipped — P2F-PR3 |
| No third-party client-side analytics | Verified |
| Per-record Tier 2 encryption at rest (output / .html / _unified / _merged) | Shipped — P2F-PR2 |
| Production startup fail-fast on missing SIRR_ENCRYPTION_KEY | Shipped — P2F-PR2 |
| `order_store.py` order-row PII encryption-at-rest (name + DOB on disk) | Closed — P2G (2026-04-27) |
| `/api/delete` PII null-out + post-migration fail-closed mode | Closed — P2G (2026-04-27) |
| `_make_slug` name+DOB-derived order_id (filename + row field) | Deferred — revisit at ~10⁵ active orders |
| Tier 3 aggregate store | Planned — requires DB migration |
| Differential-privacy noise calibration | Planned — requires real traffic |
| Zero-knowledge admin UI | Planned |

---

*Doc version 1.3 — 2026-04-27 — P2G-followup closure: migration script hardened (V2 full-literal preservation, V3 three-state classifier covering both missing-`order_id`-with-PII-keys and `order_id`↔`path.stem` mismatch via `SuspiciousRowAbort` + exit code 3, with reason tags codified as `AbortReason(str, Enum)`) and test #17 rewritten with sentinel `os.getpid` to actually observe `_atomic_write_json` (Codex R6 C2 + R2 C1 + R4 C1/C2 catches). Suite 236 → 240. Two §16.5 surfaces remain deferred with ~10⁵-active-order revisit thresholds: `hash_oid` 12-char log-correlation truncation, and `_make_slug` 4-char name+DOB-encoded order_id (filename + row field). See `Docs/engine/SIRR_MASTER_REGISTRY.md` §16.5 for upgrade paths.*
