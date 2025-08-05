from rest_framework import generics
from NeuroRsa.serializers.decrypt_message import DecryptMessageSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class DecryptMessageView(generics.CreateAPIView):
    serializer_class = DecryptMessageSerializer

    @swagger_auto_schema(
        operation_summary="Decrypt an encrypted PGP message",
        operation_description=(
            "Decrypt a message using one of your private keypairs.\n\n"
            "**Required fields:**\n"
            "- `message`: the encrypted PGP message block\n"
            "- `keypair_id`: ID of the keypair to use for decryption\n\n"
            "**Optional:**\n"
             "`passphrase`: Only needed if the keypair is passphrase-protected\n\n"
            "**Returns:** The original decrypted message."
        ),
        request_body=DecryptMessageSerializer,
        responses={
            201: openapi.Response(
                description="Message decrypted successfully.",
                examples={
                    "application/json": {
                        "message": "Hello, this is a decrypted message."
                    }
                },
            ),
            400: "Validation error: Invalid keypair, missing message, or decryption failed.",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
