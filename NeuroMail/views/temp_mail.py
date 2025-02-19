import requests, time, hashlib

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.response import Response
from rest_framework import generics

from NeuroMail.models.temp_mail import TempMail


class TempMailView(generics.RetrieveAPIView):

    API_KEY = "5366fbc343msh65a91e45af93d35p164a71jsn1ecc567b915b"
    API_HOST = "privatix-temp-mail-v1.p.rapidapi.com"
    HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}

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
        is_change = request.query_params.get("ischange", "false").lower() == "true"

        user = request.user
        temp_mail, created = TempMail.objects.get_or_create(user=user)

        if created or not temp_mail.email:
            temp_mail.email = self.generate_new_email()
            temp_mail.save()
        elif is_change:
            temp_mail.email = self.generate_new_email()
            temp_mail.save()

        email = temp_mail.email
        emails = self.get_emails(email)
        if email:
            return Response({"email": email, "inbox": emails})
        return Response({"error": "Failed to generate email"}, status=500)

    def generate_new_email(self):
        url = f"https://{self.API_HOST}/request/domains/"
        try:
            response = requests.get(url, headers=self.HEADERS)
            response.raise_for_status()
            domains = response.json()
            if domains:
                return f"user{int(time.time())}{domains[0]}"
            return None
        except requests.exceptions.RequestException:
            return None

    def get_email_hash(self, email):
        return hashlib.md5(email.encode("utf-8")).hexdigest()

    def get_emails(self, email):
        email_hash = self.get_email_hash(email)
        endpoint = f"https://{self.API_HOST}/request/mail/id/{email_hash}/"

        try:
            response = requests.get(endpoint, headers=self.HEADERS)
            response.raise_for_status()
            emails = response.json()
            return emails
            # if isinstance(emails, list) and emails:
            #     formatted_emails = []
            #     for mail in emails:
            #         formatted_emails.append(
            #             {
            #                 "from": mail.get("mail_from", "Unknown"),
            #                 "subject": mail.get("mail_subject", "No Subject"),
            #                 "message": mail.get("mail_text", "No Message"),
            #             }
            #         )
            #     return formatted_emails

            return []

        except requests.exceptions.RequestException:
            return {"error": "API Error"}
