from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from main.serializers import UserSignInSerializer


class UserSignInView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSignInSerializer

    @swagger_auto_schema(
        operation_summary="User Sign-In using Seed Phrase",
        operation_description="""
This endpoint allows users to log in using their **Resonance seed phrase**.

- If the seed is valid, a new user is created (if it doesn't exist already).
- The seed is validated from the Resonance server.
- After validation:
    - User gets **JWT access** and **refresh tokens**
    - Address linked with the user is returned

### 🚀 Usage:
- Only provide `pass_phrase` in request body.
- On success, `access`, `refresh`, and `address` are returned.
- `refresh` token is also set as **HttpOnly Secure Cookie**.
        """,
        request_body=openapi.Schema(
            title="User Login Schema",
            type=openapi.TYPE_OBJECT,
            required=["pass_phrase"],
            properties={
                "pass_phrase": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    title="Seed Phrase",
                    description="Your secure seed phrase to sign in with Resonance.",
                    example="yellow peanut taxi..."
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Sign-in successful. JWT tokens and address returned.",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
                        "refresh": "eyJ1c2VyX2lkIjoxfQ...",
                        "address": "0x2Af...C67E"
                    }
                }
            ),
            400: "Bad Request — seed not provided or invalid format.",
            401: "Unauthorized — Invalid or rejected seed.",
            500: "Internal Server Error — Resonance service unreachable."
        },
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.pop("refresh", None)
        if refresh_token:
            response.set_cookie(
                "neuro_refresh_token", refresh_token, httponly=True, secure=True
            )
        return response
