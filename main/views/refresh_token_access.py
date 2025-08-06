from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from main.serializers import RefreshTokenSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RefreshTokenAPIView(generics.RetrieveAPIView):
    """
    - If you are logged in successfully, the refresh token is stored in an HTTP-only cookie.
    - To obtain a new access token, send a **GET request** to this endpoint.
    - The access token will be returned in the response.
    """

    permission_classes = []
    serializer_class = RefreshTokenSerializer

    @swagger_auto_schema(
        operation_summary="Refresh access token",
        operation_description="""
            This endpoint allows users to refresh their **access token** using the **refresh token**.
    
            **How It Works:**
            - When a user logs in successfully, the `refresh_token` is stored in the browser’s **HTTP-only cookies**.

            - To get a new **access token**, the client should send a `GET` request to this endpoint.

            - If the request is from the **same origin** and includes the stored `refresh_token`, a new access token will be returned.
    
            **Request:**
            - Requires a valid `refresh_token` stored in HTTP-only cookies.

            **Response:**
            - If successful, returns a new `access token`.
            - If the refresh token is missing or invalid, an authentication error is raised.
    
            """,
        responses={
            200: RefreshTokenSerializer,
            401: "Unauthorized — No or invalid refresh token in cookie.",
        },
    )
    def get(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("neuro_refresh_token")

        if not refresh_token:
            raise AuthenticationFailed(detail="No refresh token found in cookies")

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access": access_token})
        except Exception:
            raise AuthenticationFailed(detail="Invalid refresh token")
