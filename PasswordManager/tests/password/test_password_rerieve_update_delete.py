from rest_framework import status
from rest_framework.test import APITestCase
from PasswordManager.models.password import Password
from django.contrib.auth.models import User
from PasswordManager.models.folder import Folder
from main.customclient import CustomTestClient


class TestPasswordRetrieveUpdateDelete(APITestCase):

    def setUp(self):
        # Create users for testing
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpassword1"
        )

        # Create folder and password entry
        self.folder = Folder.objects.create(user=self.user, title="Test Folder")
        self.password = Password.objects.create(
            url="http://password.com",
            notes="Old password notes",
            title="Test Password",
            emoji="🔑",
            folder=self.folder,
            username="testuser",
            password="testpassword",
            user=self.user,
        )

        self.url = f"/api/passwords/{self.password.id}/"
        self.client = CustomTestClient("pm:8000")

    def test_get_password_success(self):
        """Test retrieving a password entry successfully"""
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.password.title)
        self.assertEqual(response.data["url"], self.password.url)

    def test_get_password_unauthorized(self):
        """Test that an unauthorized user cannot retrieve a password entry"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_password_success(self):
        """Test updating a password entry with patch"""
        patch_data = {"title": "Partially Updated Test Password"}

        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url, patch_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Partially Updated Test Password")
        self.assertEqual(response.data["url"], self.password.url)

    def test_patch_password_forbidden(self):
        """Test that a different user cannot update the password"""
        patch_data = {"title": "Unauthorized User Update"}

        self.client.force_authenticate(self.user1)
        response = self.client.patch(self.url, patch_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_password_invalid_data(self):
        """Test that invalid data (e.g. empty title) returns an error"""
        patch_data = {
            "title": ""  # Title should not be empty based on model constraints
        }

        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url, patch_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_put_password_success(self):
        """Test updating a password entry with put"""
        updated_data = {
            "title": "Updated Test Password",
            "url": "http://updatedpassword.com",
            "username": "testuser",
            "password": "newpassword123",
            "folder": self.folder.id,
        }

        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, updated_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Test Password")
        self.assertEqual(response.data["url"], "http://updatedpassword.com")
        self.assertEqual(response.data["password"], "newpassword123")

    def test_put_password_failure_unauthorized(self):
        """Test that an unauthorized user cannot update a password entry"""
        updated_data = {
            "title": "Updated Test Password",
            "url": "http://updatedpassword.com",
            "username": "testuser",
            "password": "newpassword123",
            "folder": self.folder.id,
        }

        self.client.force_authenticate(self.user1)
        response = self.client.put(self.url, updated_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_password_success(self):
        """Test that an authenticated user can delete a password entry"""
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Password.objects.filter(id=self.password.id).exists())

    def test_delete_password_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a password entry"""
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_password_other_user(self):
        """Test that a different user cannot delete a password entry"""
        self.client.force_authenticate(self.user1)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
