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
            "Returns all password entries for the authenticated user.\n\n"
            "Supports filters:\n"
            "- `folder`: Filter by folder ID\n"
            "- `search`: Search by title, username, url, notes, or emoji"
        ),
        manual_parameters=[
            openapi.Parameter(
                "folder",
                openapi.IN_QUERY,
                description="Filter by folder ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search keyword in title, username, url, notes, or emoji",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: PasswordSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new password entry",
        operation_description=(
            "Creates a new password record associated with the authenticated user.\n\n"
            "**Fields include:** title, url, username, password, folder, notes, emoji, and optional file attachment."
        ),
        request_body=PasswordSerializer,
        responses={
            201: PasswordSerializer(),
            400: "Validation errors or bad request",
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
        operation_description="Fetch the details of a specific password entry using its ID.",
        responses={200: PasswordSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a password entry",
        operation_description=(
            "Update any fields of a saved password including file or folder.\n\n"
            "**Note:** If no new file is uploaded, the old one is preserved."
        ),
        request_body=PasswordSerializer,
        responses={200: PasswordSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a password entry",
        operation_description="Permanently delete a password entry using its ID.",
        responses={204: "Password deleted successfully"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
