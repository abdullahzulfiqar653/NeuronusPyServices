import os
import socket
import smtplib
import ssl
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional

import requests
from django.conf import settings
from urllib.parse import urlparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from NeuroMail.models.email import Email


# --------------------------
# Configuration
# --------------------------
SMTP_SERVER: str = settings.MAIL_SERVER  # e.g. "mail.scoolarc.com"
SMTP_PORT: int = getattr(settings, "MAIL_PORT", 587)  # 587 (STARTTLS) or 465 (SSL)
SMTP_TIMEOUT: int = getattr(settings, "MAIL_TIMEOUT", 15)  # seconds
SMTP_RETRIES: int = getattr(settings, "MAIL_RETRIES", 3)
SMTP_BACKOFF_SECONDS: int = getattr(settings, "MAIL_BACKOFF_SECONDS", 2)
ATTACH_TIMEOUT: int = getattr(settings, "MAIL_ATTACH_TIMEOUT", 30)

# Logging
logging.basicConfig(
    level=getattr(settings, "MAIL_LOG_LEVEL", logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# --------------------------
# Helpers
# --------------------------
def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _get_ipv4(hostname: str) -> Optional[str]:
    """Resolve hostname to first IPv4 address, or None if not found."""
    try:
        infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
        for fam, *_rest, sockaddr in infos:
            if fam == socket.AF_INET:
                return sockaddr[0]
    except Exception as e:
        logging.warning(f"DNS resolution failed for {hostname}: {e}")
    return None


def _connect_ipv4_with_sni(hostname: str, port: int, timeout: int) -> smtplib.SMTP:
    """
    Connect TCP to an IPv4 address (to avoid AAAA/IPv6 timeouts) but keep the SMTP
    object's _host as the original hostname so StartTLS uses correct SNI for cert validation.
    """
    ipv4 = _get_ipv4(hostname)
    if not ipv4:
        # Fall back to normal hostname connection (lets OS decide family)
        return smtplib.SMTP(hostname, port, timeout=timeout)

    server = smtplib.SMTP(timeout=timeout)
    # Connect underlying TCP to the IPv4 address
    server.connect(ipv4, port)
    # Preserve/force hostname for TLS SNI/cert validation
    server._host = hostname  # noqa: SLF001 (intentional internal attribute)
    return server


def _smtp_client(hostname: str, port: int, timeout: int) -> smtplib.SMTP:
    """
    Create an SMTP client:
      - 465: implicit TLS (SMTP_SSL) using hostname (for SNI)
      - others: connect via IPv4 when possible but keep hostname for SNI
    """
    if port == 465:
        context = ssl.create_default_context()
        return smtplib.SMTP_SSL(hostname, port, timeout=timeout, context=context)
    return _connect_ipv4_with_sni(hostname, port, timeout)


def _collect_emails(recipients: List[Dict], kind: str) -> List[str]:
    return [
        r.get("email")
        for r in recipients
        if r.get("recipient_type") == kind and r.get("email")
    ]


# --------------------------
# Public API
# --------------------------
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
    Send an email with subject/body/attachments via SMTP.

    recipients: list of dicts:
      [{"recipient_type": "to"|"cc"|"bcc", "email": "user@example.com"}, ...]

    attachments: list of presigned file URLs (HTTP[S]) to fetch and attach.
    """
    attachments = attachments or []

    # Build message (plain + HTML)
    msg = MIMEMultipart("alternative")
    msg["From"] = from_email
    msg["Subject"] = subject

    to_emails = _collect_emails(recipients, "to")
    cc_emails = _collect_emails(recipients, "cc")
    bcc_emails = _collect_emails(recipients, "bcc")
    all_recipients = to_emails + cc_emails + bcc_emails

    msg["To"] = ", ".join(to_emails)
    msg["Cc"] = ", ".join(cc_emails)

    # Attach body (plain fallback + HTML)
    msg.attach(MIMEText(body.strip(), "plain"))
    msg.attach(MIMEText(body, "html"))

    # Fetch and attach files
    for url in attachments:
        try:
            resp = requests.get(url, timeout=ATTACH_TIMEOUT)
            resp.raise_for_status()
            filename = os.path.basename(urlparse(url).path) or "attachment"
            part = MIMEApplication(resp.content, Name=filename)
            part["Content-Disposition"] = f'attachment; filename="{filename}"'
            msg.attach(part)
        except Exception as e:
            logging.error(f"Attachment fetch failed ({url}) at {_now_str()}: {e}")

    # Connect + send with retries
    last_err: Optional[Exception] = None
    logging.info(
        f"Connecting to SMTP {SMTP_SERVER}:{SMTP_PORT} (hostname SNI preserved)"
    )

    for attempt in range(1, SMTP_RETRIES + 1):
        server: Optional[smtplib.SMTP] = None
        try:
            server = _smtp_client(SMTP_SERVER, SMTP_PORT, SMTP_TIMEOUT)
            server.ehlo()

            # STARTTLS for non-465 ports
            if SMTP_PORT != 465:
                context = ssl.create_default_context()
                # starttls uses server._host (the hostname) for SNI/cert validation
                server.starttls(context=context)
                server.ehlo()

            server.login(from_email, password)
            server.sendmail(from_email, all_recipients, msg.as_string())

            logging.info(f"Email {email_id or ''} sent successfully at {_now_str()}")
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
                f"[Attempt {attempt}/{SMTP_RETRIES}] SMTP timeout at {_now_str()}: {e}"
            )

        except smtplib.SMTPAuthenticationError as e:
            # Wrong creds: no point retrying
            logging.error(f"SMTP auth failed for {from_email} at {_now_str()}: {e}")
            try:
                if server:
                    server.quit()
            finally:
                raise

        except ssl.SSLError as e:
            # Certificate/SNI issues surface here
            last_err = e
            logging.error(
                f"[Attempt {attempt}/{SMTP_RETRIES}] TLS/SSL error at {_now_str()}: {e}"
            )

        except smtplib.SMTPException as e:
            last_err = e
            logging.error(
                f"[Attempt {attempt}/{SMTP_RETRIES}] SMTP error at {_now_str()}: {e}"
            )

        except Exception as e:
            last_err = e
            logging.error(
                f"[Attempt {attempt}/{SMTP_RETRIES}] Unexpected error at {_now_str()}: {e}"
            )

        finally:
            try:
                if server:
                    server.quit()
            except Exception:
                pass

        # Backoff before next attempt
        time.sleep(SMTP_BACKOFF_SECONDS * attempt)

    # All retries failed
    raise RuntimeError(
        f"Failed to send email {email_id or ''} after {SMTP_RETRIES} attempts at {_now_str()}: {last_err}"
    )


# COAT FRUIT TABLE UNDER JELLY OPERA CHALK HANDS CHALK JEEP NAME XEROX EIGHT AIM ZOOM ELEPHANT
