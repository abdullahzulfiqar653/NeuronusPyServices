from rest_framework.response import Response
from rest_framework import generics, status, filters
from django_filters.rest_framework import DjangoFilterBackend

from NeuroMail.models.email import Email
from NeuroMail.models.mailbox import MailBox

from NeuroMail.serializers.email import EmailSerializer
from NeuroMail.serializers.email_trash import EmailTrashSerializer
from NeuroMail.serializers.email_starred import EmailUpdateSerializer
from NeuroMail.serializers.email_attachment import EmailAttachmentSerializer

from main.services.s3 import S3Service
from NeuroMail.permissions import IsMailBoxOwner, IsEmailOwner
from NeuroMail.utils.reciever import get_recieved_emails


class MailboxEmailListCreateView(generics.ListCreateAPIView):
    """THis API used to create emails of type [sent, draft] and use to list emails of all types"""

    queryset = Email.objects.none()
    serializer_class = EmailSerializer
    search_fields = ["subject", "body"]
    permission_classes = [IsMailBoxOwner]
    filterset_fields = ["email_type", "is_starred", "is_seen"]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    def get_queryset(self):
        mailbox = self.request.mailbox
        email_type = self.request.query_params.get("email_type")
        if email_type in [Email.INBOX, Email.SPAM]:
            get_recieved_emails(mailbox, self.request.user)
        return mailbox.emails.filter(is_deleted=False).order_by("-created_at")


class MailboxEmailRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """THis API use to fetch signle email data or to mark it as starred or seen"""

    permission_classes = [IsMailBoxOwner]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return EmailUpdateSerializer
        return EmailSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return MailBox.objects.none()
        return self.request.mailbox.emails.filter(is_deleted=False)


class MailboxEmailMoveToTrashView(generics.UpdateAPIView):
    """APIs to move emails to trash by sending list of email ids"""

    serializer_class = EmailTrashSerializer
    permission_classes = [IsMailBoxOwner]

    def update(self, request, *args, **kwargs):
        mailbox = self.request.mailbox
        serializer = self.get_serializer(
            data=request.data, context={"request": request, "mailbox": mailbox}
        )

        if serializer.is_valid():
            serializer.update_emails_to_trash()
            return Response(
                {"message": "Emails moved to trash successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MailboxEmailRestoreFromTrashView(generics.UpdateAPIView):
    """APIs to restore emails from trash by sending list of email ids"""

    serializer_class = EmailTrashSerializer
    permission_classes = [IsMailBoxOwner]

    def update(self, request, *args, **kwargs):
        mailbox = self.request.mailbox
        serializer = self.get_serializer(
            data=request.data, context={"request": request, "mailbox": mailbox}
        )

        if serializer.is_valid():
            serializer.update_trash_to_emails()
            return Response(
                {"message": "Emails restored from trash successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MailboxEmailDeleteFromTrashView(generics.UpdateAPIView):
    """APIs to delete emails from trash by sending list of email ids"""

    serializer_class = EmailTrashSerializer
    permission_classes = [IsMailBoxOwner]

    def update(self, request, *args, **kwargs):
        mailbox = self.request.mailbox
        serializer = self.get_serializer(
            data=request.data, context={"request": request, "mailbox": mailbox}
        )

        if serializer.is_valid():
            serializer.update_trash_to_delete()
            return Response(
                {"message": "Emails Deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"error": "unable to delete emails, please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class EmailFileRetrieveView(generics.RetrieveAPIView):
    queryset = Email.objects.filter(is_deleted=False)
    permission_classes = [IsEmailOwner]
    serializer_class = EmailAttachmentSerializer

    def get(self, request, *args, **kwargs):
        attachment_id = kwargs["pk"]
        """
        Retrieve email attachments for a given email, generate presigned URLs for each.
        """
        try:
            attachment = request.email.attachments.get(id=attachment_id)
        except:
            return Response(
                {"detail": "Attachment not found."}, status=status.HTTP_404_NOT_FOUND
            )
        s3_client = S3Service()
        return Response(
            {"url": s3_client.generate_presigned_url(attachment.s3_url)}, status=200
        )
