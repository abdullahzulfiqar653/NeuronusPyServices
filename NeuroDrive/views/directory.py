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
        operation_description="""
        **Create a New Directory**

        Allows the user to create a new directory.

        **Required Fields:**
        - `name` (required) - Name of the new directory.\n
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
            # If the directory is not found, you could raise an error or create a default directory.
            obj, _ = Directory.objects.get_or_create(
                owner=self.request.user, name="main"
            )
        return obj

    def perform_destroy(self, instance):
        if not instance.name == "main":
            instance.delete()

    @swagger_auto_schema(
        operation_description="""
        **Retrieve Directory Details**

        - Fetches details of a specific directory.
        - The user must  **own the directory** .
        """,
        responses={200: DirectorySerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="""
        **Update Directory Details**

        - Allows updating the **name** or **parent directory**.
        - The user must be the **owner** of the directory.

        **Allowed Fields:**
        - `name`  - New name of the directory.\n
        - `parent`  - ID of the new parent directory (optional).
        """,
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
        operation_description="""
        **Delete a Directory**

        - Only the **owner** of the directory can delete it.
        """,
        responses={204: "Directory deleted successfully"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class DirectoryFileListCreateView(generics.ListCreateAPIView):
    """
    API for listing files in a directory and uploading new files.
    """

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
        operation_description="""
        **List Files in a Directory**

        Retrieves all files present in a specified directory.

        **Required Parameters:**
        - `directory_id` (path parameter) - ID of the directory.\n
        - if `shared` is passed as directory ID it will return all shared files.

        **Response:**
        - Returns a list of files with their details.
        """,
        responses={200: FileSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="""
        **Upload a File to a Directory**

        Allows users to upload a file into a specified directory.

        **Required Parameters:**
        - `file` (required) - The file to be uploaded (pdf,img etc).\n
        - `directory_id` (path parameter) - ID of the directory where the file will be uploaded.

        **Response:**
        - Returns the uploaded file details.
        """,
        request_body=FileFakeSerializer,
        responses={201: FileSerializer()},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
