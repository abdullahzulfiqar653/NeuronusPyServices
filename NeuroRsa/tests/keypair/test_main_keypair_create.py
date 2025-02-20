from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from main.customclient import CustomTestClient


class TestMainKeyPairCreate(APITestCase):

    def setUp(self):
        self.client = CustomTestClient("rsa:8000")
        self.url = "/api/keypairs/main/"

    def test_create_valid_main_keypair(self):

        data = {"pass_phrase": "securePassphrase123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("public_key", response.data)
        self.assertIn("private_key", response.data)

    def test_create_main_keypair_user_exists(self):

        data = {"pass_phrase": "userPassphrase123"}
        self.client.post(self.url, data, format="json")

        # Second request: Attempt to create the main key pair again
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            str(response.data["msg"][0]), "User already have main keypair."
        )

    def test_create_main_keypair_missing_passphrase(self):

        # Missing pass_phrase
        data = {}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("pass_phrase", response.data)

    def test_create_main_keypair_authenticated(self):
        self.user = User.objects.create_user(username="user", password="password")
        self.client.force_authenticate(self.user)
        """Ensure an authenticated user can create a keypair successfully."""
        data = {"pass_phrase": "securePassphrase123"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertIn("public_key", response.data)
        self.assertIn("private_key", response.data)
