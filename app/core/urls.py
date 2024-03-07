from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("tgadmin/", admin.site.urls),
    path("api/", include("subscription_service.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
