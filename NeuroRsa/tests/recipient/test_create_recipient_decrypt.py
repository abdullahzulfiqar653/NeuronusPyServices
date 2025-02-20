from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from main.customclient import CustomTestClient


class DecryptionTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="senderuser", password="testpassword"
        )
        self.client = CustomTestClient("rsa:8000")

        self.url_encrypt = "/api/recipients/encrypt-message/"
        self.url_decrypt = "/api/recipients/decrypt-message/"

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
        self.keypair_id = keypair_response.data["id"]

        # Create recipient
        self.recipient_data = {"name": "Soha", "public_key": public_key, "emoji": "🔒"}
        response = self.client.post(
            "/api/recipients/", self.recipient_data, format="json"
        )
        self.recipient_id = response.data["id"]

        # Encrypt a message
        self.message_text = "This is a secret message."
        encrypt_data = {
            "message": self.message_text,
            "recipient_ids": [self.recipient_id],
        }
        encrypt_response = self.client.post(
            self.url_encrypt, encrypt_data, format="json"
        )

        self.assertEqual(encrypt_response.status_code, status.HTTP_201_CREATED)
        self.encrypted_message = encrypt_response.data["message"]

    def test_decrypt_message_success(self):
        """Test successful decryption of an encrypted message."""
        data = {
            "message": self.encrypted_message,
            "keypair_id": self.keypair_id,
            "passphrase": "null",
        }

        response = self.client.post(self.url_decrypt, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], self.message_text)

    def test_decrypt_message_corrupted(self):
        corrupted_message = self.encrypted_message + "tampered_data"
        data = {
            "message": corrupted_message,
            "keypair_id": self.keypair_id,
        }
        response = self.client.post(self.url_decrypt, data, format="json")

        # Check if the error message indicates that the message is invalid
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"][0].code, "invalid"
        )  # Check if the message error code is 'invalid'

    def test_encrypt_message_multiple_recipients(self):
        # Create another recipient
        recipient_data = {
            "name": "Alice",
            "public_key": self.client.post(
                "/api/keypairs/",
                {"name": "Alice", "email": "alice@example.com"},
                format="json",
            ).data["public_key"],
            "emoji": "🔒",
        }
        response = self.client.post("/api/recipients/", recipient_data, format="json")
        recipient_id_2 = response.data["id"]

        encrypt_data = {
            "message": self.message_text,
            "recipient_ids": [self.recipient_id, recipient_id_2],
        }
        encrypt_response = self.client.post(
            self.url_encrypt, encrypt_data, format="json"
        )
        self.assertEqual(encrypt_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", encrypt_response.data)

    def test_decrypt_message_unauthorized(self):
        # Create another user and generate a keypair for them
        other_user = User.objects.create_user(
            username="otheruser", password="testpassword"
        )
        self.client.force_authenticate(other_user)
        keypair_data = {
            "name": "otheruser",
            "email": "otheruser@example.com",
        }
        keypair_response = self.client.post(
            "/api/keypairs/", keypair_data, format="json"
        )
        other_keypair_id = keypair_response.data["id"]

        data = {
            "message": self.encrypted_message,
            "keypair_id": other_keypair_id,
            "passphrase": "null",
        }
        response = self.client.post(self.url_decrypt, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
