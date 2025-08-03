from rest_framework import generics, filters
from PasswordManager.serializers.folder import FolderSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class FolderListCreateView(generics.ListCreateAPIView):
    serializer_class = FolderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]

    def get_queryset(self):
        return self.request.user.folders.all().order_by("-created_at")

    @swagger_auto_schema(
        operation_summary="List all folders",
        operation_description=(
            "Returns all folders created by the authenticated user.\n\n"
            "**Supports search** on `title` field."
        ),
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search folders by title",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: FolderSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new folder",
        operation_description="Create a new folder with a given title for the current user.",
        request_body=FolderSerializer,
        responses={
            201: FolderSerializer(),
            400: "Validation error: title is required or duplicate",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FolderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FolderSerializer

    def get_queryset(self):
        return self.request.user.folders.all()

    @swagger_auto_schema(
        operation_summary="Retrieve a folder",
        operation_description="Fetch the details of a specific folder using its ID.",
        responses={200: FolderSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a folder",
        operation_description="Update the title of a specific folder.",
        request_body=FolderSerializer,
        responses={200: FolderSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a folder",
        operation_description="Permanently delete a folder by ID.",
        responses={204: "Folder deleted successfully"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
