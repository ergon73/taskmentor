# core/management/commands/create_demo_fixture.py
"""Management command: создаёт fixtures/demo_data.json.

Данные:
  1 demo-пользователь  (username=demo, password=demo12345)
  5 клиентов
  15 задач (3 на клиента, разные статусы/приоритеты/дедлайны)
  30 записей самочувствия (6 на клиента, 6 последних дней)
  5 уведомлений (2 прочитанных, 3 непрочитанных)

Запуск:
    python manage.py create_demo_fixture

Загрузка:
    python manage.py loaddata demo_data
"""

import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core import serializers
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Client, Task, MoodEntry, Notification


class Command(BaseCommand):
    help = 'Создаёт fixtures/demo_data.json с демонстрационными данными'

    DEMO_USERNAME = 'demo'
    DEMO_PASSWORD = 'demo12345'
    DEMO_EMAIL = 'demo@taskmentor.ru'

    def handle(self, *args, **options):
        today = timezone.localdate()

        # ── 1. Demo-пользователь ────────────────────────────────────────────
        user, created = User.objects.get_or_create(
            username=self.DEMO_USERNAME,
            defaults={'email': self.DEMO_EMAIL, 'first_name': 'Demo', 'last_name': 'User'},
        )
        if created:
            user.set_password(self.DEMO_PASSWORD)
            user.save()
        else:
            # Убеждаемся, что пароль актуален
            user.set_password(self.DEMO_PASSWORD)
            user.save(update_fields=['password'])

        # ── 2. Чистим старые demo-данные ────────────────────────────────────
        Client.objects.filter(owner=user).delete()   # каскадно: tasks, mood_entries
        Notification.objects.filter(user=user).delete()

        # ── 3. Пять клиентов ────────────────────────────────────────────────
        clients_spec = [
            ('Анна Смирнова',    'anna@example.com',    '+7 900 111-22-33',
             'Цель: снижение тревожности. Работает менеджером среднего звена.'),
            ('Михаил Кузнецов',  'mikhail@example.com', '+7 900 444-55-66',
             'Карьерный коучинг. Хочет сменить сферу деятельности.'),
            ('Елена Петрова',    'elena@example.com',   '',
             'Работа над самооценкой. Начало сессий: январь 2026.'),
            ('Алексей Воронов',  'aleksey@example.com', '+7 900 777-88-99',
             'Тайм-менеджмент и продуктивность.'),
            ('Ольга Титова',     'olga@example.com',    '+7 900 000-11-22',
             'Семейный коучинг. Баланс работы и личной жизни.'),
        ]
        clients = [
            Client.objects.create(owner=user, name=n, email=e, phone=p, notes=nt)
            for n, e, p, nt in clients_spec
        ]

        # ── 4. Пятнадцать задач (3 на клиента) ──────────────────────────────
        # Формат: (client_idx, title, due_offset_days, priority, status)
        tasks_spec = [
            # Анна Смирнова
            (0, 'Подготовить план первых сессий',                     -12, 'high',   'done'),
            (0, 'Отправить домашнее задание по дыхательным практикам', -2, 'medium', 'in_progress'),
            (0, 'Согласовать расписание на май',                       15, 'low',    'new'),
            # Михаил Кузнецов
            (1, 'Провести анализ сильных сторон (колесо баланса)',      -5, 'high',   'done'),
            (1, 'Составить список целевых компаний',                     1, 'high',   'in_progress'),
            (1, 'Подготовить резюме для новой сферы',                    7, 'medium', 'new'),
            # Елена Петрова
            (2, 'Провести вводную диагностику самооценки',              -8, 'medium', 'done'),
            (2, 'Проработать аффирмации на неделю',                      0, 'medium', 'in_progress'),
            (2, 'Заполнить дневник успехов за март',                     3, 'low',    'new'),
            # Алексей Воронов
            (3, 'Разбор матрицы Эйзенхауэра',                          -1, 'high',   'in_progress'),
            (3, 'Настроить Pomodoro-систему',                            2, 'medium', 'new'),
            (3, 'Обсудить итоги эксперимента с расписанием',            10, 'low',    'new'),
            # Ольга Титова
            (4, 'Провести семейную сессию (диагностика)',               -3, 'high',   'done'),
            (4, 'Выдать материалы по активному слушанию',                1, 'high',   'in_progress'),
            (4, 'Запланировать совместный разбор ролей',                14, 'medium', 'new'),
        ]
        tasks = [
            Task.objects.create(
                client=clients[ci],
                title=title,
                due_date=today + timedelta(days=offset),
                priority=priority,
                status=status,
            )
            for ci, title, offset, priority, status in tasks_spec
        ]

        # ── 5. Тридцать записей самочувствия (6 дней × 5 клиентов) ─────────
        mood_patterns = [
            [3, 4, 3, 5, 4, 4],   # Анна — стабильно хорошо
            [2, 3, 2, 4, 3, 4],   # Михаил — положительная динамика
            [4, 4, 5, 4, 5, 5],   # Елена — очень хорошо
            [2, 2, 3, 2, 3, 3],   # Алексей — низкий уровень, медленный рост
            [3, 4, 4, 3, 4, 4],   # Ольга — ровно
        ]
        mood_comments = [
            ['Чувствую усталость', '', 'Хороший день', 'Отличное настроение!', '', 'Спокойно'],
            ['Тревога с утра', 'Немного лучше', '', 'Продуктивный день', '', 'Есть прогресс'],
            ['Всё хорошо', 'Отличный день', 'На подъёме', '', 'Очень доволен/а', ''],
            ['Устал/а', 'Трудно сосредоточиться', 'Немного лучше', '', 'Поработал/а над расписанием', ''],
            ['Нормально', 'Хороший разговор с семьёй', '', 'Небольшая тревога', 'Лучше', ''],
        ]
        mood_count = 0
        for client, scores, comments in zip(clients, mood_patterns, mood_comments):
            for day_i, (score, comment) in enumerate(zip(scores, comments)):
                MoodEntry.objects.create(
                    client=client,
                    date=today - timedelta(days=5 - day_i),
                    score=score,
                    comment=comment,
                )
                mood_count += 1

        # ── 6. Пять уведомлений ─────────────────────────────────────────────
        active_tasks = [t for t in tasks if t.status != 'done']
        overdue = [t for t in active_tasks if t.due_date < today]
        upcoming = [t for t in active_tasks if t.due_date >= today]

        def notif_text(task):
            if task.due_date < today:
                return (
                    f'⚠️ Просрочена задача «{task.title}» '
                    f'(клиент: {task.client.name}, '
                    f'дедлайн: {task.due_date.strftime("%d.%m.%Y")})'
                )
            elif task.due_date == today + timedelta(days=1):
                return (
                    f'⏰ Завтра дедлайн задачи «{task.title}» '
                    f'(клиент: {task.client.name}, '
                    f'дедлайн: {task.due_date.strftime("%d.%m.%Y")})'
                )
            else:
                return (
                    f'⏰ Скоро дедлайн задачи «{task.title}» '
                    f'(клиент: {task.client.name}, '
                    f'дедлайн: {task.due_date.strftime("%d.%m.%Y")})'
                )

        # 2 прочитанных (из просроченных) + 3 непрочитанных (из ближайших)
        pool_read = overdue[:2]
        pool_unread = (overdue[2:] + upcoming)[:3]
        notifs_created = 0
        for task in pool_read:
            Notification.objects.create(user=user, task=task, text=notif_text(task), is_read=True)
            notifs_created += 1
        for task in pool_unread:
            Notification.objects.create(user=user, task=task, text=notif_text(task), is_read=False)
            notifs_created += 1

        # ── 7. Сериализация → fixtures/demo_data.json ───────────────────────
        fixtures_dir = os.path.join(settings.BASE_DIR, 'fixtures')
        os.makedirs(fixtures_dir, exist_ok=True)
        fixture_path = os.path.join(fixtures_dir, 'demo_data.json')

        all_objects = (
            list(User.objects.filter(pk=user.pk))
            + list(Client.objects.filter(owner=user).order_by('pk'))
            + list(Task.objects.filter(client__owner=user).order_by('pk'))
            + list(MoodEntry.objects.filter(client__owner=user).order_by('pk'))
            + list(Notification.objects.filter(user=user).order_by('pk'))
        )

        data = serializers.serialize('json', all_objects, indent=2)
        with open(fixture_path, 'w', encoding='utf-8') as f:
            f.write(data)

        self.stdout.write(self.style.SUCCESS(
            f'Fixture создан: {fixture_path}\n'
            f'  Пользователь: {self.DEMO_USERNAME} / {self.DEMO_PASSWORD}\n'
            f'  Клиентов: {len(clients)}\n'
            f'  Задач: {len(tasks)}\n'
            f'  Mood-записей: {mood_count}\n'
            f'  Уведомлений: {notifs_created}\n'
            f'\nЗагрузить: python manage.py loaddata demo_data'
        ))
