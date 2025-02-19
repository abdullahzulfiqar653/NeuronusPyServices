import os
import requests, time, hashlib
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import generics
from NeuroMail.models.temp_mail import TempMail

API_HOST = os.getenv("API_HOST")
API_KEY = os.getenv("API_KEY")
HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}


class TempMailRetrieveAPIView(generics.RetrieveAPIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="ischange",
                in_=openapi.IN_QUERY,
                description="Set to `true` to generate a new email.",
                type=openapi.TYPE_BOOLEAN,
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        is_change = request.query_params.get("ischange", "false")
        user = request.user
        temp_mail, created = TempMail.objects.get_or_create(user=user)
        if created or is_change == "true":
            temp_mail.email = self.generate_new_email()
            temp_mail.save()
        email = temp_mail.email
        if not email:
            return Response({"error": "Failed to generate email"}, status=500)

        emails = self.get_emails(email)
        return Response({"email": email, "inbox": emails})

    def generate_new_email(self):
        url = f"https://{API_HOST}/request/domains/"
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            domains = response.json()
            new_email = f"user{int(time.time())}{domains[0]}"
            return new_email
        except requests.exceptions.RequestException as e:
            print(f"Debug: API Error - {e}")
            return None

    def get_email_hash(self, email):
        if not email:
            raise ValueError("Error: Email is None, cannot generate hash.")
        return hashlib.md5(email.encode("utf-8")).hexdigest()

    def get_emails(self, email):
        email_hash = self.get_email_hash(email)
        endpoint = f"https://{API_HOST}/request/mail/id/{email_hash}/"

        try:
            response = requests.get(endpoint, headers=HEADERS)
            response.raise_for_status()
            emails = response.json()
            return emails
        except requests.exceptions.RequestException as e:
            return {"error": f"API Error - {str(e)}"}
