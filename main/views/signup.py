from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from main.serializers import UserSignUpSerializer


class UserSignUpView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSignUpSerializer

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Create a new user with cryptographic keys",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['pass_phrase', 'public_key', 'encrypted_private_key', 
                     'encrypted_private_key_iv', 'encrypted_private_key_tag', 'enc_salt'],
            properties={
                'pass_phrase': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User passphrase (min 8 characters)',
                    example='yellow-sky-bird-frost'
                ),
                'public_key': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Public key in PEM format',
                    example='-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----'
                ),
                'encrypted_private_key': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Encrypted private key',
                    example='U2FsdGVkX19/abc123def456ghi789...'
                ),
                'encrypted_private_key_iv': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Initialization Vector for AES encryption',
                    example='a1b2c3d4e5f67890'
                ),
                'encrypted_private_key_tag': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Authentication tag for AES-GCM',
                    example='tag1234567890abcd'
                ),
                'enc_salt': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Salt for key derivation',
                    example='salt1234567890abcdef'
                ),
            }
        ),
        responses={
            201: openapi.Response(
                description="User created successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "User created successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "Try again with different user registration"
                    }
                }
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)