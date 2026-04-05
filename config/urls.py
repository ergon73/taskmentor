# config/urls.py
"""Корневые URL-маршруты проекта TaskMentor."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Все маршруты приложения core
    path('', include('core.urls', namespace='core')),
]
