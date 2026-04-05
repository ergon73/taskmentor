# core/management/commands/create_demo_data.py
"""Команда для наполнения базы тестовыми данными.

Создаёт 3 клиентов, 10 задач и 60 записей самочувствия (20 дней × 3 клиента)
с разными паттернами для наглядной визуализации на дашборде.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from core.models import Client, Task, MoodEntry


class Command(BaseCommand):
    help = 'Создаёт тестовые данные: 3 клиента, 10 задач, 60 записей настроения'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Имя пользователя (по умолчанию — первый суперпользователь)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Удалить существующих клиентов и задачи пользователя перед созданием',
        )

    def handle(self, *args, **options):
        # Определяем пользователя
        username = options.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'Пользователь «{username}» не найден.'))
                return
        else:
            user = (
                User.objects.filter(is_superuser=True).first()
                or User.objects.first()
            )
            if not user:
                self.stderr.write(self.style.ERROR(
                    'Нет ни одного пользователя. '
                    'Сначала выполните: python manage.py createsuperuser'
                ))
                return

        self.stdout.write(f'Пользователь: {user.username}')

        # Очистка при флаге --clear
        if options['clear']:
            count = Client.objects.filter(owner=user).count()
            Client.objects.filter(owner=user).delete()
            self.stdout.write(self.style.WARNING(f'Удалено клиентов: {count}'))

        if Client.objects.filter(owner=user).exists():
            self.stdout.write(self.style.WARNING(
                f'У «{user.username}» уже есть клиенты. '
                'Добавьте флаг --clear для повторного создания.'
            ))
            return

        today = timezone.now().date()

        # === 3 клиента ===
        clients_data = [
            {
                'name': 'Иванов Алексей',
                'email': 'ivanov@example.com',
                'phone': '+7 900 111-22-33',
                'notes': 'Карьерный коучинг. Цель — рост до тимлида. Работаем третий месяц.',
            },
            {
                'name': 'Петрова Мария',
                'email': 'petrova@example.com',
                'phone': '+7 900 444-55-66',
                'notes': 'Управление стрессом и work-life balance. Сессии каждый понедельник.',
            },
            {
                'name': 'Сидоров Константин',
                'email': 'sidorov@example.com',
                'phone': '',
                'notes': '',
            },
        ]
        clients = [Client.objects.create(owner=user, **d) for d in clients_data]

        # === 10 задач ===
        tasks_data = [
            # 2 просроченных
            {'title': 'Подготовить отчёт о прогрессе', 'description': '',
             'client': clients[0], 'due_date': today - timedelta(days=8),
             'priority': 'high', 'status': 'new'},
            {'title': 'Анализ целей и корректировка плана', 'description': '',
             'client': clients[1], 'due_date': today - timedelta(days=3),
             'priority': 'medium', 'status': 'in_progress'},
            # 2 на завтра
            {'title': 'Еженедельный созвон с клиентом', 'description': '',
             'client': clients[1], 'due_date': today + timedelta(days=1),
             'priority': 'high', 'status': 'in_progress'},
            {'title': 'Отправить материалы для чтения', 'description': '',
             'client': clients[0], 'due_date': today + timedelta(days=1),
             'priority': 'medium', 'status': 'new'},
            # 3 в ближайшие дни
            {'title': 'Обновить индивидуальный план развития', 'description': '',
             'client': clients[2], 'due_date': today + timedelta(days=3),
             'priority': 'medium', 'status': 'new'},
            {'title': 'Подготовить упражнения для практики', 'description': '',
             'client': clients[2], 'due_date': today + timedelta(days=5),
             'priority': 'low', 'status': 'new'},
            {'title': 'Групповая сессия — подготовка материалов', 'description': '',
             'client': clients[0], 'due_date': today + timedelta(days=7),
             'priority': 'medium', 'status': 'new'},
            # 2 через месяц
            {'title': 'Итоговая встреча по квартальным целям', 'description': '',
             'client': clients[0], 'due_date': today + timedelta(days=30),
             'priority': 'high', 'status': 'new'},
            {'title': 'Заметки по результатам месяца', 'description': '',
             'client': clients[1], 'due_date': today + timedelta(days=30),
             'priority': 'low', 'status': 'new'},
            # 1 завершённая (внизу списка)
            {'title': 'Вводная встреча — знакомство и постановка целей', 'description': '',
             'client': clients[2], 'due_date': today - timedelta(days=15),
             'priority': 'medium', 'status': 'done'},
        ]
        for d in tasks_data:
            Task.objects.create(**d)

        # === Записи самочувствия (20 дней × 3 клиента) ===
        # Паттерны: Иванов — улучшение, Петрова — стабильно высокое, Сидоров — рост с низкого
        mood_patterns = [
            {
                'client': clients[0],
                'scores': [3, 2, 3, 4, 3, 4, 3, 4, 4, 3, 4, 4, 3, 5, 4, 4, 5, 4, 5, 4],
                'comments': {0: 'Немного устал', 5: 'После хорошей сессии',
                             13: 'Отличная неделя!', 18: 'Чувствую прогресс'},
            },
            {
                'client': clients[1],
                'scores': [4, 3, 4, 3, 3, 4, 4, 3, 2, 3, 4, 4, 3, 4, 3, 4, 4, 3, 4, 4],
                'comments': {8: 'Сложный день на работе', 15: 'Хорошее настроение'},
            },
            {
                'client': clients[2],
                'scores': [2, 2, 3, 2, 3, 3, 2, 3, 3, 4, 3, 3, 4, 3, 4, 4, 3, 4, 4, 3],
                'comments': {0: 'Тяжело даётся', 9: 'Становится лучше',
                             16: 'Заметный прогресс'},
            },
        ]

        mood_count = 0
        for pattern in mood_patterns:
            for i, score in enumerate(pattern['scores']):
                # i=0 → 19 дней назад, i=19 → сегодня
                entry_date = today - timedelta(days=19 - i)
                comment = pattern['comments'].get(i, '')
                MoodEntry.objects.create(
                    client=pattern['client'],
                    date=entry_date,
                    score=score,
                    comment=comment,
                )
                mood_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Создано: {len(clients)} клиента, {len(tasks_data)} задач, '
            f'{mood_count} записей настроения для «{user.username}».'
        ))
