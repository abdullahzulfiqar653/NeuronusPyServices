from django.http import HttpResponse
from django.utils import timezone
from NeuroMail.models.email import Email
import base64

def email_tracker(request, email_id):
    try:
        email = Email.objects.get(id=email_id) 
        if not email.is_viewed_by_recepient:
            email.is_viewed_by_recepient = True
            email.seen_at = timezone.now()
            email.save()
        print(f"[PIXEL TRACKED] Email ID: {email_id}, IP: {request.META.get('REMOTE_ADDR')}")
    except Email.DoesNotExist:
        print(f"[PIXEL TRACK FAILED] Email ID not found: {email_id}")

    transparent_pixel = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    )
    return HttpResponse(transparent_pixel, content_type="image/png")
