from rest_framework import generics, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from NeuroDrive.models import SharedAccess, File
from NeuroDrive.models.directory import Directory
from NeuroDrive.serializers.file import FileSerializer
from NeuroDrive.serializers.directory import DirectorySerializer
from NeuroDrive.serializers.file_upload_serializer import FileFakeSerializer

from NeuroDrive.permissions import (
    IsDirectoryOwner,
    IsOwnerOrSharedDirectory,
)

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class DirectoryListCreateView(generics.ListCreateAPIView):
    serializer_class = DirectorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "files__name", "files__directory__name"]

    def get_queryset(self):
        return (
            self.request.user.directories.filter(parent=None, name="main")
            | Directory.objects.filter(shared_with=self.request.user)
        ).order_by("-created_at")

    @swagger_auto_schema(
        operation_summary="List Directories",
        operation_description="""
        **Retrieve Directories**

        This endpoint retrieves all directories that:
        - Are **owned** by the authenticated user.

        **Response:**
        - A list of directories with their details.
        """,
        responses={200: DirectorySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a New Directory",
        operation_description="""
        **Create a New Directory**

        Allows the user to create a new directory.

        **Required Fields:**
        - `name` (required) - Name of the new directory.
        - `parent` (optional) - ID of the parent directory.

        **Response:**
        - Returns the newly created directory details.
        """,
        request_body=DirectorySerializer,
        responses={201: DirectorySerializer()},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DirectoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DirectorySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return self.request.user.directories.all() | Directory.objects.filter(
                shared_with=self.request.user
            )
        return Directory.objects.none()

    def get_object(self):
        try:
            obj = super().get_object()
        except:
            obj, _ = Directory.objects.get_or_create(owner=self.request.user, name="main")
        return obj

    def perform_destroy(self, instance):
        if instance.name != "main":
            instance.delete()

    @swagger_auto_schema(
        operation_summary="Retrieve Directory Details",
        operation_description="""
        **Retrieve Directory Details**

        - Fetches details of a specific directory.
        - The user must **own the directory**.
        """,
        manual_parameters=[
            openapi.Parameter(
                name="pk",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description="ID of the directory",
            )
        ],
        responses={200: DirectorySerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Directory Details",
        operation_description="""
        **Update Directory Details**

        - Allows updating the **name** or **parent directory**.
        - The user must be the **owner** of the directory.

        **Allowed Fields:**
        - `name`  - New name of the directory.
        - `parent`  - ID of the new parent directory (optional).
        """,
        manual_parameters=[
            openapi.Parameter(
                name="pk",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description="ID of the directory",
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New directory name"
                ),
                "parent": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Parent directory ID (optional)",
                ),
            },
        ),
        responses={200: DirectorySerializer()},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Directory",
        operation_description="""
        **Delete a Directory**

        - Only the **owner** of the directory can delete it.
        """,
        manual_parameters=[
            openapi.Parameter(
                name="pk",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description="ID of the directory",
            )
        ],
        responses={204: "Directory deleted successfully"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class DirectoryFileListCreateView(generics.ListCreateAPIView):
    search_fields = ["name"]
    filterset_fields = ["is_starred"]
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsDirectoryOwner()]
        return [IsOwnerOrSharedDirectory()]

    def get_queryset(self):
        directory_id = self.kwargs.get("directory_id") or self.kwargs.get("pk")
        user = self.request.user
        if directory_id == "shared":
            return File.objects.filter(
                id__in=SharedAccess.objects.filter(user=user).values_list(
                    "item", flat=True
                )
            )
        return self.request.directory.files.all().order_by("-created_at")

    @swagger_auto_schema(
        operation_summary="List Files in a Directory",
        operation_description="""
        Retrieves all files present in a specified directory.

        **Path Parameter:**
        - `directory_id` – ID of the target directory.  
          If `'shared'` is passed instead of an ID, returns all files shared with the authenticated user.

        **Query Parameters:**
        - `search` - Search by file name.
        - `is_starred` - Filter by starred files (true/false).

        **Response:**
        - List of files in the specified directory (owned or shared).
        """,
        manual_parameters=[
            openapi.Parameter(
                name="directory_id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description="Directory ID or `'shared'` to fetch shared files.",
            ),
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Search by file name",
            ),
            openapi.Parameter(
                name="is_starred",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=False,
                description="Filter by starred status",
            ),
        ],
        responses={200: FileSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Upload a File to a Directory",
        operation_description="""
        **Upload a File to a Directory**

        Allows users to upload a file into a specified directory.

        **Path Parameter:**
        - `directory_id` (required) - ID of the directory where the file will be uploaded.

        **Form Parameters:**
        - `file` (required) - The file to be uploaded (PDF, image, etc.).

        **Response:**
        - Returns the uploaded file details.
        """,
        manual_parameters=[
            openapi.Parameter(
                name="directory_id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description="Directory ID",
            )
        ],
        request_body=FileFakeSerializer,
        responses={201: FileSerializer()},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
