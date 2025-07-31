import base64
import logging
from django.utils import timezone
from rest_framework.views import APIView
from django.http import HttpResponse
from NeuroMail.models.email import Email
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        ip_address = request.META.get("REMOTE_ADDR")

        # Common prefetching agents to ignore
        suspicious_agents = [
            "googleimageproxy",
            "outlook",  # Often prefetches from Microsoft cloud
            "thunderbird",
            "mozilla/5.0 (windows nt",  # Some auto-fetching occurs
            "curl",  # Security scanners sometimes use this
            "python-requests",
            "applewebkit",  # Sometimes prefetches, e.g. Apple Mail
        ]
        logger.info(f"user-agent: {user_agent}, ip-address: {ip_address}")
        logger.info(
            f"Is condition true to not mark as read: {any(agent in user_agent for agent in suspicious_agents)}"
        )
        if any(agent in user_agent for agent in suspicious_agents):
            # Log it, but don't mark as read
            logger.info(
                f"📬 Pixel prefetch ignored from UA: {user_agent}, IP: {ip_address}"
            )
            return HttpResponse(self.TRANSPARENT_PIXEL, content_type="image/png")
        try:
            email = Email.objects.get(id=email_id)
            if not email.is_read_by_recipient:
                email.is_read_by_recipient = True
                email.read_at = timezone.now()
                email.save()
        except Email.DoesNotExist:
            pass

        return HttpResponse(self.TRANSPARENT_PIXEL, content_type="image/png")
