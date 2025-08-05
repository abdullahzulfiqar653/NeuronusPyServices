from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from main.serializers import UserSignUpSerializer


class UserSignUpView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSignUpSerializer

    @swagger_auto_schema(
        operation_summary="Create a new user with a unique passphrase (seed)",
        operation_description="""
        This endpoint is used to create a new user by generating a secure and unique passphrase (seed).

         **How it works**:
        - Sends a `POST` request with no body.
        - Generates a unique `pass_phrase` (seed) using internal logic.
        - Sends the seed to Resonance API for registration and login.
        - Stores the returned identity address in the user's profile.
        - Returns the generated `pass_phrase`.

         If an error occurs during the external API call, it will return a 400 error.
        """,
        request_body=None,
        responses={
            201: openapi.Response(
                description="User created successfully.",
                examples={
                    "application/json": {
                        "pass_phrase": "yellow-sky-bird-frost"  # Example seed
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request. Could not create user.",
                examples={
                    "application/json": {
                        "error": "Failed to create passphrase please refresh page"
                    }
                }
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
