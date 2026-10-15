"""Outgoing e-mail (password reset). Uses plain SMTP from the standard library - no extra packages.

If SMTP is not configured (SMTP_HOST / SMTP_FROM empty) nothing is sent: the message is printed to the backend console and saved in
data/outbox/ so the feature can be tried locally. Configure SMTP in backend/.env to send real e-mail."""
import logging
import re
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from html import escape

import config

log = logging.getLogger("marketmind.mail")


def smtp_configured() -> bool:
    return bool(config.SMTP_HOST and config.SMTP_FROM)


def _save_to_outbox(to: str, subject: str, text: str) -> None:
    banner = "=" * 70
    print(f"\n{banner}\n[MarketMind] SMTP is not configured - e-mail NOT sent. Dev copy below.\nTo: {to}\nSubject: {subject}\n\n{text}\n{banner}\n", flush=True)
    try:
        config.OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^A-Za-z0-9_.@-]", "_", to)
        (config.OUTBOX_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_{safe}.txt").write_text(f"To: {to}\nSubject: {subject}\n\n{text}\n", encoding="utf-8")
    except OSError:
        log.warning("could not write the dev outbox file")


def send_email(to: str, subject: str, text: str, html: str | None = None) -> bool:
    """Returns True if the message was handed to an SMTP server. Never raises (callers run it in a background task)."""
    if not smtp_configured():
        _save_to_outbox(to, subject, text)
        return False
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = subject, config.SMTP_FROM, to
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")
    try:
        ctx = ssl.create_default_context()
        if config.SMTP_SECURITY == "ssl":
            server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=20, context=ctx)
        else:
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20)
        with server as smtp:
            if config.SMTP_SECURITY == "starttls":
                smtp.starttls(context=ctx)
            if config.SMTP_USER:
                smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as exc:                      # wrong password, blocked port, offline ... - never crash the request
        log.error("could not send e-mail to %s: %s", to, exc)
        print(f"[MarketMind] Could not send e-mail to {to}: {exc}", flush=True)
        return False


def send_reset_email(to: str, name: str, link: str) -> bool:
    minutes = config.RESET_TOKEN_MINUTES
    text = (f"Hi {name},\n\nWe received a request to reset your MarketMind AI password.\n\n"
            f"Open this link to choose a new one (valid for {minutes} minutes, works once):\n{link}\n\n"
            "If you did not ask for this, you can ignore this e-mail - your password will not change.\n\n- MarketMind AI")
    html = (f"<p>Hi {escape(name)},</p><p>We received a request to reset your MarketMind AI password.</p>"
            f'<p><a href="{escape(link)}" style="background:#3b5bdb;color:#fff;padding:10px 18px;border-radius:8px;text-decoration:none">Choose a new password</a></p>'
            f"<p>This link is valid for {minutes} minutes and works once. Or paste it into your browser:<br>{escape(link)}</p>"
            "<p>If you did not ask for this, you can ignore this e-mail - your password will not change.</p><p>- MarketMind AI</p>")
    return send_email(to, "Reset your MarketMind AI password", text, html)
