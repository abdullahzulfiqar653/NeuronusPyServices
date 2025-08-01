import secrets
from django.core.files.base import ContentFile
from imap_server import fetch_emails
from main.services.s3 import S3Service
from NeuroMail.models.email import Email
from NeuroMail.models.email_recipient import EmailRecipient
from NeuroMail.models.email_attachment import EmailAttachment


def get_recieved_emails(mailbox, user):
    saved_inbox_imap_ids = set(
        Email.objects.filter(mailbox=mailbox, email_type=Email.INBOX).values_list(
            "imap_id", flat=True
        )
    )
    saved_spam_imap_ids = set(
        Email.objects.filter(mailbox=mailbox, email_type=Email.SPAM).values_list(
            "imap_id", flat=True
        )
    )

    inbox_emails = fetch_emails(
        mailbox.email, mailbox.password, saved_inbox_imap_ids, Email.INBOX
    )
    spam_emails = fetch_emails(
        mailbox.email, mailbox.password, saved_spam_imap_ids, Email.SPAM
    )
    emails = inbox_emails + spam_emails
    new_emails = []
    recipients = []
    attachments = []
    total_emails_size = 0
    if emails:
        for email in emails:
            total_size = len(email["body"].encode("utf-8"))  # Size of body in bytes
            new_email = Email(
                id=f"{Email.UID_PREFIX}{secrets.token_hex(6)}",
                mailbox=mailbox,
                body=email["body"],
                is_seen=email["is_seen"],
                subject=email["subject"],
                imap_id=email["imap_id"],
                email_type=email["email_type"],
                primary_email_type=email["email_type"],
            )
            s3_client = S3Service()
            new_emails.append(new_email)
            for recipient in email["recipients"]:
                recipients.append(
                    EmailRecipient(
                        id=f"{EmailRecipient.UID_PREFIX}{secrets.token_hex(6)}",
                        mail=new_email,
                        **recipient,
                    )
                )
            # Create attachments
            for attachment in email.get("attachments", []):
                attachment_size = len(attachment["data"])
                total_size += attachment_size
                filename = attachment["filename"].replace(" ", "_")
                s3_key = f"neuromail/{new_email.id}/{filename}"
                s3_url = s3_client.upload_file(
                    ContentFile(attachment["data"], name=attachment["filename"]),
                    s3_key,
                )
                attachments.append(
                    EmailAttachment(
                        id=f"{EmailAttachment.UID_PREFIX}{secrets.token_hex(6)}",
                        s3_url=s3_url,
                        mail=new_email,
                        filename=filename,
                        content_type=attachment["content_type"],
                    )
                )
            new_email.total_size = total_size
            total_emails_size += total_size
        user.profile.add_size(total_emails_size)
        Email.objects.bulk_create(new_emails)
        EmailRecipient.objects.bulk_create(recipients)
        EmailAttachment.objects.bulk_create(attachments)
