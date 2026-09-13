"""Optional email when a family writes in."""
from __future__ import annotations

import smtplib
from email.message import EmailMessage

from db import settings_map


def notify(subject: str, body: str) -> None:
    s = settings_map()
    to = (s.get("notify_email") or s.get("email") or "").strip()
    host = (s.get("smtp_host") or "").strip()
    user = (s.get("smtp_user") or "").strip()
    password = (s.get("smtp_pass") or "").strip()
    port = int(s.get("smtp_port") or "587")
    if not to or not host or not user:
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, port, timeout=12) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
    except Exception:
        pass
