# core/urls.py
"""URL-маршруты приложения core.

Этап 1: аутентификация + дашборд (заглушка).
Этапы 2–4: маршруты клиентов, задач, настроения, уведомлений добавляются позже.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Главная → редирект на дашборд
    path('', views.index, name='index'),
    # Дашборд
    path('dashboard/', views.dashboard, name='dashboard'),
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
