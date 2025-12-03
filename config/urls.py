"""URL configuration for the project."""
from django.contrib import admin
from django.urls import path

from dashboard.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
]