import os
from django.apps import apps
from django.conf import settings
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404, HttpResponseForbidden
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from main.models.feature import Feature

# Mapping for file types and their respective models and storage paths
FILE_MODEL_MAP = {
    "mailbox-attachments": {
        "model": apps.get_model("NeuroMail", "EmailAttachment"),
        "path": "protected/mailbox/attachments/",
    },
    "password-attachments": {
        "model": apps.get_model("PasswordManager", "Password"),
        "path": "protected/passwords/attachments/",
    },
    "drive-attachments": {
        "model": apps.get_model("NeuroDrive", "File"),
        "path": "protected/drive/attachments/",
    },
}


class ProtectedMediaView(APIView):
    """
    View to serve protected media files with token-based authentication.
    Checks if the user owns the media file and serves it.
    """

    @swagger_auto_schema(
        operation_summary="Download protected media file",
        operation_description="""
        Serve secured media files stored under protected paths (like attachments or drive files).  
        Access is restricted to file owners or shared recipients.

        **Path Parameters:**
        - `file_type`:
        - `mailbox-attachments`
        - `password-attachments`
        - `drive-attachments`
        - `file_name`: Name of the file to download (must exactly match the saved filename).

        **Responses:**
        - `200`: File download response (as attachment).
        - `403`: Forbidden – Access denied due to subscription or ownership.
        - `404`: File not found or invalid file type.
        """,
        manual_parameters=[
            openapi.Parameter(
                name="file_type",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Type of file (e.g., mailbox-attachments, password-attachments, drive-attachments)",
                required=True,
            ),
            openapi.Parameter(
                name="file_name",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Exact file name to be downloaded",
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="File served successfully."),
            403: "Forbidden. Upgrade required or no access to file.",
            404: "Not found. File type invalid or file does not exist.",
        },
    )
    def get(self, request, file_type, file_name):
        SharedAccess = apps.get_model("NeuroDrive", "SharedAccess")
        file_type_data = FILE_MODEL_MAP.get(file_type)

        if not file_type_data:
            raise Http404("Invalid file type.")

        Model = file_type_data["model"]
        file_path = f"{file_type_data['path']}{file_name}"
        user = request.user

        obj = self.get_media_object(Model, file_path)
        shared_obj = self.get_shared_object(SharedAccess, file_path)
        # Check permissions for accessing the file
        if not self.check_user_permissions(obj, shared_obj, user):
            raise Http404("File not found in your accessible storage.")

        if file_type == "drive-attachments":
            if not self.check_file_size(user, shared_obj, obj):
                return HttpResponseForbidden(
                    "File Owner needs to upgrade subscription to access this file."
                    if shared_obj
                    else "You need to upgrade your subscription to access this file."
                )

        # Construct the full file path in the protected directory
        full_file_path = os.path.join(
            settings.MEDIA_ROOT, file_type_data["path"], file_name
        )

        if not os.path.exists(full_file_path):
            raise Http404("File not found in your accessible storage.")

        # Return the file as response
        file_handle = default_storage.open(full_file_path, "rb")
        response = FileResponse(file_handle, content_type=obj.content_type)
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response

    def get_media_object(self, Model, file_path):
        """Helper function to safely get the media object."""
        try:
            return Model.objects.get(file=file_path)
        except Model.DoesNotExist:
            raise Http404("Media not found.")

    def get_shared_object(self, SharedAccess, file_path):
        """Helper function to safely get the shared access object."""
        try:
            return SharedAccess.objects.get(item__file=file_path)
        except SharedAccess.DoesNotExist:
            return None

    def check_user_permissions(self, obj, shared_obj, user):
        """Helper function to check permissions for file access."""
        error_msg_403 = "You do not have permission to access this media."

        if hasattr(obj, "mail"):
            if user != obj.mail.mailbox.user:
                return HttpResponseForbidden(error_msg_403)

        if hasattr(obj, "user"):
            if user != obj.user:
                return HttpResponseForbidden(error_msg_403)

        if hasattr(obj, "owner"):
            if user != obj.user or (shared_obj and user != shared_obj.user):
                return HttpResponseForbidden(error_msg_403)

        return True

    def check_file_size(self, user, shared_obj, obj):
        """Check if the file size can be accessed by the user based on their subscription."""
        requested_id = (
            getattr(obj, "id", None)
            or getattr(shared_obj, "item", None)
            and getattr(shared_obj.item, "id", None)
        )
        if shared_obj:
            user = shared_obj.item.owner
        space_allowed_in_gb = Feature.get_feature_value(Feature.Code.STORAGE_GB, user)
        files = user.files.order_by("created_at")

        # Check available space and file size
        for file in files:
            if file.size_in_gb() <= space_allowed_in_gb:
                if file.id == requested_id:  # Check by file id
                    return True
                space_allowed_in_gb -= file.size_in_gb()
