# core/urls.py
"""URL-маршруты приложения core.

Этап 1: аутентификация + дашборд.
Этап 2: клиенты, задачи.
Этап 3: самочувствие.
Этап 4: уведомления — добавляются позже.
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

    # === Клиенты ===
    path('clients/', views.client_list, name='client_list'),
    path('clients/add/', views.client_create, name='client_create'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
    path('clients/<int:client_id>/edit/', views.client_update, name='client_update'),
    path('clients/<int:client_id>/delete/', views.client_delete, name='client_delete'),

    # === Задачи ===
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/edit/', views.task_update, name='task_update'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/status/', views.task_change_status, name='task_change_status'),

    # === Самочувствие ===
    path('clients/<int:client_id>/mood/add/', views.mood_create, name='mood_create'),
    path('clients/<int:client_id>/mood/', views.mood_history, name='mood_history'),

    # === Уведомления ===
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
]
