from rest_framework import generics
from NeuroRsa.serializers.encrypt_message import EncryptMessageSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class EncryptMessageView(generics.CreateAPIView):
    serializer_class = EncryptMessageSerializer

    @swagger_auto_schema(
        operation_summary="Encrypt message with PGP for recipients",
        operation_description=(
            "Encrypt a short message using the PGP public key of one or more recipients.\n\n"
            "**Validation rules:**\n"
            "- Message must not be empty\n"
            "- Message must not exceed 446 characters\n"
            "- At least one recipient ID must be provided\n\n"
            "**Returns:** PGP encrypted message."
        ),
        request_body=EncryptMessageSerializer,
        responses={
            201: openapi.Response(
                description="Message encrypted successfully.",
            ),
            400: "Validation error: empty message, too long, or no recipient selected.",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
