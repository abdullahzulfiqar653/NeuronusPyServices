from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from main.serializers import UserSignUpSerializer


class UserSignUpView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSignUpSerializer

    @swagger_auto_schema(
        operation_summary="Create a new user with a unique passphrase",
        operation_description="""
        **User Sign-Up Endpoint**  

        - Accepts an **empty request body**.  
        - Automatically creates a new user and generates a unique **seed**.  
        - Returns the generated seed.  
        """,
        request_body=None,
        responses={
            201: "User created successfully. Returns generated seed.",
            400: "Bad request. Something went wrong.",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
