from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from NeuroMail.models.mailbox import MailBox
from NeuroMail.serializers.mailbox import MailboxSerializer
from NeuroMail.utils.mail_server_apis import delete_mail_box
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class MailBoxExistenceCheckView(generics.CreateAPIView):
    """
    This API checks whether the selected email address is available or already taken.
    """

    serializer_class = MailboxSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["is_check"] = True
        return context

    @swagger_auto_schema(
        operation_summary="Check if mailbox is available",
        operation_description=(
            "Checks whether the email constructed from `local_part` and `domain` is available to register.\n\n"
            "**Returns:** `available: True` if the email does not exist."
        ),
        request_body=MailboxSerializer,
        responses={
            200: openapi.Response(
                description="Email is available.",
                examples={"application/json": {"available": True, "message": "MailBox is available to add."}},
            ),
            400: "Invalid or already taken email.",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"available": True, "message": "MailBox is available to add."},
            status=status.HTTP_200_OK,
        )


class MailBoxListCreateView(generics.ListCreateAPIView):
    """
    API to list all mailboxes of the current user, or create a new one.
    """

    serializer_class = MailboxSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return MailBox.objects.all()
        return self.request.user.mailboxes.all()

    @swagger_auto_schema(
        operation_summary="List all mailboxes",
        operation_description="Returns all mailboxes associated with the authenticated user.",
        responses={200: MailboxSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new mailbox",
        operation_description=(
            "Creates a new email address based on provided `local_part` and selected `domain`.\n\n"
            "**Auto-generated fields:**\n"
            "- Full email (e.g., local_part@domain.com)\n"
            "- Secure password\n\n"
            "**Note:** User must not exceed their mailbox quota."
        ),
        request_body=MailboxSerializer,
        responses={
            201: MailboxSerializer(),
            400: "Validation error, domain issue, or quota reached.",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MailBoxRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete a specific mailbox belonging to the authenticated user.
    """

    serializer_class = MailboxSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return MailBox.objects.none()
        return self.request.user.mailboxes.all()

    @swagger_auto_schema(
        operation_summary="Retrieve a mailbox",
        operation_description="Fetch the details of a specific mailbox using its ID.",
        responses={200: MailboxSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a mailbox",
        operation_description=(
            "Permanently deletes the selected mailbox and also removes it from the mail server backend."
        ),
        responses={
            204: "Mailbox deleted successfully.",
            400: "Error deleting mailbox from backend.",
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance: MailBox):
        success, msg = delete_mail_box([instance.email])
        if success:
            super().perform_destroy(instance)
        else:
            raise APIException(detail=msg, code=400)
