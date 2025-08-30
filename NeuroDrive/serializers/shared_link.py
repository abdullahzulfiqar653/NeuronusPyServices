from rest_framework import serializers

class SharedLinkPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=False, allow_blank=True)
    confirm_password = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password or confirm_password:  # Only check if user provided something
            if password != confirm_password:
                raise serializers.ValidationError("Passwords do not match")
        return data
