import requests
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

from main.utils import hash_passphrase


class UserSignInSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    pass_phrase = serializers.CharField(write_only=True)

    def create(self, validated_data):
        pass_phrase = validated_data["pass_phrase"]
        hash = hash_passphrase(pass_phrase)

        user = User.objects.filter(username=pass_phrase).first()
        if not user:
            url = "https://apiresonance.neuronus.net/api/user/login"
            payload = {"seed": pass_phrase}
            try:
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    user = User.objects.create(username=pass_phrase)
                    user.set_password(hash)
                    user.save()
                else:
                    AuthenticationFailed("Invalid Seed.")
            except:
                AuthenticationFailed("Resonance Server down please contact admin Seed.")

        if user and user.check_password(hash):
            refresh = RefreshToken.for_user(user)
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        raise AuthenticationFailed("Invalid Seed.")
