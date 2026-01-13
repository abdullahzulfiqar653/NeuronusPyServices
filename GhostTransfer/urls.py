from drf_yasg import openapi
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny


schema_view = get_schema_view(
    openapi.Info(
        title="GhostTransfer",
        default_version="v1",
        description="API documentation for GhostTransfer",
    ),
    public=True,
    permission_classes=(AllowAny,),
    patterns=[
        path("api/", include("GhostTransfer.apis")),
    ],
)

urlpatterns = [
    path("api/", include("GhostTransfer.apis")),
    path("", include("GhostTransfer.download_urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
