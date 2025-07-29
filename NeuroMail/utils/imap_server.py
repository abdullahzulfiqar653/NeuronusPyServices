import email
import imaplib
from django.conf import settings
from email.header import decode_header
from NeuroMail.models import Email, EmailRecipient, EmailAttachment
from django.core.files.base import ContentFile
from django.utils import timezone

IMAP_SERVER = settings.MAIL_SERVER
IMAP_PORT = 993  # SSL Port


def decode_mime_words(mime_words):
    decoded_string = ""
    for word, encoding in decode_header(mime_words):
        if isinstance(word, bytes):
            word = word.decode(encoding if encoding else "utf-8")
        decoded_string += word
    return decoded_string


def extract_emails(email_string, recipient_type):
    result = []
    if email_string:
        addresses = email.utils.getaddresses([email_string])
        for name, email_addr in addresses:
            result.append({
                "name": name,
                "email": email_addr,
                "recipient_type": recipient_type
            })
    return result


def fetch_inbox_emails(username, password):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(username, password)
    mail.select("inbox")

    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    for e_id in email_ids:
        res, msg_data = mail.fetch(e_id, "(RFC822)")
        mail.store(e_id, "+FLAGS", "\\Seen")  # Mark as seen

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                subject = decode_mime_words(msg.get("Subject", ""))
                from_email = decode_mime_words(msg.get("From", ""))
                to_emails = decode_mime_words(msg.get("To", ""))
                cc_emails = decode_mime_words(msg.get("Cc", ""))
                bcc_emails = decode_mime_words(msg.get("Bcc", ""))

                all_recipients = (
                    extract_emails(to_emails, "to") +
                    extract_emails(cc_emails, "cc") +
                    extract_emails(bcc_emails, "bcc") +
                    extract_emails(from_email, "from")
                )

                body = ""
                attachments = []

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                        elif content_type == "text/html" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode(errors="ignore")

                        # Handle attachments
                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                decoded_filename = decode_mime_words(filename)
                                file_data = part.get_payload(decode=True)
                                attachments.append({
                                    "filename": decoded_filename,
                                    "content_type": content_type,
                                    "data": file_data
                                })
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                # 📨 Save Email object
                email_obj = Email.objects.create(
                    subject=subject,
                    body=body,
                    is_seen=False,
                    email_type="inbox",
                    created_at=timezone.now(),
                )

                # 👥 Save recipients (to/from/cc/bcc)
                for r in all_recipients:
                    EmailRecipient.objects.create(
                        email=email_obj,
                        name=r["name"],
                        email_address=r["email"],
                        recipient_type=r["recipient_type"],
                    )

                # 📎 Save attachments
                for attachment in attachments:
                    EmailAttachment.objects.create(
                        email=email_obj,
                        filename=attachment["filename"],
                        content_type=attachment["content_type"],
                        file=ContentFile(attachment["data"], name=attachment["filename"]),
                    )

    mail.logout()
    
def fetch_spam_emails(username, password):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(username, password)
    
    # 🗂 Select spam folder
    status, _ = mail.select("[Gmail]/Spam")  # Gmail spam folder
    if status != "OK":
        print("Couldn't open spam folder")
        return

    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    for e_id in email_ids:
        res, msg_data = mail.fetch(e_id, "(RFC822)")
        mail.store(e_id, "+FLAGS", "\\Seen")  # Mark as seen

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                subject = decode_mime_words(msg.get("Subject", ""))
                from_email = decode_mime_words(msg.get("From", ""))
                to_emails = decode_mime_words(msg.get("To", ""))
                cc_emails = decode_mime_words(msg.get("Cc", ""))
                bcc_emails = decode_mime_words(msg.get("Bcc", ""))

                all_recipients = (
                    extract_emails(to_emails, "to") +
                    extract_emails(cc_emails, "cc") +
                    extract_emails(bcc_emails, "bcc") +
                    extract_emails(from_email, "from")
                )

                body = ""
                attachments = []

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                        elif content_type == "text/html" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode(errors="ignore")

                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                decoded_filename = decode_mime_words(filename)
                                file_data = part.get_payload(decode=True)
                                attachments.append({
                                    "filename": decoded_filename,
                                    "content_type": content_type,
                                    "data": file_data
                                })
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                # 📩 Save as spam email
                email_obj = Email.objects.create(
                    subject=subject,
                    body=body,
                    is_seen=False,
                    email_type="spam",  # 🔄 email_type changed from inbox to spam
                    created_at=timezone.now(),
                )

                for r in all_recipients:
                    EmailRecipient.objects.create(
                        email=email_obj,
                        name=r["name"],
                        email_address=r["email"],
                        recipient_type=r["recipient_type"],
                    )

                for attachment in attachments:
                    EmailAttachment.objects.create(
                        email=email_obj,
                        filename=attachment["filename"],
                        content_type=attachment["content_type"],
                        file=ContentFile(attachment["data"], name=attachment["filename"]),
                    )

    mail.logout()
