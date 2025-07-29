import email
import imaplib
from django.conf import settings
from email.header import decode_header
from NeuroMail.models import Email, EmailRecipient, EmailAttachment
from django.core.files.base import ContentFile
from django.utils import timezone


IMAP_SERVER = settings.MAIL_SERVER
IMAP_PORT = 993


def decode_mime_words(mime_words):
    decoded_string = ""
    for word, encoding in decode_header(mime_words):
        if isinstance(word, bytes):
            word = word.decode(encoding if encoding else "utf-8", errors="ignore")
        decoded_string += word
    return decoded_string


def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" and part.get_content_disposition() is None:
                charset = part.get_content_charset() or "utf-8"
                body += part.get_payload(decode=True).decode(charset, errors="ignore")
                break
    else:
        charset = msg.get_content_charset() or "utf-8"
        body += msg.get_payload(decode=True).decode(charset, errors="ignore")
    return body


def save_attachments(email_obj, msg):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue

        filename = part.get_filename()
        if filename:
            filename = decode_mime_words(filename)
            file_content = part.get_payload(decode=True)
            attachment = EmailAttachment(
                email=email_obj,
                filename=filename,
                content_type=part.get_content_type()
            )
            attachment.file.save(filename, ContentFile(file_content), save=True)


def connect_to_imap():
    try:
        imap_server = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        imap_server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        return imap_server
    except Exception as e:
        print(f"IMAP connection failed: {e}")
        return None


def fetch_inbox_emails():
    imap_server = connect_to_imap()
    if not imap_server:
        return

    imap_server.select("inbox")
    status, email_ids = imap_server.search(None, "ALL")
    email_ids = email_ids[0].split()

    for e_id in email_ids:
        imap_id = e_id.decode()
        if Email.objects.filter(imap_id=imap_id).exists():
            continue

        _, data = imap_server.fetch(e_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        email_obj = Email.objects.create(
            imap_id=imap_id,
            subject=decode_mime_words(msg.get("Subject")),
            sender=decode_mime_words(msg.get("From")),
            recipients=decode_mime_words(msg.get("To")),
            cc=decode_mime_words(msg.get("Cc")),
            bcc=decode_mime_words(msg.get("Bcc")),
            date=msg.get("Date"),
            body=get_email_body(msg),
        )

        save_attachments(email_obj, msg)

    imap_server.logout()


def fetch_spam_emails():
    imap_server = connect_to_imap()
    if not imap_server:
        return

    for spam_folder in ['[Gmail]/Spam', 'Spam', 'Junk']:
        try:
            imap_server.select(spam_folder)
            status, email_ids = imap_server.search(None, "ALL")
            email_ids = email_ids[0].split()

            for e_id in email_ids:
                imap_id = e_id.decode()
                if Email.objects.filter(imap_id=imap_id).exists():
                    continue

                _, data = imap_server.fetch(e_id, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                email_obj = Email.objects.create(
                    imap_id=imap_id,
                    subject=decode_mime_words(msg.get("Subject")),
                    sender=decode_mime_words(msg.get("From")),
                    recipients=decode_mime_words(msg.get("To")),
                    cc=decode_mime_words(msg.get("Cc")),
                    bcc=decode_mime_words(msg.get("Bcc")),
                    date=msg.get("Date"),
                    body=get_email_body(msg),
                    is_spam=True,
                )

                save_attachments(email_obj, msg)

            break
        except Exception:
            continue

    imap_server.logout()
