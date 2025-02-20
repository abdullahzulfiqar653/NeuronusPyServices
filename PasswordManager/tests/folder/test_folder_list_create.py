import logging
from rest_framework import status
from rest_framework.test import APITestCase
from PasswordManager.models.folder import Folder
from django.contrib.auth.models import User
from main.customclient import CustomTestClient


class TestFolderListCreateView(APITestCase):
    """Test class for listing, creating folders APIS"""

    def setUp(self):
        """Set up test users, folders, and client"""
        # Reduce log level to suppress unnecessary errors
        logger = logging.getLogger("django.request")
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        # Create test users
        self.user = User.objects.create_user(username="user", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")

        # Create folders for users
        self.folder1 = Folder.objects.create(user=self.user, title="Folder 1")
        self.folder2 = Folder.objects.create(user=self.user2, title="Folder 2")

        # Initialize custom test client
        self.client = CustomTestClient("pm:8000")
        self.url = "/api/folders/"

    def authenticate_user(self, user):
        """Authenticate a user"""
        self.client.force_authenticate(user)

    def test_list_folders(self):
        """Test that a user can only list their own folders"""
        self.authenticate_user(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        folder_titles = [
            folder["title"] for folder in response.json().get("results", [])
        ]
        self.assertCountEqual(folder_titles, ["Folder 1"])
        self.client.logout()
        # Check for user2 (should not see user1's folder)
        self.authenticate_user(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        folder_titles = [
            folder["title"] for folder in response.json().get("results", [])
        ]
        self.assertCountEqual(folder_titles, ["Folder 2"])

    def test_create_folder(self):
        """Test that a user can create a new folder"""
        self.authenticate_user(self.user)
        data = {"title": "New Folder"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        folder = Folder.objects.get(id=response.json()["id"])
        self.assertEqual(folder.title, "New Folder")
        self.assertEqual(folder.user, self.user)

    def test_retrieve_folder(self):
        """Test retrieving a folder by its owner"""
        self.authenticate_user(self.user)
        response = self.client.get(f"/api/folders/{self.folder1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.folder1.id)
        self.assertEqual(response.data["title"], "Folder 1")

    def test_retrieve_folder_not_found(self):
        """Test retrieving a folder that does not belong to the authenticated user"""
        self.authenticate_user(self.user)
        response = self.client.get(f"/api/folders/{self.folder2.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No Folder matches the given query.")

    def test_update_folder(self):
        """Test updating a folder by its owner"""
        self.authenticate_user(self.user)
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
        self.authenticate_user(self.user)
        data = {"title": "Updated Folder Title"}
        response = self.client.put(
            f"/api/folders/{self.folder2.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No Folder matches the given query.")

    def test_delete_folder(self):
        """Test deleting a folder by its owner"""
        self.authenticate_user(self.user)
        response = self.client.delete(f"/api/folders/{self.folder1.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Folder.objects.filter(id=self.folder1.id).exists())

    def test_delete_folder_not_found(self):
        """Test deleting a folder that does not belong to the authenticated user"""
        self.authenticate_user(self.user)
        response = self.client.delete(f"/api/folders/{self.folder2.id}/")

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
