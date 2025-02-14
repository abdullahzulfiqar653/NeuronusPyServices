import os
import secrets
import mimetypes

from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.contrib.auth.hashers import make_password, check_password

from main.services.s3 import S3Service
from NeuroDrive.models.file import File
from NeuroDrive.models.shared_access import SharedAccess
from NeuroDrive.serializers.shared_access import SharedAccessSerializer

from main.utils.utils import get_file_metadata, remove_exif, remove_pdf_metadata


s3_client = S3Service()


class FileSerializer(serializers.ModelSerializer):
    url = serializers.URLField(read_only=True)
    file = serializers.FileField(required=False)
    metadata = serializers.JSONField(read_only=True)
    is_password_protected = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=255, required=False)
    shared_accesses = SharedAccessSerializer(many=True, read_only=True)
    user_address = serializers.CharField(write_only=True, required=False)
    is_remove_metadata = serializers.BooleanField(default=False, write_only=True)
    is_remove_password = serializers.BooleanField(write_only=True, required=False)
    is_giving_permission = serializers.BooleanField(
        write_only=True, required=False, default=False
    )
    password = serializers.CharField(
        write_only=True, required=False, validators=[MinLengthValidator(8)]
    )

    class Meta:
        model = File
        fields = [
            "id",
            "url",
            "name",
            "file",
            "size",
            "metadata",
            "password",
            "directory",
            "is_starred",
            "content_type",
            "user_address",
            "shared_accesses",
            "is_remove_metadata",
            "is_remove_password",
            "is_giving_permission",
            "is_password_protected",
        ]
        read_only_fields = ["size", "directory", "content_type"]

    def get_is_password_protected(self, obj):
        """Check if the file is password protected"""
        return bool(obj.password)

    def validate_user_address(self, value):
        if self.instance:
            if not User.objects.filter(profile__address=value).exists():
                raise serializers.ValidationError({"detail": "User address not found."})
        return value

    def validate(self, data):
        """
        Ensure that the combination of 'owner', 'name', and 'directory' is unique.
        """
        file = data.get("file", None)
        if not self.instance:
            if not file:
                raise serializers.ValidationError({"file": ["File is required"]})
        name = data.get("name", "")
        if not name:
            name = self.instance.name if self.instance else file.name
        request = self.context.get("request")

        query = File.objects.all()
        if self.instance:
            query = query.exclude(owner=request.user, directory=request.directory)
        if query.filter(
            owner=request.user, name=name, directory=request.directory
        ).exists():
            pass
        return data

    def get_unique_filename(self, name):
        request = self.context.get("request")
        user = request.user
        directory = request.directory
        base, ext = os.path.splitext(name)

        if user.files.filter(directory=directory, name=name).exists():
            random_str = secrets.token_hex(4)
            return f"{base}_{random_str}{ext}"

        return name

    def create(self, validated_data):
        _ = validated_data.pop("is_starred", None)
        _ = validated_data.pop("is_remove_password", None)
        _ = validated_data.pop("is_remove_metadata", None)
        _ = validated_data.pop("is_giving_permission", None)
        file = validated_data.pop("file")
        request = self.context.get("request")
        name = validated_data.get("name", file.name).replace(" ", "_")
        name = self.get_unique_filename(name)
        content_type, _ = mimetypes.guess_type(file.name)
        s3_key = f"neurodrive/{request.directory.id}/{name}"
        s3_url = s3_client.upload_file(file, s3_key)
        validated_data["name"] = name
        validated_data["s3_url"] = s3_url
        validated_data["size"] = file.size
        validated_data["owner"] = request.user
        validated_data["directory"] = request.directory
        validated_data["content_type"] = content_type or "application/octet-stream"
        validated_data["metadata"] = get_file_metadata(file)
        validated_data["metadata"]["file_name"] = name

        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        password = validated_data.pop("password", None)
        user_address = validated_data.pop("user_address", None)
        is_giving_permission = validated_data.pop("is_giving_permission", False)
        is_remove_password = validated_data.pop("is_remove_password", False)

        if is_remove_password:
            if not password:
                raise serializers.ValidationError({"password": ["Password required."]})
            if not instance.password:
                raise serializers.ValidationError(
                    {"password": ["File is not password protected."]}
                )

            if not check_password(password, instance.password):
                raise serializers.ValidationError({"password": ["Incorrect password."]})

            instance.password = None

        elif password:
            instance.password = make_password(password)

        is_remove_metadata = validated_data.pop("is_remove_metadata", False)
        if is_remove_metadata:
            url = s3_client.generate_presigned_url(instance.s3_url)
            if instance.content_type:
                try:
                    file = s3_client.download_file(url)
                    if not file:
                        raise ValueError("File could not be downloaded from S3.")

                    s3_key = f"neurodrive/{request.directory.id}/{instance.name}"

                    if instance.content_type.startswith("image"):
                        file_without_exif = remove_exif(file)
                        s3_url = s3_client.upload_file(file_without_exif, s3_key)
                        instance.s3_url = s3_url

                    elif instance.content_type == "application/pdf":
                        file_without_metadata = remove_pdf_metadata(file)
                        s3_url = s3_client.upload_file(file_without_metadata, s3_key)
                        instance.s3_url = s3_url

                    if os.path.exists(file):
                        os.remove(file)

                except Exception as e:
                    raise serializers.ValidationError(
                        {"error": f"Metadata removal failed: {e}"}
                    )

        file = validated_data.pop("file", None)
        if file:
            name = validated_data.get("name", file.name).replace(" ", "_")
            content_type, _ = mimetypes.guess_type(file.name)
            s3_key = f"neurodrive/{request.directory.id}/{name}"
            s3_url = s3_client.upload_file(file, s3_key)
            validated_data["s3_url"] = s3_url
            validated_data["size"] = file.size
            validated_data["content_type"] = content_type or "application/octet-stream"

        if is_giving_permission and user_address:
            user_to_share_with = User.objects.get(profile__address=user_address)
            SharedAccess.objects.create(user=user_to_share_with, item=instance)

        if hasattr(request, "directory") and hasattr(request, "file"):
            validated_data["directory"] = request.directory

        if validated_data.get("name"):
            name = self.get_unique_filename(validated_data["name"])
            validated_data["name"] = name
        return super().update(instance, validated_data)
