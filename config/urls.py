"""آدرس‌های اصلی پروژهٔ نمونه‌شاپ."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("store.urls")),
]
