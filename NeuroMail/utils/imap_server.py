import email
import imaplib
from django.conf import settings
from email.header import decode_header

IMAP_SERVER = settings.MAIL_SERVER
IMAP_PORT = 993  # Use 993 for SSL


def decode_mime_words(mime_words):
    decoded_string = ""
    for word, encoding in decode_header(mime_words):
        if isinstance(word, bytes):
            word = word.decode(encoding if encoding else "utf-8")
        decoded_string += word
    return decoded_string


def fetch_emails(username, password, existing_imap_ids, email_type):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(username, password)
    mail.select(email_type)

    # Search for unread emails
    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()
    email_list = []  # List to store email data
    for e_id in email_ids:
        res, msg_data = mail.fetch(e_id, "(RFC822)")
        mail.store(e_id, "+FLAGS", "\\Seen")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                imap_id = (
                    msg.get("Message-ID") or e_id.decode()
                )  # this is the unique email ID
                if imap_id in existing_imap_ids:
                    continue

                subject = decode_mime_words(msg["Subject"])
                from_email = decode_mime_words(msg.get("From", ""))
                to_emails = decode_mime_words(msg.get("To", ""))
                cc_emails = decode_mime_words(msg.get("Cc", ""))
                bcc_emails = decode_mime_words(msg.get("Bcc", ""))

                # Helper function to clean and separate emails from names
                def extract_emails(email_string, recipient_type):
                    email_list = []
                    if email_string:
                        addresses = email.utils.getaddresses([email_string])
                        for name, email_addr in addresses:
                            email_list.append(
                                {
                                    "name": name,
                                    "email": email_addr,
                                    "recipient_type": recipient_type,
                                }
                            )
                    return email_list

                recipients = (
                    extract_emails(to_emails, "to")
                    + extract_emails(cc_emails, "cc")
                    + extract_emails(bcc_emails, "bcc")
                    + extract_emails(from_email, "from")
                )

                body = ""
                attachments = []  # List to store attachment data

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        # Get plain text body if exists
                        if (
                            content_type == "text/plain"
                            and "attachment" not in content_disposition
                        ):
                            body = part.get_payload(decode=True).decode()

                        # Get HTML body if exists
                        elif (
                            content_type == "text/html"
                            and "attachment" not in content_disposition
                        ):
                            body = part.get_payload(decode=True).decode()

                        # Handle attachments
                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                attachment_data = part.get_payload(decode=True)
                                attachments.append(
                                    {
                                        "filename": filename,
                                        "content_type": content_type,
                                        "data": attachment_data,
                                    }
                                )
                else:
                    body = msg.get_payload(decode=True).decode()

                # Structuring the email data into a dictionary
                email_data = {
                    "imap_id": imap_id,
                    "body": body,
                    "subject": subject,
                    "is_seen": False,  # since you're fetching unseen emails
                    "email_type": email_type,
                    "recipients": recipients,
                    "attachments": attachments,  # Attachments list
                }

                # Add the structured email data to the email list
                email_list.append(email_data)

    mail.logout()
    return email_list
