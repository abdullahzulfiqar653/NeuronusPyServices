from rest_framework import serializers

from NeuroMail.models.email import Email


class EmailTrashSerializer(serializers.Serializer):
    emails = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Email.objects.filter(is_deleted=False),
        pk_field=serializers.CharField(),
    )

    def __init__(self, *args, **kwargs):
        """
        Modifying the queryset of the emails field based on the request user.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if hasattr(request, "user") and request.user.is_authenticated:
            mailbox = self.context.get("mailbox")
            self.fields["emails"].queryset = mailbox.emails.filter(is_deleted=False)

    def update_emails_to_trash(self):
        emails = self.validated_data["emails"]
        emails_to_update = []
        for email in emails:
            email.email_type = Email.TRASH
            email.is_starred = False
            emails_to_update.append(email)

        if emails_to_update:
            Email.objects.bulk_update(
                emails_to_update, ["email_type", "primary_email_type", "is_starred"]
            )
        return emails

    def update_trash_to_emails(self):
        emails = self.validated_data["emails"]
        emails_to_update = []
        for email in emails:
            if email.email_type == Email.TRASH:
                email.email_type = email.primary_email_type
                emails_to_update.append(email)
        if emails_to_update:
            Email.objects.bulk_update(emails_to_update, ["email_type"])
        return emails

    def update_trash_to_delete(self):
        emails = self.validated_data["emails"]
        Email.objects.filter(id__in=[email.id for email in emails]).update(
            is_deleted=True
        )
        return emails
