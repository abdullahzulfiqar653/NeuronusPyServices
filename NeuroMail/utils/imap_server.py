import email
import imaplib
from django.conf import settings
from email.header import decode_header
from email import utils as email_utils

IMAP_SERVER = settings.MAIL_SERVER
IMAP_PORT = 993  # SSL

# ---------- Decoding helpers ----------


def safe_decode_bytes(b: bytes, declared_charset: str | None) -> str:
    """
    Try declared charset, then common fallbacks. Never raises; replaces bad bytes.
    """
    # Normalize common oddities
    if declared_charset:
        cs = declared_charset.strip().lower()
        if cs in {"utf8", "utf-8"}:
            declared_charset = "utf-8"
        elif cs in {"us-ascii", "ascii"}:
            declared_charset = "ascii"
        else:
            declared_charset = cs

    for charset in (declared_charset, "utf-8", "windows-1252", "latin-1"):
        if not charset:
            continue
        try:
            return b.decode(charset, errors="replace")
        except LookupError:
            # Unknown/invalid charset label; try next fallback
            continue
        except UnicodeDecodeError:
            continue

    # Absolute fallback
    return b.decode("utf-8", errors="replace")


def decode_mime_words(header_value: str | None) -> str:
    """
    RFC 2047 header decoder with robust charset fallbacks.
    """
    if not header_value:
        return ""
    decoded_parts = []
    for part, enc in decode_header(header_value):
        if isinstance(part, bytes):
            decoded_parts.append(safe_decode_bytes(part, enc))
        else:
            decoded_parts.append(part)
    return "".join(decoded_parts)


def decode_filename(part) -> str | None:
    """
    Decode filename from a MIME part, handling RFC 2231/2047 encodings.
    """
    raw = part.get_filename()
    if not raw:
        return None
    pieces = []
    for p, enc in decode_header(raw):
        if isinstance(p, bytes):
            pieces.append(safe_decode_bytes(p, enc))
        else:
            pieces.append(p)
    # sanitize spaces to underscores (kept from your original behavior)
    return "".join(pieces).replace(" ", "_")


def extract_recipients(header_value: str, recipient_type: str):
    """
    Expand addresses from a header into structured list entries.
    """
    out = []
    if not header_value:
        return out
    for name, addr in email_utils.getaddresses([header_value]):
        out.append(
            {
                "name": name,
                "email": addr,
                "recipient_type": recipient_type,
            }
        )
    return out


# ---------- Main fetch function ----------


def fetch_emails(username, password, saved_uids, type="inbox"):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    try:
        mail.login(username, password)
        # Select mailbox (e.g., "inbox", "spam"). Many servers expect uppercase.
        mail.select(type)

        status, data = mail.uid("search", None, "ALL")
        if status != "OK" or not data or not data[0]:
            return []

        all_uids = set(data[0].split())
        email_uids = all_uids - saved_uids

        email_list = []

        for uid in email_uids:
            # Fetch full RFC822 and flags to decide seen status if you want
            res, msg_data = mail.fetch(uid, "(RFC822 FLAGS)")
            # Mark as seen (kept from your original)
            mail.store(uid, "+FLAGS", "\\Seen")

            if res != "OK":
                continue

            for response_part in msg_data:
                if not isinstance(response_part, tuple) or not response_part[1]:
                    continue

                msg = email.message_from_bytes(response_part[1])

                # ----- Headers -----
                subject = decode_mime_words(msg.get("Subject"))
                from_hdr = decode_mime_words(msg.get("From", ""))
                to_hdr = decode_mime_words(msg.get("To", ""))
                cc_hdr = decode_mime_words(msg.get("Cc", ""))
                bcc_hdr = decode_mime_words(msg.get("Bcc", ""))

                recipients = (
                    extract_recipients(to_hdr, "to")
                    + extract_recipients(cc_hdr, "cc")
                    + extract_recipients(bcc_hdr, "bcc")
                    + extract_recipients(from_hdr, "from")
                )

                # ----- Body (prefer HTML if present, else plain) -----
                plain_body = ""
                html_body = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = (part.get_content_type() or "").lower()
                        disp = (part.get("Content-Disposition") or "").lower()

                        # Text bodies
                        if "attachment" not in disp and content_type in (
                            "text/plain",
                            "text/html",
                        ):
                            payload = part.get_payload(decode=True)
                            if isinstance(payload, bytes):
                                body_text = safe_decode_bytes(
                                    payload, part.get_content_charset()
                                )
                            else:
                                # Sometimes non-binary payloads are already str
                                body_text = str(payload) if payload is not None else ""

                            if content_type == "text/plain" and not plain_body:
                                plain_body = body_text
                            elif content_type == "text/html" and not html_body:
                                html_body = body_text

                        # Attachments
                        if "attachment" in disp:
                            filename = decode_filename(part)
                            if filename:
                                attachment_data = part.get_payload(decode=True) or b""
                                attachments = (
                                    email_list[-1]["attachments"] if email_list else []
                                )
                                # If we're not already constructing a message, stash to local and append later
                else:
                    payload = msg.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        plain_body = safe_decode_bytes(
                            payload, msg.get_content_charset()
                        )
                    else:
                        plain_body = str(payload) if payload is not None else ""

                # We need to walk again to gather attachments (kept separate for clarity)
                attachments = []
                if msg.is_multipart():
                    for part in msg.walk():
                        disp = (part.get("Content-Disposition") or "").lower()
                        if "attachment" in disp:
                            filename = decode_filename(part)
                            if not filename:
                                continue
                            content_type = (
                                part.get_content_type() or "application/octet-stream"
                            )
                            attachment_data = part.get_payload(decode=True) or b""
                            attachments.append(
                                {
                                    "filename": filename,
                                    "content_type": content_type,
                                    "data": attachment_data,
                                }
                            )

                # Choose body: HTML preferred if available, otherwise plain
                body = html_body if html_body else plain_body

                email_data = {
                    "imap_uid": uid.decode(errors="ignore"),
                    "body": body,
                    "subject": subject,
                    "is_seen": False,  # your API logic controls this flag; you already store \Seen on server
                    "email_type": type,
                    "recipients": recipients,
                    "attachments": attachments,
                }

                email_list.append(email_data)

        return email_list

    finally:
        try:
            mail.logout()
        except Exception:
            pass
