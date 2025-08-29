from rest_framework import serializers

class SharedLinkPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=4)
    confirm_password = serializers.CharField(write_only=True, min_length=4)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"detail": "Passwords do not match"})
        return data
