from django.urls import path

from GhostTransfer.views import FileShareView, FileShareAccessView
from main.views.file_url import FileUrlCreateAPIView

urlpatterns = [
    # =====================================================
    # File Share
    # =====================================================
    path(
        "file-share/generate-url/",
        FileShareView.as_view(),
        name="generate-file-share-url-view",
    ),
    path("share/<str:pk>/", FileShareAccessView.as_view(), name="fileshare-access"),
    # =====================================================
    # Media
    # =====================================================
    path("media/upload-file/", FileUrlCreateAPIView.as_view(), name="presigned-url"),
]
