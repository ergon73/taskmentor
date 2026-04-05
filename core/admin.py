# core/admin.py
"""Настройки Django Admin для TaskMentor.

Этап 2: ClientAdmin, TaskAdmin
Этап 3: MoodEntryAdmin
Этап 4: NotificationAdmin
"""

from django.contrib import admin
from .models import Client, Task, MoodEntry


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Клиенты в Django Admin."""

    list_display = ('name', 'email', 'phone', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('name', 'email')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Задачи в Django Admin."""

    list_display = ('title', 'client', 'priority', 'status', 'due_date')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('title', 'client__name')


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    """Записи самочувствия в Django Admin."""

    list_display = ('client', 'date', 'score', 'comment')
    list_filter = ('date', 'score')
    search_fields = ('client__name',)
