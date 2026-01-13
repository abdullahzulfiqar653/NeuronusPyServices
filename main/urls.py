from django.urls import path
from django.contrib import admin
from GhostTransfer.views import FileShareAccessView

urlpatterns = [ 
    path("admin/", admin.site.urls),
    path("<str:pk>", FileShareAccessView.as_view(), name="fileshare-access-no-slash"),

]
