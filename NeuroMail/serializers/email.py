import json
import secrets
import mimetypes
from django.http import QueryDict
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from NeuroMail.utils.smtp_server import send_email

from main.services.s3 import S3Service
from NeuroMail.models.email import Email
from NeuroMail.threads import EmailSendThread
from NeuroMail.models.email_recipient import EmailRecipient
from NeuroMail.models.email_attachment import EmailAttachment
from NeuroMail.serializers.email_recipient import EmailRecipientSerializer
from NeuroMail.serializers.email_attachment import EmailAttachmentSerializer


class EmailSerializer(serializers.ModelSerializer):
    recipients = EmailRecipientSerializer(many=True)
    attachments = EmailAttachmentSerializer(many=True)

    class Meta:
        model = Email
        fields = [
            "id",
            "body",
            "subject",
            "is_seen",
            "created_at",
            "email_type",
            "is_starred",
            "recipients",
            "total_size",
            "attachments",
        ]
        read_only_fields = ["id", "total_size"]

    def run_validation(self, data):
        if isinstance(data, QueryDict):
            data = data.dict()

        if "recipients" in data and isinstance(data["recipients"], str):
            try:
                data["recipients"] = json.loads(data["recipients"])
                data["attachments"] = [
                    {"file": file} for file in self.initial_data.getlist("attachments")
                ]
            except json.JSONDecodeError:
                raise ValidationError({"recipients": "Invalid JSON format."})
        return super().run_validation(data)

    def validate(self, attrs):
        email_type = attrs.get("email_type")
        body = attrs.get("body", "").strip()
        subject = attrs.get("subject", "").strip()
        recipients = attrs.get("recipients", [])

        if email_type == Email.SENT:
            if not recipients or len(recipients) == 0:
                raise serializers.ValidationError(
                    {"recipients": "At least one recipient is required."}
                )

            if not body:
                raise serializers.ValidationError(
                    {"body": "The email body cannot be empty."}
                )

            if not subject:
                raise serializers.ValidationError(
                    {"subject": "The email subject cannot be empty."}
                )

        return super().validate(attrs)

    def create(self, validated_data):
     request = self.context.get("request")
     recipients_data = validated_data.pop("recipients", [])
     attachments_data = validated_data.pop("attachments", [])
     email_type = validated_data.get("email_type")

     if validated_data.get("is_seen"):
        del validated_data["is_seen"]

     if validated_data.get("is_starred"):
        del validated_data["is_starred"]

     if email_type not in (Email.DRAFT, Email.SENT):
        raise serializers.ValidationError(
            {"email_type": f"{email_type} is not a valid choice."}
        )

    # STEP 1: Temporarily remove body to append pixel later
     body_content = validated_data.pop("body", "")

    # STEP 2: Create email (without body)
     email = Email.objects.create(
        **validated_data,
        body="",  # Temporarily empty
        primary_email_type=email_type,
        mailbox=request.mailbox,
        is_seen=True,
    )

    # STEP 3: Append tracking pixel (only for SENT emails)
     if email_type == Email.SENT:
        pixel_url = request.build_absolute_uri(f"/api/track/{email.id}/")
        tracking_img = f'<img src="{pixel_url}" width="1" height="1" style="display:none;" />'
        body_content += tracking_img

    # STEP 4: Save updated body
     email.body = body_content
     email.save()

    # STEP 5: Upload attachments to S3
     s3_client = S3Service()
     attachments = []
     attachment_urls = []
     size = 0
     for attachment in attachments_data:
        file = attachment.get("file")
        content_type, _ = mimetypes.guess_type(file.name)
        size += file.size
        name = file.name.replace(" ", "_")
        s3_key = f"neuromail/{email.id}/{name}"
        s3_url = s3_client.upload_file(file, s3_key)
        attachment_urls.append(s3_client.generate_presigned_url(s3_url))
        attachments.append(
            EmailAttachment(
                id=f"{EmailAttachment.UID_PREFIX}{secrets.token_hex(6)}",
                mail=email,
                s3_url=s3_url,
                filename=name,
                content_type=content_type or "application/octet-stream",
            )
        )

    # STEP 6: Save recipients
     recipients = [
        EmailRecipient(
            id=f"{EmailRecipient.UID_PREFIX}{secrets.token_hex(6)}",
            mail=email,
            name=recipient_data.get("name", None),
            email=recipient_data["email"],
            recipient_type=recipient_data["recipient_type"],
        )
        for recipient_data in recipients_data
    ]

     email.total_size = size
     email.save()
     request.user.profile.add_size(size)
     EmailRecipient.objects.bulk_create(recipients)
     EmailAttachment.objects.bulk_create(attachments)
     if email_type == Email.SENT:
       EmailSendThread(
           send_email,
           validated_data["subject"],
           validated_data["body"],
           request.mailbox.email,
           request.mailbox.password,
           recipients_data,
           attachment_urls,
        ).start()

     return email

