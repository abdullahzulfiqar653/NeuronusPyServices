from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from main.customclient import CustomTestClient


class TestRecipientListCreate(APITestCase):

    def setUp(self):
        """Set up the test environment for recipient creation and listing."""
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = CustomTestClient("rsa:8000")
        self.url = "/api/recipients/"

        # Recipient data for creation
        self.recipient_data_1 = {
            "name": "Soha",
            "public_key": "MIIBIjANBgkqhkiG9w0BAQEFA...",
            "emoji": "🔒",
        }
        self.recipient_data_2 = {
            "name": "Alice",
            "public_key": "MIIBIjANBgkqhkiG9w0BAQEFA...",
            "emoji": "🔐",
        }
        self.duplicate_data = {
            "name": "Alice",
            "public_key": "MIIBIjANBgkqhkiG9w0BAQEFA...",
            "emoji": "🔐",
        }
        self.missing_emoji_data = {"name": "Alice", "public_key": "M..."}

    # __________________________Creating Recipient________
    def test_create_recipient_success(self):
        """Test successful creation of a recipient."""
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, self.recipient_data_1, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["name"], "Soha")
        self.assertEqual(response.data["public_key"], "MIIBIjANBgkqhkiG9w0BAQEFA...")
        self.assertEqual(response.data["emoji"], "🔒")

    def test_create_recipient_missing_data(self):
        """Test recipient creation with missing data."""
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("public_key", response.data)

    def test_create_recipient_unauthorized(self):
        """Test that unauthenticated users can't create recipients."""
        response = self.client.post(self.url, self.recipient_data_1, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_create_recipient_duplicate_name(self):
        """Test that duplicate recipient names are not allowed."""
        self.client.force_authenticate(self.user)
        self.client.post(self.url, self.recipient_data_2, format="json")

        response = self.client.post(self.url, self.duplicate_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            str(response.data["non_field_errors"][0]),
            "Recipient with this name already exists",
        )

    def test_create_recipient_missing_emoji(self):
        """Test recipient creation with missing emoji field."""
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, self.missing_emoji_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["name"], "Alice")
        self.assertIn("emoji", response.data)
        self.assertIsNone(response.data["emoji"])

    # ___________________________Retrieving Recipient________
    def test_list_all_recipients(self):
        """Test listing all recipients."""
        self.client.force_authenticate(self.user)
        self.client.post(self.url, self.recipient_data_1, format="json")
        self.client.post(self.url, self.recipient_data_2, format="json")

        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["name"], "Alice")
        self.assertEqual(response.data["results"][1]["name"], "Soha")

    def test_list_all_recipients_unauthorized(self):
        """Test that unauthorized users cannot list recipients."""
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
