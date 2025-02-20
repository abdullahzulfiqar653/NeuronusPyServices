from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from main.customclient import CustomTestClient


class RecipientTests(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="senderuser", password="testpassword"
        )

        self.client = CustomTestClient("rsa:8000")

        self.url_encrypt = "/api/recipients/encrypt-message/"

        self.client.force_authenticate(self.user)
        keypair_data = {
            "name": "senderuser",
            "email": "senderuser@example.com",
        }
        keypair_response = self.client.post(
            "/api/keypairs/", keypair_data, format="json"
        )

        self.assertEqual(keypair_response.status_code, status.HTTP_201_CREATED)

        public_key = keypair_response.data["public_key"]

        self.recipient_data = {"name": "Soha", "public_key": public_key, "emoji": "🔒"}

        response = self.client.post(
            "/api/recipients/", self.recipient_data, format="json"
        )

        self.recipient_id = response.data["id"]

    def test_encrypt_message_success(self):
        message = "This is a secret message."
        data = {
            "message": message,
            "recipient_ids": [self.recipient_id],  # Add the recipient's ID
        }

        response = self.client.post(self.url_encrypt, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_encrypt_message_invalid_public_key(self):
        message = "This is a secret message."
        data = {
            "message": message,
            "recipient_ids": ["non_existing_id"],  # Invalid recipient ID
        }

        response = self.client.post(self.url_encrypt, data, format="json")

        # Check for a 400 Bad Request response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Updated assertion to check for recipient_ids key instead of "error"
        self.assertIn("recipient_ids", response.data)
        self.assertEqual(
            response.data["recipient_ids"][0],
            'Invalid pk "non_existing_id" - object does not exist.',
        )

    def test_encrypt_message_missing_message(self):

        data = {"recipient_ids": [self.recipient_id]}

        response = self.client.post(self.url_encrypt, data, format="json")

        # Check that the status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Optionally, check for a specific error message in the response
        self.assertIn("message", response.data)

    def test_encrypt_message_unauthorized_user(self):
        self.client.logout()
        message = "This is a secret message."
        data = {"message": message, "recipient_ids": [self.recipient_id]}
        response = self.client.post(self.url_encrypt, data, format="json")

        # Assert Unauthorized (401)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_encrypt_message_invalid_recipient_type(self):
        data = {"message": "Test message", "recipient_ids": "invalid_string"}
        response = self.client.post(self.url_encrypt, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recipient_ids", response.data)
