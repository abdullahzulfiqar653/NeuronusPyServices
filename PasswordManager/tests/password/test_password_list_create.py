from rest_framework import status
from PasswordManager.models.password import Password
from PasswordManager.models.folder import Folder
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from main.customclient import CustomTestClient


class BasePasswordTest(APITestCase):
    """Base test class for password tests that sets up common objects"""

    def setUp(self) -> None:
        """Set up common test data for passwords and folders"""
        self.user = User.objects.create_user(username="user", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")

        self.folder1 = Folder.objects.create(user=self.user, title="Folder 1")
        self.folder2 = Folder.objects.create(user=self.user2, title="Folder 2")

        self.client = CustomTestClient("pm:8000")
        self.url = "/api/passwords/"

        self.folder = self.folder1
        self.data = {
            "url": "http://example.com",
            "notes": "Sample password notes",
            "title": "Test Password",
            "emoji": "🔒",
            "folder": self.folder.id,
            "username": "user123",
            "password": "secret123",
        }
        self.client.force_authenticate(self.user)


class TestListCreatePassword(BasePasswordTest):
    """Test class for listing and creating password entries"""

    def test_create_password_entry(self):
        """Test that a password entry can be created successfully"""
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        password_entry = Password.objects.get(id=response.data["id"])

        self.assertEqual(password_entry.title, self.data["title"])
        self.assertEqual(password_entry.username, self.data["username"])
        self.assertEqual(password_entry.folder.id, self.data["folder"])

    def test_list_passwords(self):
        """Test that a user can list their passwords"""
        # Create a password entry for the authenticated user
        Password.objects.create(
            url="http://example.com",
            notes="Password 1",
            title="Password 1",
            emoji="🔒",
            folder=self.folder,
            username="user123",
            password="secret123",
            user=self.user,
        )

        # List the passwords for the authenticated user
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the created password is included in the response
        password_titles = [password["title"] for password in response.json()["results"]]
        self.assertIn("Password 1", password_titles)

    def test_folder_not_belonging_to_user(self):
        """Test that the folder must belong to the user"""
        self.data["folder"] = self.folder2.id
        response = self.client.post(self.url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("folder", response.data)

    def test_duplicate_title(self):
        """Test that a password entry cannot have a duplicate title"""
        Password.objects.create(
            url="http://oldpassword.com",
            notes="Old password notes",
            title="Test Password",
            emoji="🔑",
            folder=self.folder,
            username="olduser",
            password="oldpassword123",
            user=self.user,
        )

        response = self.client.post(self.url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_create_password_with_file(self):
        """Test creating a password entry with an uploaded file"""
        from io import BytesIO
        from django.core.files.uploadedfile import InMemoryUploadedFile

        file_data = BytesIO(b"Sample file content")
        file = InMemoryUploadedFile(
            file_data,
            None,
            "testfile.txt",
            "text/plain",
            len(file_data.getvalue()),
            None,
        )
        self.data["file"] = file

        response = self.client.post(self.url, self.data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        password_entry = Password.objects.get(id=response.data["id"])
        self.assertIsNotNone(password_entry.file)
        self.assertEqual(password_entry.content_type, "text/plain")

    def test_create_password_without_folder(self):
        """Test that a folder is required when creating a password entry"""
        del self.data["folder"]
        response = self.client.post(self.url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("folder", response.data)

    def test_unauthorized_access(self):
        """Test that an unauthenticated user cannot access the password API"""
        # Ensure the client is not authenticated
        self.client.force_authenticate(user=None)

        # Try to list passwords
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

        # Try to create a password entry
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
