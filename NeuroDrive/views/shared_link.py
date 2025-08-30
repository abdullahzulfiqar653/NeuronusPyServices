from datetime import datetime
import uuid
from dateutil import parser
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from NeuroDrive.models.shared_link import SharedLink
from rest_framework.permissions import AllowAny
from main.services.s3 import S3Service
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from NeuroDrive.serializers.shared_link import SharedLinkPasswordSerializer


class SharedLinkGenerateAPIView(APIView):
    permission_classes = [AllowAny] 
    parser_classes = [MultiPartParser, FormParser]
    s3_service = S3Service()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="File to upload"
            ),
            openapi.Parameter(
                name="allowed_views",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                name="ends_at",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format="date-time",
                required=False
            ),
            openapi.Parameter(
                name="allowed_ip",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                name="password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description="Optional password to protect the file"
            ),
        ],
        consumes=["multipart/form-data"],
        responses={
            201: openapi.Response(
                description="Public link created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "public_key": openapi.Schema(type=openapi.TYPE_STRING),
                        "url": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            )
        }
    )
    def post(self, request, format=None):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"detail": "File is required"}, status=status.HTTP_400_BAD_REQUEST)

        allowed_views = request.data.get("allowed_views")
        ends_at = request.data.get("ends_at")
        allowed_ip = request.data.get("allowed_ip")
        password = request.data.get("password")  # optional

        if ends_at:
            try:
                ends_at = parser.parse(ends_at)
            except Exception:
                return Response({"detail": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        s3_key = f"public_files/{uuid.uuid4().hex}_{uploaded_file.name}"
        s3_url = self.s3_service.upload_file(uploaded_file, s3_key)

        shared_link = SharedLink.objects.create(
            file_name=uploaded_file.name,
            s3_url=s3_url,
            allowed_views=allowed_views,
            ends_at=ends_at,
            allowed_ip=allowed_ip,
            public_key=uuid.uuid4().hex,
            password=password if password else None
        )

        return Response({
            "public_key": shared_link.public_key,
            "url": f"https://neurodrive.com/links/{shared_link.public_key}"
        }, status=status.HTTP_201_CREATED)


class SharedLinkAccessAPIView(APIView):
    permission_classes = [AllowAny]
    s3_service = S3Service()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('password', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: openapi.Response(
                description="Presigned URL",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "url": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            403: "Password incorrect",
            404: "Link not found or expired",
        }
    )
    def get(self, request, key, format=None):
        try:
            obj = SharedLink.objects.get(public_key=key)
        except SharedLink.DoesNotExist:
            raise Http404("Link not found")

        ip = request.META.get('REMOTE_ADDR')
        password = request.GET.get('password')

        # Check restrictions
        if obj.is_expired():
            raise Http404("Link expired")
        if obj.allowed_views is not None and obj.used_views >= obj.allowed_views:
            raise Http404("View limit reached")
        if obj.allowed_ip and obj.allowed_ip != ip:
            raise Http404("IP restricted")

        # Password check
        if obj.password:
            if password != obj.password:
                # Render password input template if incorrect or missing
                return render(
                    request,
                    "NeuroDrive/enter_password.html",
                    {"key": obj.public_key, "error": "Incorrect password" if password else ""}
                )

        # Increment views after successful access
        obj.increment_views()

        # Generate presigned URL
        try:
            presigned_url = self.s3_service.generate_presigned_url(obj.s3_url, expiration=3600)
            return Response({"url": presigned_url}, status=status.HTTP_200_OK)
        except Exception as e:
            raise Http404(f"Error accessing file: {e}")
