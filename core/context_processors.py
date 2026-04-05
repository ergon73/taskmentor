# core/context_processors.py
"""Контекстные процессоры приложения TaskMentor.

Данные, добавляемые автоматически в контекст каждого шаблона.
"""


def unread_notifications_count(request):
    """Добавляет количество непрочитанных уведомлений в контекст всех шаблонов.

    Используется для отображения бейджа в навигации (колокольчик).
    Активировано на Этапе 4.
    """
    if request.user.is_authenticated:
        from .models import Notification
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
