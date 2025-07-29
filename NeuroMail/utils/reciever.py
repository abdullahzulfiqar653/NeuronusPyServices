import secrets
from django.core.files.base import ContentFile
from main.services.s3 import S3Service
from NeuroMail.models.email import Email
from NeuroMail.models.email_recipient import EmailRecipient
from NeuroMail.models.email_attachment import EmailAttachment
from NeuroMail.utils.imap_server import fetch_inbox_emails
from NeuroMail.utils.imap_server import fetch_spam_emails


def get_recieved_emails(mailbox, user):
    emails = fetch_inbox_emails(mailbox.email, mailbox.password)
    new_emails = []
    recipients = []
    attachments = []
    total_emails_size = 0

    if emails:
        s3_client = S3Service()

        for email_data in emails:
            # Create Email instance
            new_email = Email(
                id=f"{Email.UID_PREFIX}{secrets.token_hex(6)}",
                mailbox=mailbox,
                subject=email_data.get("subject", ""),
                body=email_data.get("body", ""),
                is_seen=email_data.get("is_seen", False),
                email_type=email_data.get("email_type", Email.INBOX),
                primary_email_type=email_data.get("email_type", Email.INBOX),
                uid=secrets.token_hex(16),
            )
            total_size = len(new_email.body.encode("utf-8"))

            # Create Recipient instances
            for recipient_data in email_data.get("recipients", []):
                recipients.append(
                    EmailRecipient(
                        id=f"{EmailRecipient.UID_PREFIX}{secrets.token_hex(6)}",
                        mail=new_email,
                        **recipient_data,
                    )
                )

            # Create Attachment instances
            for attachment in email_data.get("attachments", []):
                filename = attachment["filename"].replace(" ", "_")
                attachment_data = attachment["data"]
                s3_key = f"neuromail/{new_email.id}/{filename}"

                # Upload to S3
                s3_url = s3_client.upload_file(
                    ContentFile(attachment_data, name=filename),
                    s3_key,
                )

                attachments.append(
                    EmailAttachment(
                        id=f"{EmailAttachment.UID_PREFIX}{secrets.token_hex(6)}",
                        mail=new_email,
                        s3_url=s3_url,
                        filename=filename,
                        content_type=attachment["content_type"],
                    )
                )

                total_size += len(attachment_data)

            new_email.total_size = total_size
            new_emails.append(new_email)
            total_emails_size += total_size

        # Save all data in bulk
        Email.objects.bulk_create(new_emails)
        EmailRecipient.objects.bulk_create(recipients)
        EmailAttachment.objects.bulk_create(attachments)

        # Add total size to user profile
        user.profile.add_size(total_emails_size)

def get_spam_emails(mailbox, user):
    emails = fetch_spam_emails(mailbox.email, mailbox.password)
    new_emails = []
    recipients = []
    attachments = []
    total_emails_size = 0

    if emails:
        s3_client = S3Service()

        for email_data in emails:
            new_email = Email(
                id=f"{Email.UID_PREFIX}{secrets.token_hex(6)}",
                mailbox=mailbox,
                subject=email_data.get("subject", ""),
                body=email_data.get("body", ""),
                is_seen=email_data.get("is_seen", False),
                email_type=Email.SPAM,
                primary_email_type=Email.SPAM,
                uid=secrets.token_hex(16),
            )
            total_size = len(new_email.body.encode("utf-8"))

            for recipient_data in email_data.get("recipients", []):
                recipients.append(
                    EmailRecipient(
                        id=f"{EmailRecipient.UID_PREFIX}{secrets.token_hex(6)}",
                        mail=new_email,
                        **recipient_data,
                    )
                )

            for attachment in email_data.get("attachments", []):
                filename = attachment["filename"].replace(" ", "_")
                attachment_data = attachment["data"]
                s3_key = f"neuromail/{new_email.id}/{filename}"

                s3_url = s3_client.upload_file(
                    ContentFile(attachment_data, name=filename),
                    s3_key,
                )

                attachments.append(
                    EmailAttachment(
                        id=f"{EmailAttachment.UID_PREFIX}{secrets.token_hex(6)}",
                        mail=new_email,
                        s3_url=s3_url,
                        filename=filename,
                        content_type=attachment["content_type"],
                    )
                )

                total_size += len(attachment_data)

            new_email.total_size = total_size
            new_emails.append(new_email)
            total_emails_size += total_size

        Email.objects.bulk_create(new_emails)
        EmailRecipient.objects.bulk_create(recipients)
        EmailAttachment.objects.bulk_create(attachments)

        user.profile.add_size(total_emails_size)