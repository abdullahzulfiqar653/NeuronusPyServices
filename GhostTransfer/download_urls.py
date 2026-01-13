from django.urls import path
from GhostTransfer.views import FileShareAccessView

urlpatterns = [
    path("<str:pk>/", FileShareAccessView.as_view(), name="fileshare-access"),
    # path("<str:pk>", FileShareAccessView.as_view(), name="fileshare-access-no-slash"),
]
