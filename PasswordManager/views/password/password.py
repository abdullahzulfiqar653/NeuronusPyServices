from rest_framework import generics, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from PasswordManager.serializers.password import PasswordSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class PasswordListCreateView(generics.ListCreateAPIView):
    serializer_class = PasswordSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["title", "username", "url", "notes", "emoji"]
    filterset_fields = ["folder"]

    def get_queryset(self):
        return self.request.user.passwords.all().order_by("-created_at")

    @swagger_auto_schema(
        operation_summary="List all saved passwords",
        operation_description=(
            "Retrieve all password entries saved by the authenticated user.\n\n"
            "🔎 **Search Supported:**\n"
            "- `search` parameter allows searching in title, username, URL, notes, and emoji.\n\n"
            "🎯 **Filter Supported:**\n"
            "- `folder`: Filter passwords by folder ID."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="folder",
                in_=openapi.IN_QUERY,
                description="Filter passwords by Folder ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Search in title, username, URL, notes, or emoji",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of password entries",
                schema=PasswordSerializer(many=True),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new password entry",
        operation_description=(
            "Create a password record with title, credentials, and optional attachment.\n\n"
            "📎 **Supported fields:**\n"
            "- `title` (required, must be unique)\n"
            "- `url`, `username`, `password`, `notes`, `emoji`\n"
            "- `folder` (required: must belong to the user)\n"
            "- `file` (optional file upload — e.g. PDF, image, document)"
        ),
        request_body=PasswordSerializer,
        responses={
            201: openapi.Response(
                description="Password created successfully", schema=PasswordSerializer()
            ),
            400: openapi.Response(description="Validation errors or bad request"),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PasswordRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PasswordSerializer

    def get_queryset(self):
        return self.request.user.passwords.all()

    @swagger_auto_schema(
        operation_summary="Retrieve a password entry",
        operation_description=(
            "Fetch the full details of a single password entry using its ID.\n\n"
            "Returns all saved fields including optional file metadata."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="pk",
                in_=openapi.IN_PATH,
                description="ID of the password entry",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Password entry details", schema=PasswordSerializer()
            ),
            404: openapi.Response(description="Password not found"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a password entry",
        operation_description=(
            "Update one or more fields of a password entry.\n\n"
            "📌 You can send partial fields (`PATCH`).\n"
            "📁 File field can be updated. If not sent, previous file remains."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="pk",
                in_=openapi.IN_PATH,
                description="ID of the password to update",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        request_body=PasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password updated", schema=PasswordSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Password not found"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a password entry",
        operation_description="Permanently delete the password entry by ID.",
        manual_parameters=[
            openapi.Parameter(
                name="pk",
                in_=openapi.IN_PATH,
                description="ID of the password to delete",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            204: openapi.Response(description="Password deleted successfully"),
            404: openapi.Response(description="Password not found"),
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
