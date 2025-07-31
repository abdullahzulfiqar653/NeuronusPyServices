import base64
from django.utils import timezone
from rest_framework.views import APIView
from django.http import HttpResponse
from NeuroMail.models.email import Email
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
            if not email.is_read_by_recipient:
                email.is_read_by_recipient = True
                email.read_at = timezone.now()
                email.save()
        except Email.DoesNotExist:
            pass

        return HttpResponse(self.TRANSPARENT_PIXEL, content_type="image/png")
