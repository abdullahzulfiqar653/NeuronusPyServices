from rest_framework import serializers
from django.contrib.auth.models import User
from main.utils import hash_passphrase  


class UserSignUpSerializer(serializers.Serializer):
    pass_phrase = serializers.CharField(write_only=True, required=True)
    public_key = serializers.CharField(write_only=True, required=True)
    encrypted_private_key = serializers.CharField(write_only=True, required=True)
    encrypted_private_key_iv = serializers.CharField(write_only=True, required=True)
    encrypted_private_key_tag = serializers.CharField(write_only=True, required=True)
    enc_salt = serializers.CharField(write_only=True, required=True)

    def create(self, validated_data):
        passphrase = validated_data.get('pass_phrase')
        public_key = validated_data.get('public_key')
        encrypted_private_key = validated_data.get('encrypted_private_key')
        encrypted_private_key_iv = validated_data.get('encrypted_private_key_iv')
        encrypted_private_key_tag = validated_data.get('encrypted_private_key_tag')
        enc_salt = validated_data.get('enc_salt')
        
        # Check if user already exists
        if User.objects.filter(username=passphrase).exists():
            raise serializers.ValidationError(
                {"error": "Try again with different user registration"}
            )
        
        try:
            user = User.objects.create(username=passphrase)   
            hashed_password = hash_passphrase(passphrase)
            user.set_password(hashed_password)
            user.save()

            user.profile.public_key = public_key
            user.profile.encrypted_private_key = encrypted_private_key
            user.profile.encrypted_private_key_iv = encrypted_private_key_iv
            user.profile.encrypted_private_key_tag = encrypted_private_key_tag
            user.profile.enc_salt = enc_salt
            user.profile.save()
                
        except Exception as e:
            print(f"Error creating user: {e}")
            
            if 'user' in locals():
                user.delete()
                
            raise serializers.ValidationError(
                {"error": "Failed to create user account. Please try again."}
            )

        return {
            "success": True,
            "message": "User created successfully",
        }
