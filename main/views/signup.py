from rest_framework import generics
from rest_framework.permissions import AllowAny
from main.serializers import UserSignUpSerializer


class UserSignUpView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSignUpSerializer