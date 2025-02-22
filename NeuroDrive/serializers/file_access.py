from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.hashers import check_password

from NeuroDrive.models.file import File
from NeuroDrive.models.shared_access import SharedAccess

from main.services.s3 import S3Service


class FileAccessSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    url = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    content_type = serializers.CharField(read_only=True)

    def create(self, validated_data):
        request = self.context.get("request")
        file_id = self.context.get("view").kwargs.get("pk")

        obj = get_object_or_404(File, id=file_id)

        if obj.owner != request.user:
            shared_access = SharedAccess.objects.filter(
                user=request.user,
                item=obj,
                permission_type__in=[
                    SharedAccess.Permission.READ,
                    SharedAccess.Permission.FULL,
                ],
            )
            if not shared_access.exists():
                raise PermissionDenied(
                    "You do not have permission to access this file."
                )

        if obj.password:
            password = validated_data.get("password")
            if not check_password(password, obj.password):
                raise serializers.ValidationError({"password": ["Incorrect password."]})

        s3_client = S3Service()
        obj.url = s3_client.generate_presigned_url(obj.s3_url)
        validated_data["url"] = obj.url
        validated_data["name"] = obj.name
        validated_data["content_type"] = obj.content_type

        return validated_data
