"""Pure unit tests for mailer.py with a fake SMTP server (nothing is really sent):  python -m pytest tests/test_mailer.py"""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import config
import mailer
import resettokens

LINK = "http://localhost:5173/?reset_token=abc123_DEF-456"


def _smtp(**kw):
    base = dict(SMTP_HOST="smtp.example.com", SMTP_PORT=587, SMTP_USER="me@example.com", SMTP_PASSWORD="app-pass",
                SMTP_FROM="me@example.com", SMTP_SECURITY="starttls")
    base.update(kw)
    return [patch.object(config, k, v) for k, v in base.items()]


def _run(patches, fn):
    for p in patches:
        p.start()
    try:
        return fn()
    finally:
        for p in patches:
            p.stop()


def test_without_smtp_the_mail_goes_to_the_dev_outbox_and_nothing_is_sent():
    out = Path(tempfile.mkdtemp())
    with patch("smtplib.SMTP") as smtp:
        ok = _run(_smtp(SMTP_HOST="", SMTP_FROM="") + [patch.object(config, "OUTBOX_DIR", out)], lambda: mailer.send_reset_email("a@b.com", "Ann", LINK))
    assert ok is False and not smtp.called
    files = list(out.glob("*.txt"))
    assert len(files) == 1 and LINK in files[0].read_text(encoding="utf-8")


def test_starttls_login_and_message_content():
    server = MagicMock()
    with patch("smtplib.SMTP") as smtp:
        smtp.return_value.__enter__.return_value = server
        ok = _run(_smtp(), lambda: mailer.send_reset_email("user@x.com", "Ann <b>", LINK))
    assert ok is True
    smtp.assert_called_once_with("smtp.example.com", 587, timeout=20)
    server.starttls.assert_called_once()
    server.login.assert_called_once_with("me@example.com", "app-pass")
    msg = server.send_message.call_args[0][0]
    assert msg["To"] == "user@x.com" and msg["From"] == "me@example.com" and "Reset" in msg["Subject"]
    text, html = msg.get_body(("plain",)).get_content(), msg.get_body(("html",)).get_content()
    assert LINK in text and LINK in html and "30 minutes" in text
    assert "Ann &lt;b&gt;" in html and "<b>" not in html.split("Hi ")[1].split(",")[0]      # name is HTML-escaped


def test_ssl_mode_uses_smtp_ssl_without_starttls():
    server = MagicMock()
    with patch("smtplib.SMTP_SSL") as smtp_ssl, patch("smtplib.SMTP") as smtp:
        smtp_ssl.return_value.__enter__.return_value = server
        ok = _run(_smtp(SMTP_PORT=465, SMTP_SECURITY="ssl"), lambda: mailer.send_email("u@x.com", "s", "t"))
    assert ok is True and smtp_ssl.called and not smtp.called and not server.starttls.called


def test_smtp_failure_returns_false_and_never_raises():
    with patch("smtplib.SMTP", side_effect=OSError("connection refused")):
        assert _run(_smtp(), lambda: mailer.send_email("u@x.com", "s", "t")) is False
    server = MagicMock(); server.login.side_effect = Exception("535 bad credentials")
    with patch("smtplib.SMTP") as smtp:
        smtp.return_value.__enter__.return_value = server
        assert _run(_smtp(), lambda: mailer.send_email("u@x.com", "s", "t")) is False


def test_reset_tokens_are_random_and_only_hashes_are_comparable():
    a, b = resettokens.new_token(), resettokens.new_token()
    assert a != b and len(a) >= 40 and a.replace("-", "").replace("_", "").isalnum()
    assert resettokens.hash_token(a) == resettokens.hash_token(a) != resettokens.hash_token(b)
    assert len(resettokens.hash_token(a)) == 64 and a not in resettokens.hash_token(a)
