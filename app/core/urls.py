from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("tgadmin/", admin.site.urls),
    path("api/", include("subscription_service.urls")),
]
