import base64
from django.utils import timezone
from django.views import View
from django.http import HttpResponse
from NeuroMail.models.email import Email
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class EmailTrackingPixelView(View):

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
    def get(self, email_id):
        try:
            email = Email.objects.get(id=email_id)
            if not email.is_viewed_by_recepient:
                email.is_viewed_by_recepient = True
                email.viewed_at = timezone.now()
                email.save()
        except Email.DoesNotExist:
            pass

        return HttpResponse(self.TRANSPARENT_PIXEL, content_type="image/png")
