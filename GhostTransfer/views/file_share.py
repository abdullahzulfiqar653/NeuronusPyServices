import os
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from drf_yasg import openapi
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView

from rest_framework import status
from main.services.s3 import S3Service
from GhostTransfer.models.file_share import FileShare
from GhostTransfer.serializers.file_share import FileShareSerializer

client = S3Service()


class FileShareView(CreateAPIView):
    permission_classes = []
    serializer_class = FileShareSerializer

    @swagger_auto_schema(
        operation_description=(
            "Create a file share link with optional restrictions.\n\n"
            "**Important Notes:**\n"
            "- `expires_at` must be sent **without timezone info** "
            "(naive datetime, e.g. `2025-09-27T15:40:59`).\n"
            "- Do **not** include `Z` or timezone offsets like `+05:00`.\n"
            "- `timezone` is required if `expires_at` is provided and should be a valid timezone name "
            "like `Asia/Kolkata`, `Europe/London`.\n"
            "- `max_views`, `expires_at`, and `allowed_ip` are optional. If omitted, no restriction will be applied.\n"
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["files"],
            properties={
                "files": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="List of S3 file keys",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Optional password to protect the share",
                ),
                "max_views": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Maximum number of allowed views",
                ),
                "expires_at": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="date-time",
                    description=(
                        "Expiration datetime in naive format (e.g. `2025-09-27T15:40:59`). "
                        "Do not include `Z` or timezone offsets like `+05:00`. "
                        "Pass the user's local time, the `timezone` field will convert it to UTC."
                    ),
                ),
                "allowed_ip": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Restrict access to a single IP (optional)",
                ),
                "timezone": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Required if `expires_at` is provided. Must be a valid timezone name, e.g. `Asia/Kolkata`",
                ),
            },
            example={
                "files": ["s3://neuropyservices/LOCAL/public/bb4980d91cd6_1.jpg"],
                "password": "haha@123",
                "max_views": 1,
                "expires_at": "2025-09-27T16:15:00",
                "allowed_ip": None,
                "timezone": "Asia/Karachi",
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Share link created successfully",
                examples={
                    "application/json": {
                        "share_url": "https://ghosttransfer.com/share/123e4567-e89b-12d3-a456-426614174000/"
                    }
                },
            )
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FileShareAccessView(APIView):
    """
    Access a shared file with optional password, IP, view count, and expiry restrictions.
    """

    template_files = "files.html"
    template_expired = "expired.html"
    template_password = "password.html"
    permission_classes = []

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "password",
                openapi.IN_QUERY,
                description="Optional password if file share is protected",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        operation_description="Access shared files. Returns rendered HTML (not JSON). "
        "Will check expiry, max views, IP restriction, and password.",
        responses={
            200: openapi.Response(
                "HTML page with files / password / limit / expired view"
            ),
            403: "Forbidden (invalid IP or password)",
            404: "File share not found",
        },
    )
    def get(self, request, pk):
        share = get_object_or_404(FileShare, pk=pk)
        remaining_views = (
            share.max_views - share.views_used if share.max_views else "unlimited"
        )
        # Check IP restriction
        client_ip = self.get_client_ip(request)
        if share.allowed_ip and share.allowed_ip != client_ip:
            return render(
                request,
                self.template_expired,
                {"message": "Access from this IP is not allowed."},
            )

        # Check expiry
        if share.is_expired():
            return render(
                request,
                self.template_expired,
                {
                    "message": "The Link has expired. Request the owner to generate new link."
                },
            )

        # Check views
        if share.max_views and share.views_used >= share.max_views:
            return render(
                request,
                self.template_expired,
                {
                    "message": "Views Limit Exceeded. Request the owner to generate new link."
                },
            )

        # Password check
        if share.password_hash:
            password = request.GET.get("password")
            if not password or not share.check_password(password):
                return render(
                    request,
                    self.template_password,
                    {
                        "share_id": share.id,
                        "remaining_views": remaining_views,
                        "error": "Invalid or missing password" if password else None,
                    },
                )

        # ✅ Passed all checks → generate presigned URLs
        presigned_files = self.generate_presigned_links(share.files)
        # Increment views_used
        share.views_used += 1
        share.save(update_fields=["views_used"])

        return render(
            request,
            self.template_files,
            {
                "files": presigned_files,
                "remaining_views": remaining_views,
                "message": share.message,
            },
        )

    def get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def generate_presigned_links(self, files):
        result = []
        for file in files:
            presigned_url = client.generate_presigned_url(file)

            # Get filename from path
            name = os.path.basename(file)
            # If you can fetch size (depends on storage, e.g. S3 HeadObject)
            size = client.get_file_size(file)
            result.append({"url": presigned_url, "name": name, "size": size})

        return result
