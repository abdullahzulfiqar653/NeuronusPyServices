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
        operation_description="Tracking pixel to mark email as viewed.",
        manual_parameters=[
            openapi.Parameter(
                "email_id",
                openapi.IN_PATH,
                description="Email ID",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: "1x1 Transparent PNG"},
    )
    def get(self, request, email_id):
        try:
            email = Email.objects.get(id=email_id)

            # Only mark as read if 30 seconds have passed since the email was sent
            if not email.is_read_by_recipient:
                time_elapsed = timezone.now() - email.updated_at
                if time_elapsed.total_seconds() >= 10:
                    email.is_read_by_recipient = True
                    email.read_at = timezone.now()
                    email.save()
                else:
                    print(f"⏳ Email {email_id} opened too early. Not marked.")
        except Email.DoesNotExist:
            print(f"❌ Email with ID {email_id} not found.")

        return HttpResponse(self.TRANSPARENT_PIXEL, content_type="image/png")
