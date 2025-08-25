from rest_framework import generics, filters
from PasswordManager.serializers.folder import FolderSerializer
from PasswordManager.models.folder import Folder
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class FolderListCreateView(generics.ListCreateAPIView):
    serializer_class = FolderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Folder.objects.none()  # Return empty queryset for schema generation
        return self.request.user.folders.all().order_by("-created_at")

    @swagger_auto_schema(
        operation_summary="List folders",
        operation_description=(
            "Get a list of all folders created by the authenticated user.\n\n"
            "🔍 You can filter folders using the `search` query param.\n"
            "`search=work` will match folders like 'Work Documents', etc."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Search folders by title (case-insensitive)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="A list of folders", schema=FolderSerializer(many=True)
            )
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create folder",
        operation_description=(
            "Create a new folder for the logged-in user.\n\n"
            "📝 Required field:\n"
            "- `title`: Folder name (must be unique per user)"
        ),
        request_body=FolderSerializer,
        responses={
            201: openapi.Response(
                description="Folder created successfully", schema=FolderSerializer()
            ),
            400: openapi.Response(
                description="Validation error (e.g. missing or duplicate title)"
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FolderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FolderSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Folder.objects.none()
        return self.request.user.folders.all()

    @swagger_auto_schema(
        operation_summary="Get folder by ID",
        operation_description="Retrieve details of a folder using its unique ID.",
        responses={
            200: openapi.Response(
                description="Folder details", schema=FolderSerializer()
            ),
            404: openapi.Response(description="Folder not found"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update folder",
        operation_description=(
            "Update the title of a folder.\n\n"
            "You can send partial data using PATCH.\n\n"
            "Only the `title` field is accepted."
        ),
        request_body=FolderSerializer,
        responses={
            200: openapi.Response(
                description="Folder updated", schema=FolderSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Folder not found"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete folder",
        operation_description="Permanently delete a folder using its ID.",
        responses={
            204: openapi.Response(description="Folder deleted successfully"),
            404: openapi.Response(description="Folder not found"),
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
