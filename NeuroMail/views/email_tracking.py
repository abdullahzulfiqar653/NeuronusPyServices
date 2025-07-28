from django.http import HttpResponse
from django.utils import timezone
from NeuroMail.models.email_log import EmailLog
import base64

def email_tracker(request, email_id):
    try:
        log = EmailLog.objects.get(email_id=email_id)
        log.is_seen = True
        log.seen_at = timezone.now()
        log.save()
        print(f"[PIXEL TRACKED] Email ID: {email_id}, IP: {request.META.get('REMOTE_ADDR')}")
    except EmailLog.DoesNotExist:
        print(f"[PIXEL TRACK FAILED] Email ID not found: {email_id}")

    transparent_pixel = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    )
    return HttpResponse(transparent_pixel, content_type="image/png")
