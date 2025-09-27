import secrets
import logging
from django.conf import settings
from main.services.s3 import S3Service
from rest_framework import serializers
from botocore.exceptions import NoCredentialsError

s3_client = S3Service()
logger = logging.getLogger(__name__)


class FileUrlSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)
    url = serializers.URLField(read_only=True)
    public = serializers.BooleanField(default=True, write_only=True)

    def create(self, validated_data):
        file = validated_data.get("file")
        file_name = file.name.replace(" ", "_")
        public = validated_data.get("public", True)
        visibility = "public" if public else "private"
        s3_key = f"{settings.ENV}/{visibility}/{secrets.token_hex(6)}_{file_name}"

        try:
            url = s3_client.upload_file(file, s3_key, is_public=public)
            return {"url": url}
        except NoCredentialsError:
            logger.exception(
                "PreSignedUrlSerializer-Error uploading file: AWS credentials are not configured correctly."
            )
            raise serializers.ValidationError(
                "AWS credentials are not configured correctly."
            )
        except Exception as e:
            logger.exception(f"PreSignedUrlSerializer-Error uploading file: {str(e)}")
            raise serializers.ValidationError(f"Error uploading file: {str(e)}")
