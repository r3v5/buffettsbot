from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Subscriptions API microservice",
        default_version="v1",
        description="⚙️ API microservice for processing crypto payments in TRC-20 USDT for getting private subscriptions on closed community of investors - [Buffets On Crows](https://t.me/BaffetinaYorannah) in Telegram\n\n 🤖 Telegram bot for buying subscriptions is available here -> [click here](https://t.me/Warren_on_Buffet_bot)\n\n 👤 If you're an admin of Buffets On Crows private Telegram group, go to [Admin panel](https://buffetsbot.com/tgadmin/) where you can access users, subscriptions and plans\n\n ❗️ If you want to see more specialized docs for developers go here [API docs](https://buffetsbot.com/redoc/)",
        contact=openapi.Contact(email="milleryan2003@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("tgadmin/", admin.site.urls),
    path("api/", include("subscription_service.urls")),
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
