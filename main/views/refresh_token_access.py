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
        **JWT Refresh Endpoint**

        - Retrieves a new access token using a refresh token stored in an HTTP-only cookie (`neuro_refresh_token`).  
        - Requires no request body.  
        - Returns a fresh access token if the refresh token is valid.
        """,
        responses={
            200: RefreshTokenSerializer,
            401: "Unauthorized — No or invalid refresh token in cookie.",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("neuro_refresh_token")

        if not refresh_token:
            raise AuthenticationFailed(detail="No refresh token found in cookies")

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access": access_token})
        except Exception:
            raise AuthenticationFailed(detail="Invalid refresh token")
