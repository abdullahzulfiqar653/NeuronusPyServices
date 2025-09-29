import pytz
from django.utils import timezone
from rest_framework import serializers
from GhostTransfer.models.file_share import FileShare

from datetime import datetime


class NaiveDateTimeField(serializers.DateTimeField):
    """Custom field that enforces naive datetime input."""

    def to_internal_value(self, value):
        if isinstance(value, str):
            # Parse manually without timezone
            try:
                dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid datetime format. Use YYYY-MM-DDTHH:MM:SS without Z or offset."
                )
        else:
            raise serializers.ValidationError("Expected string in ISO format.")

        return dt


class FileShareSerializer(serializers.ModelSerializer):
    timezone = serializers.CharField(write_only=True)
    expires_at = NaiveDateTimeField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = FileShare
        fields = [
            "id",
            "files",
            "message",
            "password",
            "timezone",
            "max_views",
            "expires_at",
            "allowed_ip",
        ]
        read_only_fields = ["id"]

    def validate_files(self, value):
        """
        Ensure files is a list like ['url1', 'url2', ...].
        """
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Files must be in format: ['url1', 'url2', ...]."
            )
        message = self.initial_data.get("message")

        if not value and not message:
            raise serializers.ValidationError("Either provide files or a message.")

        return value

    def validate_expires_at(self, value):
        if value:
            # make naive → aware (UTC)
            tz_name = self.initial_data.get("timezone")
            if not tz_name:
                raise serializers.ValidationError(
                    "Timezone is required when passing expires_at"
                )
            if tz_name not in pytz.all_timezones:
                raise serializers.ValidationError(
                    "Invalid timezone. Must be correct timezone, e.g. 'Asia/Kolkata'."
                )
            local_tz = pytz.timezone(tz_name)
            value = timezone.make_aware(value, local_tz)
            print("Aware datetime:", value)
            if value <= timezone.now():
                raise serializers.ValidationError(
                    "Expiration time must be in the future."
                )
        return value

    def validate_max_views(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Max views must be greater than zero.")
        return value

    def create(self, validated_data):
        validated_data.pop("timezone", None)
        password = validated_data.pop("password", None)
        instance = FileShare.objects.create(**validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance
