import os
import logging
import requests

from django.conf import settings
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self, bucket=None):
        self.s3_client = settings.S3_CLIENT
        self.bucket = bucket or getattr(settings, "DIGITALOCEAN_SPACE_NAME", "neuropyservices")

    def get_bucket_and_s3_key(self, s3_url):
        """
        Extract bucket and key from S3 URL.
        Handles both formats:
        - s3://bucket/key (full URL)
        - key (just the key, uses default bucket)
        """
        if not s3_url or not s3_url.strip():
            raise ValueError("S3 URL cannot be empty")
        
        parsed_url = urlparse(s3_url)
        bucket = parsed_url.netloc
        key = parsed_url.path.lstrip("/")
        
        # If bucket is empty (URL doesn't have s3://bucket/ format),
        # treat the entire URL as a key and use the default bucket
        if not bucket:
            # If the URL doesn't start with s3://, treat the whole thing as a key
            if not s3_url.startswith("s3://"):
                key = s3_url.lstrip("/")
            bucket = self.bucket
        
        if not key:
            raise ValueError(f"Invalid S3 URL format: {s3_url}. Key cannot be empty.")
        
        return bucket, key

    def upload_file(self, file_obj, s3_key, is_public=True):
        """
        Uploads a file directly from an HTTP request to a specific folder in DigitalOcean Spaces.
        :param file_obj: The file object from the HTTP request (e.g., request.FILES['file'])
        :param s3_key: The unique file name in the space
        :param is_public: Whether the file is public or private
        :return: The presigned URL for the uploaded file
        """
        try:
            # Upload the file directly from the request
            self.s3_client.upload_fileobj(file_obj, self.bucket, s3_key)
            logger.info(f"File uploaded successfully: {s3_key}")
            return f"s3://{self.bucket}/{s3_key}"
        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise Exception(f"Error uploading file: {e}")

    def generate_presigned_url(self, s3_url, expiration=3600):
        """
        Generates a presigned URL to access the uploaded file from the Space.
        :param bucket: The name of the Space
        :param s3_key: The object name in the space
        :param expiration: Time in seconds for which the URL is valid
        :return: Presigned URL
        """
        try:
            bucket, key = self.get_bucket_and_s3_key(s3_url)
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expiration,
            )
            logger.info(f"Generated presigned URL for {s3_url}")
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise Exception(f"Error generating presigned URL: {e}")

    def delete_file(self, s3_url):
        """
        Deletes a file from the S3 bucket.
        :param s3_key: The object name (key) in the bucket to be deleted
        :return: Success message or raises exception
        """
        try:
            # Delete the file from the bucket
            bucket, key = self.get_bucket_and_s3_key(s3_url)
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"File {key} deleted successfully.")
            return f"File {key} deleted successfully."
        except Exception as e:
            logger.error(f"Error deleting file from S3: {e}")
            raise Exception(f"Error deleting file: {e}")

    def download_file(self, url):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            filename = url.split("/")[-1].split("?")[0]
            file_path = os.path.join(os.getcwd(), filename)

            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            if os.path.exists(file_path):
                return file_path
            else:
                return None

        except requests.exceptions.RequestException as e:
            return None

    def get_file_size(self, s3_url):
        """
        Get the size of a file stored in S3/Spaces.
        :param s3_url: The S3-style URL (s3://bucket/key)
        :return: File size in bytes (int)
        """
        try:
            bucket, key = self.get_bucket_and_s3_key(s3_url)
            response = self.s3_client.head_object(Bucket=bucket, Key=key)
            size = response["ContentLength"]  # size in bytes
            logger.info(f"Size of {key} is {size} bytes.")
            return self.format_file_size(size)
        except Exception as e:
            logger.error(f"Error fetching file size from S3: {e}")
            return "Unknown"

    def format_file_size(self, size_in_bytes):
        """
        Convert file size in bytes into a human-readable string.
        :param size_in_bytes: Size in bytes (int)
        :return: str (e.g., '500 B', '2.5 KB', '10.2 MB', '1.4 GB')
        """
        try:
            if size_in_bytes < 1024:
                return f"{size_in_bytes} B"
            elif size_in_bytes < 1024**2:
                return f"{size_in_bytes / 1024:.2f} KB"
            elif size_in_bytes < 1024**3:
                return f"{size_in_bytes / (1024 ** 2):.2f} MB"
            else:
                return f"{size_in_bytes / (1024 ** 3):.2f} GB"
        except Exception as e:
            logger.error(f"Error formatting file size: {e}")
            return f"{size_in_bytes} B"
