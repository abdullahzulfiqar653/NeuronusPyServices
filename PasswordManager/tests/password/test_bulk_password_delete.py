from rest_framework import status
from rest_framework.test import APITestCase
from PasswordManager.models.password import Password
from PasswordManager.models.folder import Folder
from django.contrib.auth.models import User
from main.customclient import CustomTestClient


class TestBulkPasswordDelete(APITestCase):
    def setUp(self):
        """Set up users, folders, and passwords for tests."""
        self.user = self.create_user("testuser", "testpassword")
        self.user1 = self.create_user("testuser1", "testpassword1")
        self.folder = Folder.objects.create(user=self.user, title="Test Folder")

        # Create passwords
        self.password1 = self.create_password(
            self.user, self.folder, "password1.com", "First Test Password"
        )
        self.password2 = self.create_password(
            self.user, self.folder, "password2.com", "Second Test Password"
        )

        self.url = "/api/passwords/delete/"
        self.client = CustomTestClient("pm:8000")

    def create_user(self, username, password):
        """Helper to create a user."""
        return User.objects.create_user(username=username, password=password)

    def create_password(self, user, folder, url, title):
        """Helper to create a password entry."""
        return Password.objects.create(
            url=f"http://{url}",
            notes=f"{title} notes",
            title=title,
            emoji="🔑",
            folder=folder,
            username=user.username,
            password="testpassword",
            user=user,
        )

    def test_bulk_delete_unauthenticated(self):
        """Test that unauthenticated users cannot delete passwords."""
        delete_data = {"passwords": [self.password1.id, self.password2.id]}
        response = self.client.post(self.url, delete_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bulk_delete_authenticated_success(self):
        """Test bulk password deletion for authenticated user."""
        self.client.force_authenticate(self.user)
        delete_data = {"passwords": [self.password1.id, self.password2.id]}
        response = self.client.post(self.url, delete_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Passwords deleted successfully")
        self.assertFalse(Password.objects.filter(id=self.password1.id).exists())
        self.assertFalse(Password.objects.filter(id=self.password2.id).exists())

    def test_bulk_delete_authenticated_failure_invalid_passwords(self):
        """Test bulk deletion fails if passwords are invalid."""
        self.client.force_authenticate(self.user)
        delete_data = {"passwords": [99999]}  # Non-existent password ID
        response = self.client.post(self.url, delete_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("passwords", response.data)
        self.assertIn("does not exist", str(response.data["passwords"][0]))

    def test_bulk_delete_authenticated_other_user_passwords(self):
        """Test user cannot delete passwords that belong to another user."""
        self.client.logout()
        self.client.force_authenticate(self.user1)

        # Assuming password1 and password2 belong to another user (e.g., user2)
        delete_data = {"passwords": [self.password1.id, self.password2.id]}

        # Perform the request
        response = self.client.post(self.url, delete_data, format="json")

        # Assert the correct error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check if the error message matches exactly
        self.assertEqual(response.data[0], "Invalid password(s) specified.")

    def test_bulk_delete_authenticated_user_only_own_passwords(self):
        """Test user can only delete their own passwords."""
        self.client.force_authenticate(self.user)
        delete_data = {"passwords": [self.password1.id]}  # Only delete own password
        response = self.client.post(self.url, delete_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Passwords deleted successfully")
        self.assertFalse(Password.objects.filter(id=self.password1.id).exists())
        self.assertTrue(Password.objects.filter(id=self.password2.id).exists())
