from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from main.customclient import CustomTestClient


class TestKeyPairRetrieveUpdateDeleteView(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = CustomTestClient("rsa:8000")
        self.client.force_authenticate(self.user)

        self.url = "/api/keypairs/"
        self.keypair_data = {
            "name": "Test KeyPair",
            "email": "testuser@example.com",
            "passphrase": "securePassphrase123",
        }

        response = self.client.post(self.url, self.keypair_data, format="json")
        self.keypair_id = response.data["id"]

    # ----- PATCH Tests -----

    def test_patch_keypair(self):
        """Test updating only the email of a keypair"""
        patch_data = {"email": "updateduser@example.com"}

        response = self.client.patch(
            f"{self.url}{self.keypair_id}", patch_data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "updateduser@example.com")
        self.assertEqual(response.data["name"], self.keypair_data["name"])

    def test_patch_keypair_non_existent(self):
        """Test PATCH request with a non-existent keypair ID (404)"""
        invalid_keypair_id = 99999
        patch_data = {"email": "updateduser@example.com"}

        response = self.client.patch(
            f"{self.url}{invalid_keypair_id}", patch_data, format="json"
        )

        self.assertEqual(response.status_code, 404)

    def test_patch_keypair_invalid_email(self):
        """Test PATCH request with an invalid email format"""
        invalid_patch_data = {"email": "invalidemail.com"}

        response = self.client.patch(
            f"{self.url}{self.keypair_id}", invalid_patch_data, format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    # ----- RETRIEVE Tests -----

    def test_retrieve_keypair(self):
        """Test retrieving a keypair"""
        response = self.client.get(f"{self.url}{self.keypair_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.keypair_id)
        self.assertEqual(response.data["name"], self.keypair_data["name"])
        self.assertEqual(response.data["email"], self.keypair_data["email"])
        self.assertNotIn("passphrase", response.data)
        self.assertIn("public_key", response.data)
        self.assertIn("private_key", response.data)

    def test_retrieve_keypair_not_exist(self):
        """Test retrieving a non-existent keypair"""
        invalid_keypair_id = 99999
        response = self.client.get(f"{self.url}{invalid_keypair_id}")
        self.assertEqual(response.status_code, 404)

    def test_retrieve_keypair_other_user(self):
        other_user = User.objects.create_user(
            username="otheruser", password="password123"
        )
        self.client.force_authenticate(other_user)

        other_keypair_data = {
            "name": "Other User KeyPair",
            "email": "otheruser@example.com",
            "passphrase": "otherPassphrase123",
        }
        response = self.client.post(self.url, other_keypair_data, format="json")
        other_keypair_id = response.data["id"]

        response = self.client.get(f"{self.url}{other_keypair_id}/")
        self.assertEqual(response.status_code, 404)

    # ----- DELETE Tests -----

    def test_delete_keypair(self):
        """Test deleting a keypair"""
        response = self.client.delete(f"{self.url}{self.keypair_id}")
        self.assertEqual(response.status_code, 204)

        response = self.client.get(f"{self.url}{self.keypair_id}")
        self.assertEqual(response.status_code, 404)

    def test_delete_keypair_not_exist(self):
        """Test deleting a non-existent keypair"""
        invalid_keypair_id = 99999
        response = self.client.delete(f"{self.url}{invalid_keypair_id}")

        self.assertEqual(response.status_code, 404)

    # ----- UPDATE (PUT) Tests -----

    def test_update_keypair(self):
        """Test updating a keypair with new data"""
        updated_data = {
            "name": "Updated KeyPair",
            "email": "updateduser@example.com",
            "passphrase": "newSecurePassphrase123",
        }

        response = self.client.put(
            f"{self.url}{self.keypair_id}", updated_data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.keypair_id)
        self.assertEqual(response.data["name"], updated_data["name"])
        self.assertEqual(response.data["email"], updated_data["email"])
        self.assertNotIn("passphrase", response.data)
        self.assertIn("public_key", response.data)
        self.assertIn("private_key", response.data)

    def test_update_keypair_not_found(self):
        """Test updating a non-existent keypair"""
        invalid_keypair_id = 99999
        updated_data = {
            "name": "Non-Existent KeyPair",
            "email": "nonexistent@example.com",
            "passphrase": "somePassphrase",
        }

        response = self.client.put(
            f"{self.url}{invalid_keypair_id}", updated_data, format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_update_keypair_invalid_data(self):
        """Test updating keypair with missing required fields"""
        invalid_data = {
            "email": "updateduser@example.com",
            "passphrase": "newSecurePassphrase123",
        }

        response = self.client.put(
            f"{self.url}{self.keypair_id}", invalid_data, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_update_keypair_invalid_email(self):
        """Test updating keypair with an invalid email format"""
        invalid_data = {
            "name": "Updated KeyPair",
            "email": "invalidemailformat",
            "passphrase": "newSecurePassphrase123",
        }

        response = self.client.put(
            f"{self.url}{self.keypair_id}", invalid_data, format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_unauthorized_access(self):
        """Test accessing keypairs without authentication (should return 401)"""
        unauthenticated_client = CustomTestClient(
            "rsa:8000"
        )  # New client without authentication

        # Attempt to retrieve keypair
        response = unauthenticated_client.get(f"{self.url}{self.keypair_id}")
        self.assertEqual(response.status_code, 401)

        # Attempt to update keypair
        updated_data = {
            "name": "Unauthorized Update",
            "email": "unauthorized@example.com",
            "passphrase": "unauthorizedPass",
        }
        response = unauthenticated_client.put(
            f"{self.url}{self.keypair_id}", updated_data, format="json"
        )
        self.assertEqual(response.status_code, 401)

        # Attempt to delete keypair
        response = unauthenticated_client.delete(f"{self.url}{self.keypair_id}")
        self.assertEqual(response.status_code, 401)
