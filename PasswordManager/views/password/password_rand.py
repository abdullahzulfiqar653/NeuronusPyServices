from rest_framework import generics, permissions
from PasswordManager.serializers import RandomPasswordCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RandomPasswordCreateView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RandomPasswordCreateSerializer

    @swagger_auto_schema(
        operation_summary="Generate a random password",
        operation_description="""
        Generate a secure random password by specifying length and character preferences.

        **Constraints:**
        - At least **one character type** must be selected.
        - **Minimum length** must be **10**.

        **Character type flags:**
        - `is_alphabets`: A mix of lowercase and uppercase letters (a-zA-Z)
        - `is_lowercase`: Only lowercase letters (a-z)
        - `is_uppercase`: Only uppercase letters (A-Z)
        - `is_numeric`: Numbers only (0-9)
        - `is_special`: Special symbols (!@# etc.)
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["length"],
            properties={
                "length": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Length of the generated password (min: 10)",
                    example=12,
                ),
                "is_alphabets": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Include both uppercase and lowercase alphabets",
                    example=True,
                ),
                "is_lowercase": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Include only lowercase letters",
                    example=False,
                ),
                "is_uppercase": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Include only uppercase letters",
                    example=False,
                ),
                "is_numeric": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Include numeric characters (0-9)",
                    example=True,
                ),
                "is_special": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Include special characters (!@#...)",
                    example=True,
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Password generated successfully",
                examples={
                    "application/json": {
                        "password": "8v!Gk#zL0m"
                    }
                },
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "length": ["length must be 10 or greater"],
                        "non_field_errors": ["At least one character type must be selected."]
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
