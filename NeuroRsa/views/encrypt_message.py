from rest_framework import generics
from NeuroRsa.serializers.encrypt_message import EncryptMessageSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class EncryptMessageView(generics.CreateAPIView):
    serializer_class = EncryptMessageSerializer

    @swagger_auto_schema(
        operation_summary="Encrypt a message using recipients' PGP public keys",
        operation_description=(
            "Encrypt a short message using the public keys of one or more RSA recipients.\n\n"
            "**Validation rules:**\n"
            "- `message` must not be empty\n\n"
            "- `message` must not exceed **446 characters**\n\n"
            "- `recipient_ids` must contain **at least one recipient**\n\n"
            "**Returns:** A PGP-formatted encrypted message block."
        ),
        request_body=EncryptMessageSerializer,
        responses={
            201: openapi.Response(
                description="PGP message block returned successfully.",
                examples={
                    "application/json": {
                        "message": (
                            "-----BEGIN PGP MESSAGE BLOCK-----\n"
                            "3a9fd...ab12f-ff8e9...332bc\n"
                            "-----END PGP MESSAGE BLOCK-----"
                        )
                    }
                },
            ),
            400: openapi.Response(
                description="Validation error: Empty message, too long, or no recipients.",
                examples={
                    "application/json": {
                        "message": ["Message content cannot be empty."],
                        "recipient_ids": ["At least one Recipient required."],
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
