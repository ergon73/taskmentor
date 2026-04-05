# core/management/commands/notify_deadlines.py
"""Management command: создаёт уведомления о дедлайнах.

Логика:
- Находит все активные задачи (new, in_progress) с дедлайном <= завтра.
- Для каждой такой задачи проверяет, не было ли уже уведомления сегодня.
- Если нет — создаёт уведомление для владельца клиента.

Запуск:
    python manage.py notify_deadlines

Предполагаемый запуск: ежедневно через cron или планировщик задач.
"""

from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Task, Notification


class Command(BaseCommand):
    help = 'Создаёт уведомления о задачах с истекающим или просроченным дедлайном'

    def handle(self, *args, **options):
        # timezone.localdate() → дата в TIME_ZONE (Europe/Moscow), не UTC.
        # Важно: при USE_TZ=True timezone.now().date() даёт UTC-дату,
        # которая может отличаться от московской в ночные часы.
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)

        # Явные границы «сегодня» как datetime-диапазон.
        # make_aware() без аргументов использует TIME_ZONE из settings.
        # Это позволяет избежать __date lookup на DateTimeField при USE_TZ=True:
        # SQLite вызывает django_datetime_cast_date() с zoneinfo-конвертацией,
        # которая на Windows падает молча без пакета tzdata → always False.
        today_start = timezone.make_aware(datetime.combine(today, time.min))
        tomorrow_start = timezone.make_aware(datetime.combine(tomorrow, time.min))

        # Активные задачи с дедлайном сегодня или раньше (просрочены),
        # либо с дедлайном завтра
        tasks = Task.objects.filter(
            status__in=['new', 'in_progress'],
            due_date__lte=tomorrow,
        ).select_related('client__owner')

        created_count = 0

        for task in tasks:
            # Пропускаем, если уведомление за сегодня уже создано.
            # Используем __gte/__lt вместо __date — надёжно на SQLite+Windows.
            already_notified = Notification.objects.filter(
                task=task,
                created_at__gte=today_start,
                created_at__lt=tomorrow_start,
            ).exists()

            if already_notified:
                continue

            # Формируем текст уведомления
            if task.due_date < today:
                text = (
                    f'⚠️ Просрочена задача «{task.title}» '
                    f'(клиент: {task.client.name}, '
                    f'дедлайн: {task.due_date.strftime("%d.%m.%Y")})'
                )
            else:
                text = (
                    f'⏰ Завтра дедлайн задачи «{task.title}» '
                    f'(клиент: {task.client.name}, '
                    f'дедлайн: {task.due_date.strftime("%d.%m.%Y")})'
                )

            Notification.objects.create(
                user=task.client.owner,
                text=text,
                task=task,
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'notify_deadlines: создано {created_count} уведомлений '
                f'(проверено {tasks.count()} задач).'
            )
        )
