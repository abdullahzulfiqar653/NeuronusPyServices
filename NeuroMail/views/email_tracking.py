from rest_framework import generics
from django.http import HttpResponse
from django.utils import timezone
from NeuroMail.models.email import Email
import base64


class EmailTrackingPixelView(generics.RetrieveAPIView):
    """
    Endpoint to track if recipient has viewed the email.
    Returns a 1x1 transparent PNG pixel.
    """

    queryset = Email.objects.all()
    lookup_field = "id"
    permission_classes = [] 

    def retrieve(self, request, *args, **kwargs):
        email = self.get_object()

        if not email.is_viewed_by_recepient:
            email.is_viewed_by_recepient = True
            email.viewed_at = timezone.now()  
            email.save(update_fields=["is_viewed_by_recepient", "viewed_at"])

        print(f"[PIXEL TRACKED] Email ID: {email.id}, IP: {request.META.get('REMOTE_ADDR')}")

        # Base64 for a 1x1 transparent PNG
        transparent_pixel = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
        )
        return HttpResponse(transparent_pixel, content_type="image/png")

