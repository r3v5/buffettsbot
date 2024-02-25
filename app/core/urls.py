from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('tgadmin/', admin.site.urls),
    path('subscriptions/', include('subscription_service.urls')),
]