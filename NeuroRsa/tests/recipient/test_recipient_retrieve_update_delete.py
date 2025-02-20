from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from main.customclient import CustomTestClient


class TestRecipientRetrieveUpdateDelete(APITestCase):

    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = CustomTestClient("rsa:8000")

        self.url = "/api/recipients/"

        # Recipient data
        self.recipient_data = {
            "name": "Soha",
            "public_key": "MIIBIjANBgkqhkiG9w0BAQEFA...",
            "emoji": "🔒",
        }

        self.updated_data = {
            "name": "Bobby",
            "public_key": "MIIBIjANBgkqhkiG9w0BAQEFA...",
            "emoji": "🔐",
        }

        self.client.force_authenticate(self.user)

        # Create a recipient
        response = self.client.post(self.url, self.recipient_data, format="json")
        self.recipient_id = response.data["id"]

    def test_get_recipient_by_id_success(self):
        """
        ________________________ Getting Recipient By ID Success ________________________
        """
        self.client.force_authenticate(self.user)
        get_url = f"{self.url}{self.recipient_id}/"
        response = self.client.get(get_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Soha")
        self.assertEqual(response.data["public_key"], "MIIBIjANBgkqhkiG9w0BAQEFA...")
        self.assertEqual(response.data["emoji"], "🔒")

    def test_get_recipient_by_id_not_found(self):
        """
        ________________________ Getting Recipient By ID Not Found ________________________
        """
        get_url = f"{self.url}99999/"
        response = self.client.get(get_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "No Recipient matches the given query."
        )

    def test_get_recipient_by_id_unauthorized(self):
        """
        ________________________ Unauthorized Access For GET Request ________________________
        """
        self.client.logout()  # Log out the user to simulate unauthorized access
        get_url = f"{self.url}{self.recipient_id}/"
        response = self.client.get(get_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_patch_recipient_success(self):
        """
        ________________________ Patching Recipient Successfully ________________________
        """
        patch_url = f"{self.url}{self.recipient_id}/"
        partial_data = {"emoji": "🔑"}

        response = self.client.patch(patch_url, partial_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["emoji"], "🔑")
        self.assertEqual(response.data["name"], "Soha")

    def test_patch_recipient_invalid_data(self):
        """
        ________________________ Invalid Data For PATCH Request ________________________
        """
        patch_url = f"{self.url}{self.recipient_id}/"
        invalid_data = {"emoji": "🔑", "name": ""}

        response = self.client.patch(patch_url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "This field may not be blank.")

    def test_patch_recipient_not_found(self):
        """
        ________________________ PATCH Request with Nonexistent ID ________________________
        """
        patch_url = f"{self.url}nonexistent-id/"
        partial_data = {"emoji": "🔑"}

        response = self.client.patch(patch_url, partial_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(
            str(response.data["detail"]), "No Recipient matches the given query."
        )

    def test_patch_recipient_unauthorized(self):
        """
        ________________________ Unauthorized Access For PATCH Request ________________________
        """
        self.client.logout()  # Log out the user to simulate unauthorized access
        patch_url = f"{self.url}{self.recipient_id}/"
        partial_data = {"emoji": "🔑"}

        response = self.client.patch(patch_url, partial_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_update_recipient_success(self):
        """
        ________________________ Updating Recipient Successfully ________________________
        """
        update_url = f"{self.url}{self.recipient_id}/"
        response = self.client.put(update_url, self.updated_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Bobby")
        self.assertEqual(response.data["emoji"], "🔐")

    def test_update_recipient_invalid_data(self):
        """
        ________________________ Invalid Data For PUT Request ________________________
        """
        update_url = f"{self.url}{self.recipient_id}/"
        invalid_data = {"name": "", "emoji": "🔐"}  # Blank name

        response = self.client.put(update_url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "This field may not be blank.")

    def test_update_recipient_not_found(self):
        """
        ________________________ PUT Request with Nonexistent ID ________________________
        """
        update_url = f"{self.url}nonexistent-id/"
        response = self.client.put(update_url, self.updated_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(
            str(response.data["detail"]), "No Recipient matches the given query."
        )

    def test_update_recipient_unauthorized(self):
        """
        ________________________ Unauthorized Access For PUT Request ________________________
        """
        self.client.logout()  # Log out the user to simulate unauthorized access
        update_url = f"{self.url}{self.recipient_id}/"

        response = self.client.put(update_url, self.updated_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_delete_recipient_success(self):
        """
        ________________________ Deleting Recipient Successfully ________________________
        """
        delete_url = f"{self.url}{self.recipient_id}/"
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recipient_not_found(self):
        """
        ________________________ DELETE Request with Nonexistent ID ________________________
        """
        delete_url = f"{self.url}nonexistent-id/"
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(
            str(response.data["detail"]), "No Recipient matches the given query."
        )

    def test_delete_recipient_unauthorized(self):
        """
        ________________________ Unauthorized Access For DELETE Request ________________________
        """
        self.client.logout()  # Log out the user to simulate unauthorized access
        delete_url = f"{self.url}{self.recipient_id}/"

        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
