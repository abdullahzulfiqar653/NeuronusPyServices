from django.db.models import Q
from django.contrib.auth.models import AnonymousUser

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from main.services.s3 import S3Service

from NeuroDrive.models.file import File
from NeuroDrive.serializers.file import FileSerializer
from NeuroDrive.models.shared_access import SharedAccess
from NeuroDrive.permissions import IsFileOwner, IsDirectoryOwner
from NeuroDrive.serializers.file_access import FileAccessSerializer

from drf_yasg.utils import swagger_auto_schema


class FileRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = FileSerializer
    permission_classes = [IsFileOwner]

    def perform_destroy(self, instance):
        instance.owner.profile.remove_size(instance.size)
        return super().perform_destroy(instance)

    def get_object(self):
        """
        Retrieve the file object, and check if the user is either the owner or has access through SharedAccess.
        """

        obj = super().get_object()

        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return obj

        if obj.password:
            raise PermissionDenied(
                "File is Password Protected. You cannot access this file."
            )

        s3_client = S3Service()
        obj.url = s3_client.generate_presigned_url(obj.s3_url)
        return obj

    def get_queryset(self):
        """
        Return all files that the user owns or has access to through SharedAccess.
        """
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return File.objects.none()
        # Using Q objects to combine both conditions in a single queryset
        files = File.objects.filter(
            Q(owner=user)  # User owns the file
            | Q(
                shared_accesses__user=user,
                shared_accesses__permission_type__in=[
                    SharedAccess.Permission.READ,
                    SharedAccess.Permission.WRITE,
                    SharedAccess.Permission.FULL,
                ],
            )  # User has shared access to the file
        ).distinct()  # Ensure distinct results
        return files

    @swagger_auto_schema(
        operation_description="""
    **Retrieve File Details**
    Users can retrieve the file if:

    - They are the **owner** of the file.
    - They have **shared access** to the file.

    **Important Notes:**

    - If the file is **password protected**, access will be denied.
    """,
        responses={200: FileSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="""
        **Update File Details**
        Requires *ownership* of the file.

        **Supported Operations:**

        - **Update Name:**
        Send only the `name` field.

        - **Update Starred Status:**
        Send only `is_starred` (True/False).

        - **Grant Permission:**
        Set `is_giving_permission=True` and provide `user_address` to share access woth other user.

        - **Remove Metadata:**
        Set `is_remove_metadata=True`, other fields should be `null`.

        - **Set Password:**
        Send only the `password` field .

        - **Remove Password:**
        Set `is_remove_password=True` and send the current `password` field.
        """,
        request_body=FileSerializer,
        responses={200: FileSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="""
        **Delete File**
        - Only the **owner** of the file can delete it.
        - The file size will be **deducted** from the user's storage.
        """,
        responses={204: "File deleted successfully"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class FileDirectoryUpdateView(generics.UpdateAPIView):
    serializer_class = FileSerializer
    permission_classes = [IsFileOwner, IsDirectoryOwner]

    def get_queryset(self):
        return self.request.directory.files.all().order_by("created_at")

    def get_object(self):
        return self.request.file

    @swagger_auto_schema(
        operation_description="""
        **Update File Details**
        Requires *ownership* of the file.

        **Supported Operations:**

        - **Update Name:**
          Send only the `name` field.

        - **Update Starred Status:**
          Send only `is_starred` (True/False).

        - **Grant Permission:**
          Set `is_giving_permission=True` and provide `user_address` to share access with another user.

        - **Remove Metadata:**
          Set `is_remove_metadata=True`, other fields should be `null`.

        - **Set Password:**
          Send only the `password` field.

        - **Remove Password:**
          Set `is_remove_password=True` and send the current `password` field.
        """,
        request_body=FileSerializer,
        responses={200: FileSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class FileAccessView(generics.CreateAPIView):
    queryset = File.objects.none()
    serializer_class = FileAccessSerializer
    permission_classes = [IsFileOwner]

    @swagger_auto_schema(
        operation_description="""
        **Access a Password-Protected File**

        - If a file is password-protected, you must provide the correct password to access it.
        - This endpoint verifies the password and grants access if correct.

        **Request Body:**
        - **password** (required): The correct password for the file.

        **Response:**
        - If the password is correct, access is granted.
        - If the password is incorrect, an error message is returned.
        """,
        request_body=FileAccessSerializer,
        responses={200: "Access granted", 403: "Incorrect password"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
