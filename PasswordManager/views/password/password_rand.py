from rest_framework import generics, permissions
from PasswordManager.serializers import RandomPasswordCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RandomPasswordCreateView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RandomPasswordCreateSerializer

    @swagger_auto_schema(
        operation_summary="Generate a random password",
        operation_description=(
            "Generate a secure random password by specifying length and character preferences.\n\n"
            "**At least one character type must be selected.**\n"
            "**Minimum length must be 10.**\n\n"
            "**Available character types:**\n"
            "- `is_alphabets`: a mix of a-z and A-Z\n"
            "- `is_lowercase`: only a-z\n"
            "- `is_uppercase`: only A-Z\n"
            "- `is_numeric`: only 0-9\n"
            "- `is_special`: special characters like !@#...\n\n"
            "**Note:** You can combine multiple types."
        ),
        request_body=RandomPasswordCreateSerializer,
        responses={
            201: openapi.Response(
                description="Password generated successfully",
                examples={
                    "application/json": {
                        "password": "8v!Gk#zL0m"
                    }
                },
            ),
            400: "Validation error: length too short or no character type selected",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

