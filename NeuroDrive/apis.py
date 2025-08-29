from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from main.views.download_file import FileDownloadAPIView


from main.views import (
    UserSignInView,
    UserSignUpView,
    UserProfileRetrieveUpdateView,
    RefreshTokenAPIView,
)
from NeuroDrive.views import (
    DirectoryFileListCreateView,
    FileDirectoryUpdateView,
    DirectoryListCreateView,
    FileRetrieveUpdateDestroyView,
    DirectoryRetrieveUpdateDestroyView,
    FileAccessView,
    SharedLinkAccessAPIView,
    SharedLinkGenerateAPIView,
    SharedLinkSetPasswordAPIView,
)

urlpatterns = [
    # =====================================================
    # User
    # =====================================================
    path("user/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("user/generate-token/", UserSignInView.as_view(), name="generate-token"),
    path(
        "user/generate-pass-phrase/",
        UserSignUpView.as_view(),
        name="generate-pass-phrase",
    ),
    path(
        "user/profile/",
        UserProfileRetrieveUpdateView.as_view(),
        name="user-profile-retrieve-update-delete",
    ),
    path("user/refresh-token/", RefreshTokenAPIView.as_view(), name="refresh-token"),
    # =====================================================
    # Media
    # =====================================================
    path(
        "media/file-download/",
        FileDownloadAPIView.as_view(),
        name="file-download-view",
    ),
    # =====================================================
    # Directories
    # =====================================================
    path(
        "directories/", DirectoryListCreateView.as_view(), name="directory-list-create"
    ),
    path(
        "directories/<str:pk>/",
        DirectoryRetrieveUpdateDestroyView.as_view(),
        name="directory-retrieve-update-destroy",
    ),
    path(
        "directories/<str:directory_id>/files/",
        DirectoryFileListCreateView.as_view(),
        name="file-list-create",
    ),
    path(
        "directories/<str:directory_id>/files/<str:file_id>/",
        FileDirectoryUpdateView.as_view(),
        name="file-directory-update",
    ),
    # =====================================================
    # Files
    # =====================================================
    path(
        "files/<str:pk>/",
        FileRetrieveUpdateDestroyView.as_view(),
        name="file-retrieve-update-destroy",
    ),
    path(
        "files/password-protected/<str:pk>/",
        FileAccessView.as_view(),
        name="file-access",
    ),
    # =====================================================
    # Shared Links
    # =====================================================
  # urls.py
path("links/generate/", SharedLinkGenerateAPIView.as_view(), name="sharedlink-generate"),
path("links/<slug:key>/", SharedLinkAccessAPIView.as_view(), name="sharedlink-access"),
path("links/<slug:key>/set-password/", SharedLinkSetPasswordAPIView.as_view(), name="sharedlink-set-password"),

]
