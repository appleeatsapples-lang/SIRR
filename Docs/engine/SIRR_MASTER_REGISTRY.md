# SIRR Master Registry

This file is the source-of-truth summary for SIRR's privacy doctrine state, the closures that have shipped, and the items that are explicitly deferred. It is updated each time a doctrine-affecting PR merges.

---

## §16.5 doctrine state — post-P2G closure (2026-04-27)

**Headline (honest scope):** name+DOB does not appear in any URL, response body, server runtime log line, or `_reading.md` plaintext intermediate. Tier 2 reading artifacts (output JSON, legacy `.html`, `_unified.html`, `_merged.html`) AND order rows are AES-256-GCM encrypted at rest with atomic plaintext cleanup on encryption failure. Token URLs are opaque ciphertext. `POST /api/delete` nulls all PII fields on the order row and is idempotent under repeat-delete.

**Three of the original four P2G-deferred items are now closed (commit pending squash, hash recorded post-merge below). Two distinct items remain deferred — the second was surfaced by Codex R2 and was previously conflated with the first under the post-P2F state:**

- `Engine/web_backend/sanitize.py` (`hash_oid` truncation length) — operational log correlation IDs are a 12-char SHA-256 prefix (~48 bits of preimage resistance). Acceptable for the current single-tenant log surface and threat model. **Revisit threshold: ~10⁵ active orders or transition to a multi-tenant log surface, whichever comes first.** Upgrade path: HMAC-keyed variant. See lower deferred section for canonical entry.
- `Engine/web_backend/order_store.py:_make_slug` — the order_id slug encodes the customer's name and DOB into both the on-disk filename (`<name>-<DDMMMYYYY>-<4-char-hash>.json`) and the row body's `order_id` field. After the delete path nulls the five PII fields, the slug remains as a recoverable name+DOB-derived identifier. The 4-char hash provides ~16 bits of preimage resistance. **Revisit threshold: same as `hash_oid` (~10⁵ active orders or any external party gaining access to the orders directory listing). Upgrade path: opaque random order_id (UUID4 hex truncation) decoupled from name/DOB; requires a one-shot rename migration of existing rows.** This was previously conflated with the `hash_oid` log-truncation item under the post-P2F state — Codex R2 correctly surfaced it as a separate filename/row-field surface, distinct from the log-correlation surface.

### Closures by phase

**P2D (narrow §16.5 closure, 2026-04-19 — through 2026-04-25 recovery arc):**
- `/reading/{order_id}`, `/reading/{order_id}/unified`, `/reading/{order_id}/merged` → 410 Gone (commit `070f931`)
- `_resolve_token_or_order_id` grandfather removed — raw order_ids no longer accepted on `/r/` (commit `070f931`)
- 6 `sanitize_exception()` sites in `server.py` (commit `070f931`)
- 3 `runner.py` error fields use `type(e).__name__` instead of `str(e)` (commit `070f931`)
- uvicorn `--no-access-log` flag (Procfile + railway.toml + CI guard step) — fixed forward after the `--access-log false` access-log incident (commits `92b95b4` revert + `1384053` correction)

**P2F-PR1 (broader §16.5 closure — token opacity + 4 surfaces, 2026-04-25 commit `538ab8d`):**
- Tokens AES-256-GCM AEAD-encrypted via `crypto.encrypt_bytes` with context `"sirr-token-v1"` (replaces HMAC-signed-payload format; payload is now opaque ciphertext to anyone without the master key)
- `/api/order-status/{order_id}` → 410 Gone; legacy logic moved to `_serve_order_status_by_id` reachable only via `/api/r/{token}/status`
- `/success?order_id=...` → 410 Gone (legacy query branch removed)
- `success.html` legacy JS code path entirely removed (no more raw `/api/order-status/{id}` or `/reading/{id}` URL construction)

**P2F-PR2 (defensive hardening + Codex Findings 1, 2 + encryption-integrity end-to-end, 2026-04-25 commit `7b675a7`):**
- `reading_url` field removed from `/api/r/{token}/status` response (Codex Finding 1)
- `order_id` field removed from `/api/checkout` response (Codex Finding 2; outbound payment-provider payloads still carry it server-to-server, intentional)
- Encryption silent-swallow → strict-fail with `update_order(status="failed", error="encryption_failed:<ExcClass>")` so `success.html`'s status-check fires correctly (FIX A)
- `_merged.html` added to `_encrypt_tier2_outputs` targets list (FIX B)
- Lazy regen paths (`_serve_reading_unified_by_id`, `_serve_reading_merged_by_id`) encrypt-after-write, strict-fail (FIX C, with round-3 enforcement)
- Atomic plaintext cleanup on encryption failure — any non-encrypted target file is `.unlink()`ed before the re-raise (FIX E)
- Production startup hard-fails on missing `SIRR_ENCRYPTION_KEY` when `RAILWAY_DEPLOYMENT_ID` is set
- 3 P2E `str(e)` sites (server.py:611 `/api/analyze`, :978 demo render, :1079 Stripe webhook sig) sanitized
- LemonSqueezy provider-controlled error body replaced with constant
- `SIRR_TOKEN_SECRET` deprecation INFO log on startup if env var still set

**P2F-PR3 (operational logs + status-aware serving + doctrine cleanup, 2026-04-25):**
- `hash_oid` helper in `sanitize.py` — non-reversible 12-char SHA-256 prefix for log correlation IDs
- Log scrubs at all known sites that interpolated raw `order_id`:
  - `Engine/web_backend/server.py` × 5 (`[tier2-encrypt]`, `[unified_view]`, `[merged_view]`, `[legacy_reading]`, plus the inner caller's `[tier2-encrypt]` log)
  - `Engine/web_backend/retention.py` × 6 (expire-order, expire-order-failed, expire-reading, expire-reading-failed, tier3-delete-queued — also strips raw filenames since they embed `order_id`)
  - `Engine/html_reading.py` × 1 (Saved-reading log)
  - `Engine/reading_generator.py` × 2 (drops `context['subject']` from generation logs entirely; operational signal preserved without the PII tail)
- `_reading.md` plaintext intermediate now unlinked after `generate_html_reading` consumes it (closes the Tier 2 plaintext residue gap that wasn't in any encryption target list)
- Status-aware serving in `_serve_tier2_html` — refuses plaintext for `status="failed"` orders (defense-in-depth for the case where FIX E's best-effort cleanup itself fails)
- Stale HMAC-token doctrine references updated to AEAD reality (`server.py` × 3 sites, `PRIVACY_TIERS.md`, `privacy.html`, `bootstrap_railway_env.sh`)
- `boot-smoke` CI step now executes `railway.toml`'s `startCommand` directly (deepest fix to the access-log-incident class — string-presence regex is no longer the only guard)
- `LANE_DOCTRINE_v2.md` codifies the multi-model lessons from this arc
- Audit doc superseded header (audit relocated to `PRIVATE/Archive/audits/` as part of SCRUB-V2; not retained in public repo)

**P2G (final §16.5 closure — order_store.py PII encryption-at-rest + delete null-out, 2026-04-27 commit `<HASH>`):**
- `Engine/web_backend/order_store.py` — five PII fields (`name_latin`, `name_arabic`, `dob`, `birth_time`, `birth_location`) encrypted at rest per-field with AES-256-GCM via `crypto.encrypt_str(value, context=order_id)`. Per-field rather than whole-row so `get_order_by_stripe_session` stays O(N) reads, not O(N) decrypts, and `update_order(status=…)` doesn't re-encrypt PII on every non-PII write.
- On-disk format sentinel: `enc:v1:<hex(blob)>`. **The `v1` sentinel is load-bearing** — any future migration to a new encrypted-field format must bump to `enc:v2:` and ship a read-side compat path that handles both prefixes during the transition window.
- `get_order` is status-aware: rows with `status="failed"` skip decrypt and return PII fields as `None` (mirrors the P2F serve-side refusal pattern at `server.py:415`). Decryption failures on non-failed rows surface a `[order_store-decrypt]` WARNING via `hash_oid(order_id)` + `type(exc).__name__`, never raw payload/key/IV bytes; PII is then stripped to `None` and the dict is returned (preserves the existing `dict | None` contract for callers).
- `update_order` encrypts incoming PII kwargs inside the existing module-level `threading.Lock`. The `_wrap_pii_value` helper has **no `enc:v1:` sentinel skip** — every caller-supplied PII value is encrypted unconditionally, so a malicious or buggy caller passing `name_latin="enc:v1:..."` cannot bypass the encryption layer (Codex R2 V3 catch). Encrypt-and-write happens entirely under `_lock`, so two concurrent writers cannot interleave a half-encrypted row.
- Disk writes go through `_atomic_write_json` (temp file + `fsync(file)` + `os.replace` + `fsync(dir)`) so a process kill mid-write cannot leave a torn row visible to the unlocked `get_order` reader path (Codex R2 V4 catch — the prior `Path.write_text` is open+write+close, not atomic). Temp filename is suffixed with `.<pid>.<random-hex>.tmp` (Codex R4 C2 catch); the pid+random-hex composition prevents tmp collisions within the current single-uvicorn deploy, and orphaned temps are best-effort unlinked on any failure mid-write. Cross-process semantics under multi-worker (gunicorn) are scoped for follow-up — the lock and atomicity are correct within one process today, but a true cross-process barrier would require flock or a sqlite/postgres-style lock manager (already on the roadmap for the eventual store upgrade).
- All disk I/O at the order_store boundary surfaces as `OrderStoreIOError(type_name)` — type-name only, never the slug-bearing path or the (possibly partial) row contents. `_atomic_write_json` wraps OSError; `_safe_read_row` wraps OSError + UnicodeDecodeError + JSONDecodeError, plus shape-validates that the parsed value is a dict carrying an `order_id` key (Codex R6 V4 catch — engine output AES-GCM blobs colocated in `ORDERS_DIR` per `paths.py:14` raise UnicodeDecodeError on `read_text`; foreign top-level types or dicts missing `order_id` are treated as corrupt and skipped). Every caller in `server.py` (`update_order` is called from ~9 sites) gets a sanitized exception without per-call hardening, since the slug encodes name+DOB by construction (Codex R4 V4 catch — wider call surface than R2 implied).
- Decrypt-failure log line uses `type(exc).__name__` only, never `str(exc)` — defense-in-depth against future exception types whose `__str__` could surface payload/key/IV bytes (Codex R2 V6 catch). The R5 log-hygiene test forces a PII-bearing exception through the chain to give the assertion teeth against any link reverting to `{exc}` interpolation (Codex R4 C3 catch).
- FIX E parity at the row layer: encryption raising in `create_order` aborts before any disk write, so no plaintext file is left behind. Verified by `test_create_order_atomic_on_encryption_failure`.
- `POST /api/delete` extended to null all five PII fields alongside `profile`/`email_hash`/`reading_url`/`error`. **Idempotent short-circuit reads the raw on-disk row** via `is_row_already_fully_deleted(order_id)` rather than the sanitized `get_order()` view (Codex R6 V1 catch — under fail-closed mode `get_order` strips plaintext PII to None on read, which would mask on-disk residue from the short-circuit check and lock any escaped legacy row into a permanent leak). The fast-path return only fires when the raw row has `status="deleted"` AND every PII field is literally None on disk; any row that escaped the migration with `status="deleted"` but PII still in place falls through to the null+update pass. **Error handling is split** (Codex R2 V5/C3 catch): `update_order` failures raise `HTTPException(500, "deletion failed; please retry")` rather than silently returning 200 with PII still on disk; tier-3 queue failures log via `[api-delete] tier3-queue failed` (no raise — Tier-3 retry semantics are pending Tier 3 going live, but Tier-2 deletion has already succeeded so the customer's right-to-delete contract is honored on our side). Token-authenticated `/api/delete` is fully idempotent; the `(order_id, email)` auth path is documented as latent-broken under the future-work section.
- One-shot migration script `Engine/web_backend/migrate_pii_encrypt.py` — idempotent CLI. Three classes of legacy content handled: (1) **plaintext PII** → encrypted via `update_order`; (2) **spoofed `enc:v1:` prefix** (a pre-R3 caller writing `name_latin="enc:v1:DEADBEEF"` as plaintext, which R3's V3 fix only blocked going forward) → validated by attempting decrypt; on failure, post-prefix portion is treated as the user's literal plaintext and re-encrypted (Codex R4 V2 catch); (3) **legacy `status="deleted"` rows with PII still present** (pre-P2G `/api/delete` only nulled four operational fields) → the five PII fields are NULLED, not encrypted, so a legacy gap doesn't become a permanent encrypted residue (Codex R4 V3 catch). Files in `ORDERS_DIR` are shape-filtered to row JSONs only — engine output AES-GCM blobs and any foreign files are silently skipped (Codex R4 V1 catch — `paths.py:14` confirms ORDERS_DIR holds rows + engine output files). Touches `DATA_DIR/.pii_encrypted_at_rest_v1` marker only on a clean pass. Operator runs it once before flipping production deploy. The marker activates a fail-closed mode in `_unwrap_pii_value`: post-migration, any row still carrying plaintext PII is treated as a bug and stripped to `None` on read rather than served.
- 19 tests (`Engine/tests/test_order_pii_encryption.py`): on-disk PII never plaintext, decrypt round-trip, status=failed strip-to-None, FIX E atomic on encrypt failure, delete nulls PII, repeat-delete idempotent, no plaintext PII across stderr+logging surfaces with PII-bearing forced exception, V3 enc-prefix injection re-encrypted, V4 atomic write torn-row + path-not-leaked, migration encrypts plaintext + sets marker, fail-closed mode strips plaintext post-marker, V5 /api/delete returns 500 on row-write failure, V1 migration skips engine output blobs and foreign files, V2 migration recovers spoofed prefix and round-trips, V3 migration nulls PII on legacy deleted rows, V3 belt-and-suspenders short-circuit cleans escaped legacy deleted rows, C2 tmp-suffix uniqueness across writers, R6 V1 raw-row probe (escaped row in fail-closed mode gets nulled, not short-circuited via sanitized view), R6 V4 glob loop survives binary blobs and foreign JSON shapes. Synthetic placeholder PII per §13.7.

### Remaining deferred surface (post-P2G)

- **`hash_oid` truncation length** (`Engine/web_backend/sanitize.py`) — 12-char SHA-256 prefix gives ~48 bits of preimage resistance. Acceptable for the current threat model (operational log correlation, single-tenant log surface). **Revisit threshold: ~10⁵ active orders or transition to a multi-tenant log surface, whichever comes first.** Upgrade path: HMAC-keyed variant.
- **`_make_slug` 4-char name+DOB hash** (`Engine/web_backend/order_store.py`) — order_id slug encodes name and DOB into the on-disk filename and the row body's `order_id` field. After delete nulls the five PII fields, the slug remains as a recoverable name+DOB-derived identifier. The 4-char hash gives ~16 bits of preimage resistance. **Revisit threshold: same as `hash_oid` (~10⁵ active orders, or any external party gaining access to the orders directory listing).** Upgrade path: opaque random order_id (UUID4-derived) decoupled from name/DOB; requires a one-shot rename migration of existing rows. Codex R2 V1 surfaced this as a separate surface from `hash_oid`'s log-correlation truncation; both are documented separately so future audits can address them independently.

### Future-work tracking (not §16.5 surfaces, logged here for visibility)

- **In-memory plaintext window during `create_order`** — the order dict holds plaintext PII briefly between construction and the in-place encrypt step inside `_lock`. Process core dumps could capture that window. Not a §16.5 disk-residue concern; track if/when an in-memory hardening arc starts.
- **`server.py:849` order_id+email auth path** — `order.get("email", "")` reads a field that the order store never sets, so the email-check branch always fails. Latent since pre-P2F; orphan to P2G's surface. Track separately; the token path covers all known production callers of `/api/delete`.

### Other known deferred items

- **Stripe / LS payment metadata still carries raw `order_id`** in their internal dashboards (third-party log surface, not our control). Documented in commit messages; not a runtime leak on our side.
- **Migration race window during PR-1 deploy**: pre-existing HMAC tokens became invalid the moment the new code went live. Mitigated by minting fresh tokens for the active customer's test order immediately after deploy. Not a concern for new orders post-deploy.
- **`SIRR_TOKEN_SECRET` env var on Railway**: still set, now obsolete since P2F-PR1. Harmless; deprecation INFO log surfaces on every container restart. Bootstrap script no longer generates it (P2F-PR3 round 2). Will be removed from Railway at the operator's discretion once the recommendation has been seen enough times.

### Doctrine sources of truth

- This file (registry): claims summary, deferral list
- `Docs/architecture/PRIVACY_TIERS.md`: tier definitions and rationale
- `Docs/operations/LANE_DOCTRINE_v3.md`: how multi-model work is gated and verified (supersedes v2; v2 retained as historical context)
- Brief archive: `MKB/SIRR/PRIVATE/Orchestration/Briefs/P2{D,F}_*.md`
- Audit history (superseded): relocated to `PRIVATE/Archive/audits/` as part of SCRUB-V2; not retained in public repo.
