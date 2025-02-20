import logging
from rest_framework import status
from rest_framework.test import APITestCase
from PasswordManager.models.folder import Folder
from django.contrib.auth.models import User
from main.customclient import CustomTestClient


class BaseFolderTest(APITestCase):
    """Base test class for folder tests that sets up common objects"""

    def setUp(self) -> None:
        """Set up users and folders for the test"""
        self.user = User.objects.create_user(username="user", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")
        self.folder1 = Folder.objects.create(user=self.user, title="Folder 1")
        self.folder2 = Folder.objects.create(user=self.user2, title="Folder 2")
        self.client = CustomTestClient("pm:8000")
        self.url = "/api/folders/"


class TestRetrieveUpdateDelete(BaseFolderTest):
    """Test class for Retrieve, Update, Patch, and Delete operations"""

    def test_retrieve_folder_success(self):
        """Test retrieving a folder by its owner"""
        self.client.force_authenticate(self.user)
        response = self.client.get(f"/api/folders/{self.folder1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.folder1.id)
        self.assertEqual(response.data["title"], "Folder 1")

    def test_retrieve_folder_not_found(self):
        """Test retrieving a folder that does not belong to the authenticated user"""
        self.client.force_authenticate(self.user)  # Authenticating as user1
        response = self.client.get(
            f"/api/folders/{self.folder2.id}/"
        )  # Trying to access folder2, owned by user2

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No Folder matches the given query.")

    def test_update_folder_success(self):
        """Test updating a folder by its owner"""
        self.client.force_authenticate(self.user)
        data = {"title": "Updated Folder Title"}
        response = self.client.put(
            f"/api/folders/{self.folder1.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Folder Title")

        # Verify the folder is updated in the database
        self.folder1.refresh_from_db()
        self.assertEqual(self.folder1.title, "Updated Folder Title")

    def test_update_folder_not_found(self):
        """Test updating a folder that does not belong to the authenticated user"""
        self.client.force_authenticate(self.user)  # Authenticating as user1
        data = {"title": "Updated Folder Title"}
        response = self.client.put(
            f"/api/folders/{self.folder2.id}/", data, format="json"
        )  # Trying to update folder2, owned by user2

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No Folder matches the given query.")

    def test_patch_folder_success(self):
        """Test partially updating a folder by its owner"""
        self.client.force_authenticate(self.user)
        data = {"title": "Partially Updated Folder Title"}
        response = self.client.patch(
            f"/api/folders/{self.folder1.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Partially Updated Folder Title")

        # Verify the folder is partially updated in the database
        self.folder1.refresh_from_db()
        self.assertEqual(self.folder1.title, "Partially Updated Folder Title")

    def test_patch_folder_not_found(self):
        """Test partially updating a folder that does not belong to the authenticated user"""
        self.client.force_authenticate(self.user)  # Authenticating as user1
        data = {"title": "Partially Updated Folder Title"}
        response = self.client.patch(
            f"/api/folders/{self.folder2.id}/", data, format="json"
        )  # Trying to patch folder2, owned by user2

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No Folder matches the given query.")

    def test_delete_folder_success(self):
        """Test deleting a folder by its owner"""
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"/api/folders/{self.folder1.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Folder.objects.filter(id=self.folder1.id).exists())

    def test_delete_folder_not_found(self):
        """Test deleting a folder that does not belong to the authenticated user"""
        self.client.force_authenticate(self.user)  # Authenticating as user1
        response = self.client.delete(
            f"/api/folders/{self.folder2.id}/"
        )  # Trying to delete folder2, owned by user2

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No Folder matches the given query.")

    def test_unauthenticated_access(self):
        """Test that an unauthenticated user cannot access API endpoints"""
        endpoints = [
            (self.client.get, self.url),  # List Folders
            (
                self.client.post,
                self.url,
                {"title": "Unauthorized Folder"},
            ),  # Create Folder
            (self.client.get, f"/api/folders/{self.folder1.id}/"),  # Retrieve Folder
            (
                self.client.put,
                f"/api/folders/{self.folder1.id}/",
                {"title": "Updated"},
            ),  # Update Folder
            (self.client.delete, f"/api/folders/{self.folder1.id}/"),  # Delete Folder
        ]

        for method, url, *data in endpoints:
            response = method(url, *data, format="json") if data else method(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(
                response.data["detail"], "Authentication credentials were not provided."
            )
