"""SIRR-branded post-payment email — Path-C delivery layer.

Sends the customer the durable /r/{token} link to their reading via
Resend. Fires from the LS order_created webhook handler after the
compare_and_swap_status guard succeeds; failure is logged but does
not 5xx the webhook (LS would retry forever, and the customer also
sees the LS receipt button as a recovery fallback).

Customer email is extracted transiently from the webhook payload at
send time and never persisted — no new PII field, no new
encryption-at-rest surface. See
Tools/handoff/LAUNCH_PATH_C_CUSTOM_EMAIL_BRIEF.md.
"""
from __future__ import annotations

import os

# resend is an optional runtime dep. Importing lazily so unit tests
# that monkeypatch send_post_payment_email at the boundary do not
# require the SDK to be installed in the test environment.
try:
    import resend  # type: ignore
except ImportError:
    resend = None


SUBJECT = "Your SIRR reading link"


class EmailSendError(Exception):
    """Raised when the post-payment email cannot be sent.

    Carries the type-name only — no PII, no API key, no order_id —
    safe to log directly. The webhook handler catches and logs via
    sanitize_exception() per the existing pattern.
    """


def _short_order_id(order_id: str) -> str:
    return (order_id or "")[:8] or "—"


def _build_html(reading_url: str, order_id_short: str) -> str:
    return f"""<div style="font-family: -apple-system, system-ui, sans-serif; max-width: 560px; margin: 0 auto; color: #111;">
  <p>Order received.</p>

  <p>Your SIRR reading is being computed. Access it here:</p>

  <p style="margin: 24px 0;">
    <a href="{reading_url}" style="display: inline-block; padding: 12px 24px; background: #111; color: #fff; text-decoration: none; border-radius: 4px;">
      View your reading
    </a>
  </p>

  <p style="color: #666; font-size: 14px;">
    If the page shows "your reading is being prepared," that's expected for the first ~60 seconds after payment. The page will refresh on its own once computation completes.
  </p>

  <p style="color: #666; font-size: 14px;">
    Bookmark this link. Your reading lives at this URL only — there's no account, no login, and no other way back to it.
  </p>

  <p style="color: #999; font-size: 12px; margin-top: 32px;">
    Order: {order_id_short}<br>
    SIRR is a deterministic symbolic-identity engine. Your reading is computed from the inputs you provided at checkout; nothing else is stored about you.
  </p>
</div>"""


def _build_text(reading_url: str, order_id_short: str) -> str:
    return f"""Order received.

Your SIRR reading is being computed. Access it here:

{reading_url}

If the page shows "your reading is being prepared," that's expected for the first ~60 seconds after payment. The page will refresh on its own once computation completes.

Bookmark this link. Your reading lives at this URL only — there's no account, no login, and no other way back to it.

---
Order: {order_id_short}
SIRR is a deterministic symbolic-identity engine. Your reading is computed from the inputs you provided at checkout; nothing else is stored about you.
"""


def send_post_payment_email(*, to: str, reading_url: str, order_id: str) -> None:
    """Send the SIRR-branded post-payment email via Resend.

    Subject ("Your SIRR reading link") and body are timing-agnostic
    so a single email handles all engine outcomes (success / failure /
    pending) without a separate failure-email path. See brief §6a for
    the timing-vs-clarity decision.

    Raises EmailSendError on any Resend API failure or missing config.
    The webhook handler catches and logs without 5xx-ing — LS would
    retry forever otherwise and the customer has the LS receipt
    button as a fallback.
    """
    if resend is None:
        raise EmailSendError("resend-sdk-missing")
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise EmailSendError("RESEND_API_KEY-unset")
    sender = os.environ.get("EMAIL_FROM")
    if not sender:
        raise EmailSendError("EMAIL_FROM-unset")

    resend.api_key = api_key
    order_id_short = _short_order_id(order_id)
    try:
        resend.Emails.send({
            "from": sender,
            "to": to,
            "subject": SUBJECT,
            "html": _build_html(reading_url, order_id_short),
            "text": _build_text(reading_url, order_id_short),
        })
    except Exception as exc:
        # Wrap as type-name only so the caller's log line never carries
        # the SDK exception's message (which on auth failures includes
        # a token prefix).
        raise EmailSendError(type(exc).__name__) from None
