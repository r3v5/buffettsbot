from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Subscriptions API microservice for Buffets On Crows",
        description="API microservice for processing crypto payments in TRC-20 USDT for getting private subscriptions on closed community of investors in Telegram",
        default_version="v1",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("tgadmin/", admin.site.urls),
    path(
        "swagger-docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/", include("subscription_service.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
