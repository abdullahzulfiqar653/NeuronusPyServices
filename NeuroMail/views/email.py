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
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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

    @swagger_auto_schema(
        operation_summary="List emails for mailbox",
        operation_description=(
            "Returns all emails belonging to the current mailbox.\n\n"
            "Supports filters:\n"
            "- `email_type`: inbox, sent, draft, trash, Junk\n\n"
            "- `is_starred`: true/false\n\n"
            "- `is_seen`: true/false\n\n"
            "- `search`: keyword in subject or body"
        ),
        manual_parameters=[
            openapi.Parameter(
                "email_type",
                openapi.IN_QUERY,
                description="Filter by email type (inbox, sent, draft, trash, Junk)",
                type=openapi.TYPE_STRING,
                enum=[Email.INBOX, Email.SENT, Email.DRAFT, Email.TRASH, Email.SPAM],
            ),
            openapi.Parameter(
                "is_starred",
                openapi.IN_QUERY,
                description="Filter by starred status",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "is_seen",
                openapi.IN_QUERY,
                description="Filter by seen status",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search in subject or body",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: EmailSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create an email (sent or draft)",
        operation_description=(
            "Creates a new email of type `sent` or `draft`.\n\n"
            "**For `sent` emails:**\n"
            "- Requires at least one recipient\n\n"
            "- `subject` and `body` must be non-empty\n\n"
            "- `attachments` and `recipients` must be passed as JSON (if stringified) or directly in multipart/form-data.\n\n"
            "**Attachments will be uploaded to S3** and linked to the email.\n\n"
            "**Note:** Tracking pixel is appended to body for sent emails."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["subject", "body", "email_type", "recipients"],
            properties={
                "subject": openapi.Schema(
                    type=openapi.TYPE_STRING, example="Meeting Update"
                ),
                "body": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="Dear team, the meeting is rescheduled...",
                ),
                "email_type": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["sent", "draft"]
                ),
                "recipients": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "email": openapi.Schema(
                                type=openapi.TYPE_STRING, example="user@example.com"
                            ),
                            "name": openapi.Schema(
                                type=openapi.TYPE_STRING, example="John Doe"
                            ),
                            "recipient_type": openapi.Schema(
                                type=openapi.TYPE_STRING, enum=["to", "cc", "bcc"]
                            ),
                        },
                    ),
                ),
                "attachments": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING, format="binary"),
                    description="Files uploaded as multipart/form-data.",
                ),
            },
        ),
        responses={
            201: EmailSerializer(),
            400: openapi.Response(
                description="Validation failed",
                examples={
                    "application/json": {
                        "recipients": ["At least one recipient is required."],
                        "subject": ["The email subject cannot be empty."],
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MailboxEmailRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsMailBoxOwner]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return EmailUpdateSerializer
        return EmailSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return MailBox.objects.none()
        return self.request.mailbox.emails.filter(is_deleted=False)

    @swagger_auto_schema(
        operation_summary="Retrieve a single email",
        operation_description=(
            "Fetch details of a single email including subject, body, recipients, "
            "attachments, and status fields like `is_seen`, `is_starred`, etc."
        ),
        responses={200: EmailSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update email status",
        operation_description=(
            "Update limited fields of an email — typically used to mark an email as "
            "starred or seen.\n\n"
            "**Allowed fields:**\n- `is_starred`\n\n- `is_seen`"
        ),
        request_body=EmailUpdateSerializer,
        responses={200: EmailSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class MailboxEmailMoveToTrashView(generics.UpdateAPIView):
    permission_classes = [IsMailBoxOwner]
    serializer_class = EmailTrashSerializer

    @swagger_auto_schema(
        operation_summary="Move emails to trash",
        operation_description="Move one or more emails to trash by providing a list of email IDs.",
        request_body=EmailTrashSerializer,
        responses={
            200: openapi.Response("Emails moved to trash successfully."),
            400: "Invalid request or email IDs.",
        },
    )
    def patch(self, request, *args, **kwargs):
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
    permission_classes = [IsMailBoxOwner]
    serializer_class = EmailTrashSerializer

    @swagger_auto_schema(
        operation_summary="Restore emails from trash",
        operation_description="Restore trashed emails back to their original type by providing a list of email IDs.",
        request_body=EmailTrashSerializer,
        responses={
            200: openapi.Response("Emails restored from trash successfully."),
            400: "Invalid request or email IDs.",
        },
    )
    def patch(self, request, *args, **kwargs):
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
    permission_classes = [IsMailBoxOwner]
    serializer_class = EmailTrashSerializer

    @swagger_auto_schema(
        operation_summary="Delete emails from trash",
        operation_description="Permanently delete trashed emails by sending a list of email IDs.",
        request_body=EmailTrashSerializer,
        responses={
            204: openapi.Response("Emails deleted successfully."),
            400: "Unable to delete emails. Please try again.",
        },
    )
    def patch(self, request, *args, **kwargs):
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

    @swagger_auto_schema(
        operation_summary="Get attachment download URL",
        operation_description="Retrieve a presigned download URL for a specific email attachment using its ID.",
        responses={
            200: openapi.Response(
                description="Presigned URL returned successfully.",
                examples={
                    "application/json": {
                        "url": "https://s3.amazonaws.com/bucket-name/attachment-name?signature=xyz"
                    }
                },
            ),
            404: "Attachment not found.",
        },
    )
    def get(self, request, *args, **kwargs):
        attachment_id = kwargs["pk"]
        try:
            attachment = request.email.attachments.get(id=attachment_id)
        except:
            return Response(
                {"detail": "Attachment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        s3_client = S3Service()
        return Response(
            {"url": s3_client.generate_presigned_url(attachment.s3_url)},
            status=status.HTTP_200_OK,
        )
