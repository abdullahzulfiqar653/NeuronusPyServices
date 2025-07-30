from rest_framework import generics
from django.http import HttpResponse
from django.utils import timezone
from NeuroMail.models.email import Email
import base64


class EmailTrackingPixelView(generics.RetrieveAPIView):
    """
    Retrieve view to track if recipient viewed the email.
    Returns a transparent 1x1 PNG pixel.
    """

    queryset = Email.objects.all()
    lookup_url_kwarg = "email_id"  # matches <int:email_id> from URL
    lookup_field = "id"            # Email.id field
    permission_classes = []       # Public access

    def retrieve(self, request, *args, **kwargs):
        email = self.get_object()

        if not email.is_viewed_by_recepient:
            email.is_viewed_by_recepient = True
            email.seen_at = timezone.now()
            email.save()

        print(f"[PIXEL TRACKED] Email ID: {email.id}, IP: {request.META.get('REMOTE_ADDR')}")

        transparent_pixel = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
        )
        return HttpResponse(transparent_pixel, content_type="image/png")
