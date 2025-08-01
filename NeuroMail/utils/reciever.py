import secrets
from django.core.files.base import ContentFile

from main.services.s3 import S3Service
from NeuroMail.models.email import Email
from NeuroMail.utils.imap_server import fetch_emails
from NeuroMail.models.email_recipient import EmailRecipient
from NeuroMail.models.email_attachment import EmailAttachment


def get_saved_uids(mailbox, type):
    return set(
        imap_uid.encode()
        for imap_uid in Email.objects.filter(
            mailbox=mailbox, primary_email_type=type
        ).values_list("imap_uid", flat=True)
        if imap_uid is not None
    )


def get_recieved_emails(mailbox, user):
    inbox_uids = get_saved_uids(mailbox, Email.INBOX)
    spam_uids = get_saved_uids(mailbox, Email.SPAM)
    emails = fetch_emails(mailbox.email, mailbox.password, inbox_uids, Email.INBOX)
    # spam_emails = fetch_emails(mailbox.email, mailbox.password, spam_uids, Email.SPAM)
    print(spam_uids)
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
                imap_uid=email["imap_uid"],
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
