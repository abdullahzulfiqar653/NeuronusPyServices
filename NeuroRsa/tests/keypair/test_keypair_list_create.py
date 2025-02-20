from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from NeuroRsa.models.keypair import KeyPair
from main.customclient import CustomTestClient


class TestKeyPairListCreateView(APITestCase):

    def setUp(self):
        """Set up test user and API client."""
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = CustomTestClient("rsa:8000")
        self.url = "/api/keypairs/"
        self.client.force_authenticate(self.user)

    # Test for Retrieving the ist of  keyPair
    def test_get_keypair_list(self):
        keypairs_data = [
            {
                "name": "KeyPair 1",
                "email": "user1@example.com",
                "passphrase": "securePassphrase123",
            },
            {
                "name": "KeyPair 2",
                "email": "user2@example.com",
                "passphrase": "anotherPassphrase456",
            },
        ]

        for keypair in keypairs_data:
            self.client.post(self.url, keypair, format="json")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        keypairs = response.data.get("results", response.data)
        self.assertEqual(len(keypairs), len(keypairs_data))

        response_names = {keypair["name"] for keypair in keypairs}
        expected_names = {data["name"] for data in keypairs_data}
        self.assertSetEqual(response_names, expected_names)

    # Test for Creating the keypair
    def test_create_keypair(self):
        data = {
            "name": "test_keypair",
            "email": "testuser@example.com",
            "passphrase": "secretpassphrase",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KeyPair.objects.count(), 1)
        self.assertEqual(KeyPair.objects.get().name, "test_keypair")

    def test_create_keypair_without_passphrase(self):
        data = {"name": "test_keypair", "email": "testuser@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KeyPair.objects.count(), 1)

    # Checking Vallidation for Duplicate name
    def test_create_keypair_duplicate_name(self):
        data = {
            "name": "duplicate_keypair",
            "email": "testuser@example.com",
            "passphrase": "secretpassphrase",
        }
        self.client.post(self.url, data, format="json")

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    # Checking Vallidation for Invalid Emails
    def test_create_keypair_invalid_email(self):
        data = {
            "name": "invalid_email_keypair",
            "email": "invalid-email",
            "passphrase": "secretpassphrase",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    # Checking for Unauthenticated requests
    def test_unauthenticated_requests(self):
        """Test that unauthenticated users cannot create or retrieve key pairs."""
        self.client.logout()

        # Test GET request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

        # Test POST request
        data = {
            "name": "test_keypair",
            "email": "testuser@example.com",
            "passphrase": "secretpassphrase",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
