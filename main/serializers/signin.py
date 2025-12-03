import requests
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

from main.utils import hash_passphrase


class UserSignInSerializer(serializers.Serializer):
    pass_phrase = serializers.CharField(write_only=True)

    def create(self, validated_data):
        pass_phrase = validated_data["pass_phrase"]
        hash = hash_passphrase(pass_phrase)

        user = User.objects.filter(username=pass_phrase).first()
        if not user:
            raise AuthenticationFailed("Invalid Seed.")

        if not user.check_password(hash):
            raise AuthenticationFailed("Invalid Seed.")

        self.refresh = RefreshToken.for_user(user)
        self.user = user

        return user

    def to_representation(self, instance):
        """Format the response"""
        profile = self.user.profile

        return {
            "access": str(self.refresh.access_token),
            "refresh": str(self.refresh),
            "cryptographic_data": {
                "public_key": profile.public_key,
                "encrypted_private_key": profile.encrypted_private_key,
                "encrypted_private_key_iv": profile.encrypted_private_key_iv,
                "encrypted_private_key_tag": profile.encrypted_private_key_tag,
                "enc_salt": profile.enc_salt,
            }
        }
