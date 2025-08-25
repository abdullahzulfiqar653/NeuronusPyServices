import base64
from drf_yasg import openapi
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.views import APIView
from NeuroMail.models.email import Email
from drf_yasg.utils import swagger_auto_schema


class EmailTrackingPixelView(APIView):
    permission_classes = []

    TRANSPARENT_PIXEL = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    )

    @swagger_auto_schema(
        operation_summary="Email tracking pixel (1×1 PNG)",
        operation_description=(
            "A transparent 1×1 PNG used to track when a recipient views an email.\n\n"
            "When this pixel is loaded in an email client:\n"
            "- It checks if 12 seconds have passed since the email was last updated.\n"
            "- If so, it marks the email as `is_read_by_recipient = True` and stores `read_at` timestamp.\n\n"
            "**Does not require authentication.**"
        ),
        manual_parameters=[
            openapi.Parameter(
                "email_id",
                openapi.IN_PATH,
                description="Unique Email ID to track",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: openapi.Response(
                description="1x1 Transparent PNG",
                content={"image/png": {}},
            ),
            404: "Email not found",
        },
    )
    def get(self, request, email_id):
        try:
            email = Email.objects.get(id=email_id)
            # Only mark as read if 12 seconds have passed
            if not email.is_read_by_recipient:
                time_elapsed = timezone.now() - email.updated_at
                if time_elapsed.total_seconds() >= 12:
                    email.is_read_by_recipient = True
                    email.read_at = timezone.now()
                    email.save()
                else:
                    print(f"⏳ Email {email_id} opened too early. Not marked.")
        except Email.DoesNotExist:
            print(f"❌ Email with ID {email_id} not found.")

        return HttpResponse(self.TRANSPARENT_PIXEL, content_type="image/png")
