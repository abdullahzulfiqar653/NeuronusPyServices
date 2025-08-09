import os
import socket
import smtplib
import ssl
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import requests
from django.conf import settings
from urllib.parse import urlparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from NeuroMail.models.email import Email

# --------------------------
# Config (override via Django settings if you want)
# --------------------------
SMTP_SERVER: str = getattr(settings, "MAIL_SERVER", "mail.scoolarc.com")
# Ordered candidates: (port, mode) mode is "starttls" or "ssl"
SMTP_CANDIDATES: List[Tuple[int, str]] = getattr(
    settings,
    "MAIL_PORT_CANDIDATES",
    [(587, "starttls"), (465, "ssl"), (2525, "starttls")],
)
# Short timeouts so we fail fast and try next candidate
SMTP_TIMEOUT_CONNECT: int = getattr(settings, "MAIL_TIMEOUT_CONNECT", 7)
SMTP_TIMEOUT_OPS: int = getattr(settings, "MAIL_TIMEOUT_OPS", 15)
SMTP_RETRIES_PER_CANDIDATE: int = getattr(settings, "MAIL_RETRIES_PER_CANDIDATE", 1)
SMTP_BACKOFF_SECONDS: int = getattr(settings, "MAIL_BACKOFF_SECONDS", 2)
ATTACH_TIMEOUT: int = getattr(settings, "MAIL_ATTACH_TIMEOUT", 30)

logging.basicConfig(
    level=getattr(settings, "MAIL_LOG_LEVEL", logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _get_ipv4(hostname: str) -> Optional[str]:
    try:
        infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
        for fam, *_rest, sockaddr in infos:
            if fam == socket.AF_INET:
                return sockaddr[0]
    except Exception as e:
        logging.warning(f"DNS resolution failed for {hostname}: {e}")
    return None


def _connect_ipv4_preserve_sni(hostname: str, port: int, timeout: int) -> smtplib.SMTP:
    """
    Connect TCP to IPv4 to avoid possible IPv6 issues, but preserve the hostname
    for SNI/cert validation during TLS handshake.
    """
    ipv4 = _get_ipv4(hostname)
    if not ipv4:
        return smtplib.SMTP(hostname, port, timeout=timeout)
    server = smtplib.SMTP(timeout=timeout)
    server.connect(ipv4, port)  # TCP connect to IPv4
    server._host = hostname  # preserve hostname for SNI
    return server


def _smtp_open(hostname: str, port: int, mode: str) -> smtplib.SMTP:
    """
    Open an SMTP connection with short connect timeout.
    mode: "starttls" (submission) or "ssl" (implicit TLS).
    """
    if mode == "ssl":
        context = ssl.create_default_context()
        # SMTP_SSL takes its own timeout (connect+ops)
        return smtplib.SMTP_SSL(
            hostname, port, timeout=SMTP_TIMEOUT_CONNECT, context=context
        )

    # starttls path
    return _connect_ipv4_preserve_sni(hostname, port, SMTP_TIMEOUT_CONNECT)


def _collect(recipients: List[Dict], kind: str) -> List[str]:
    return [
        r.get("email")
        for r in recipients
        if r.get("recipient_type") == kind and r.get("email")
    ]


def send_email(
    subject: str,
    body: str,
    from_email: str,
    password: str,
    recipients: List[Dict],
    attachments: Optional[List[str]] = None,
    email_id: Optional[str] = None,
) -> None:
    """
    recipients: [{"recipient_type": "to"|"cc"|"bcc", "email": "user@example.com"}, ...]
    attachments: list of HTTP(S) URLs to fetch and attach.
    """
    attachments = attachments or []

    # Build message (plain + HTML)
    msg = MIMEMultipart("alternative")
    msg["From"] = from_email
    msg["Subject"] = subject

    to_emails = _collect(recipients, "to")
    cc_emails = _collect(recipients, "cc")
    bcc_emails = _collect(recipients, "bcc")
    all_rcpts = to_emails + cc_emails + bcc_emails

    msg["To"] = ", ".join(to_emails)
    msg["Cc"] = ", ".join(cc_emails)

    msg.attach(MIMEText(body.strip(), "plain"))
    msg.attach(MIMEText(body, "html"))

    # Attachments
    for url in attachments:
        try:
            resp = requests.get(url, timeout=ATTACH_TIMEOUT)
            resp.raise_for_status()
            filename = os.path.basename(urlparse(url).path) or "attachment"
            part = MIMEApplication(resp.content, Name=filename)
            part["Content-Disposition"] = f'attachment; filename="{filename}"'
            msg.attach(part)
        except Exception as e:
            logging.error(f"Attachment fetch failed ({url}) at {_now()}: {e}")

    last_err: Optional[Exception] = None

    # Try candidate ports/modes in order
    for port, mode in SMTP_CANDIDATES:
        logging.info(f"Attempting SMTP {mode.upper()} on {SMTP_SERVER}:{port}")
        for attempt in range(1, SMTP_RETRIES_PER_CANDIDATE + 1):
            server: Optional[smtplib.SMTP] = None
            try:
                server = _smtp_open(SMTP_SERVER, port, mode)
                server.ehlo()

                if mode == "starttls":
                    context = ssl.create_default_context()
                    # Switch to operation timeout for subsequent ops
                    server.timeout = SMTP_TIMEOUT_OPS
                    server.starttls(context=context)  # SNI uses preserved hostname
                    server.ehlo()
                else:
                    # SMTP_SSL already created; set op timeout
                    try:
                        server.sock.settimeout(SMTP_TIMEOUT_OPS)  # type: ignore[attr-defined]
                    except Exception:
                        pass

                server.login(from_email, password)
                server.sendmail(from_email, all_rcpts, msg.as_string())

                logging.info(
                    f"Email {email_id or ''} sent successfully at {_now()} via {mode.upper()} {port}"
                )
                if email_id:
                    Email.objects.filter(id=email_id).update(is_sent_success=True)

                try:
                    server.quit()
                except Exception:
                    pass
                return

            except (socket.timeout, TimeoutError) as e:
                last_err = e
                logging.error(
                    f"[{mode.upper()} {port}] connect/IO timeout at {_now()}: {e}"
                )

            except ssl.SSLError as e:
                last_err = e
                logging.error(f"[{mode.upper()} {port}] TLS error at {_now()}: {e}")

            except smtplib.SMTPAuthenticationError as e:
                logging.error(
                    f"[{mode.upper()} {port}] SMTP auth failed for {from_email} at {_now()}: {e}"
                )
                try:
                    if server:
                        server.quit()
                finally:
                    raise

            except smtplib.SMTPException as e:
                last_err = e
                logging.error(f"[{mode.upper()} {port}] SMTP error at {_now()}: {e}")

            except Exception as e:
                last_err = e
                logging.error(
                    f"[{mode.upper()} {port}] Unexpected error at {_now()}: {e}"
                )

            finally:
                try:
                    if server:
                        server.quit()
                except Exception:
                    pass

            time.sleep(SMTP_BACKOFF_SECONDS * attempt)

        logging.info(f"Moving to next candidate after {mode.upper()} {port}")

    raise RuntimeError(
        f"Failed to send email {email_id or ''} via {SMTP_SERVER} after trying {SMTP_CANDIDATES} at {_now()}: {last_err}"
    )
