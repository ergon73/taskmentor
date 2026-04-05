# core/management/commands/create_demo_data.py
"""Команда для наполнения базы тестовыми данными.

Создаёт 3 клиентов и 10 задач с разными приоритетами, статусами и дедлайнами:
- 2 просроченных задачи (для демонстрации красной подсветки и высокого score)
- 2 задачи на завтра
- 3 задачи в ближайшие дни (3–7 дней)
- 2 задачи через месяц
- 1 завершённая задача (для демонстрации вывода в конце списка)
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from core.models import Client, Task


class Command(BaseCommand):
    help = 'Создаёт тестовые данные: 3 клиента, 10 задач для выбранного пользователя'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Имя пользователя (по умолчанию — первый суперпользователь или первый пользователь)',
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

        # Очистка, если передан флаг --clear
        if options['clear']:
            count = Client.objects.filter(owner=user).count()
            Client.objects.filter(owner=user).delete()
            self.stdout.write(self.style.WARNING(f'Удалено клиентов: {count} (с каскадным удалением задач)'))

        # Проверяем, есть ли уже клиенты
        if Client.objects.filter(owner=user).exists():
            self.stdout.write(self.style.WARNING(
                f'У пользователя «{user.username}» уже есть клиенты. '
                'Добавьте флаг --clear для очистки и повторного создания. Пропускаю.'
            ))
            return

        today = timezone.now().date()

        # === Создаём 3 клиентов ===
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

        clients = []
        for data in clients_data:
            client = Client.objects.create(owner=user, **data)
            clients.append(client)

        # === Создаём 10 задач ===
        tasks_data = [
            # 2 просроченных
            {
                'title': 'Подготовить отчёт о прогрессе',
                'description': 'Составить подробный отчёт об успехах клиента за последний месяц.',
                'client': clients[0],
                'due_date': today - timedelta(days=8),
                'priority': 'high',
                'status': 'new',
            },
            {
                'title': 'Анализ целей и корректировка плана',
                'description': 'Пересмотреть текущие цели, скорректировать план на квартал.',
                'client': clients[1],
                'due_date': today - timedelta(days=3),
                'priority': 'medium',
                'status': 'in_progress',
            },
            # 2 на завтра
            {
                'title': 'Еженедельный созвон с клиентом',
                'description': 'Онлайн-сессия. Обсудить результаты домашнего задания.',
                'client': clients[1],
                'due_date': today + timedelta(days=1),
                'priority': 'high',
                'status': 'in_progress',
            },
            {
                'title': 'Отправить материалы для чтения',
                'description': 'Подготовить и отправить список рекомендуемой литературы.',
                'client': clients[0],
                'due_date': today + timedelta(days=1),
                'priority': 'medium',
                'status': 'new',
            },
            # 3 в ближайшие дни
            {
                'title': 'Обновить индивидуальный план развития',
                'description': '',
                'client': clients[2],
                'due_date': today + timedelta(days=3),
                'priority': 'medium',
                'status': 'new',
            },
            {
                'title': 'Подготовить упражнения для практики',
                'description': '',
                'client': clients[2],
                'due_date': today + timedelta(days=5),
                'priority': 'low',
                'status': 'new',
            },
            {
                'title': 'Групповая сессия — подготовка материалов',
                'description': 'Подготовить план групповой встречи и раздаточные материалы.',
                'client': clients[0],
                'due_date': today + timedelta(days=7),
                'priority': 'medium',
                'status': 'new',
            },
            # 2 через месяц
            {
                'title': 'Итоговая встреча по квартальным целям',
                'description': '',
                'client': clients[0],
                'due_date': today + timedelta(days=30),
                'priority': 'high',
                'status': 'new',
            },
            {
                'title': 'Заметки по результатам месяца',
                'description': '',
                'client': clients[1],
                'due_date': today + timedelta(days=30),
                'priority': 'low',
                'status': 'new',
            },
            # 1 завершённая (внизу списка)
            {
                'title': 'Вводная встреча — знакомство и постановка целей',
                'description': 'Первичное знакомство, обсуждение целей и ожиданий от коучинга.',
                'client': clients[2],
                'due_date': today - timedelta(days=15),
                'priority': 'medium',
                'status': 'done',
            },
        ]

        for data in tasks_data:
            Task.objects.create(**data)

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Создано: {len(clients)} клиента, {len(tasks_data)} задач '
            f'для пользователя «{user.username}».'
        ))
        self.stdout.write(
            'Ожидаемый порядок в task_list (по score убывания):\n'
            '  130: Подготовить отчёт (просрочено, high)\n'
            '  120: Анализ целей (просрочено, medium)\n'
            '  80:  Созвон с клиентом (завтра, high)\n'
            '  70:  Отправить материалы (завтра, medium)\n'
            '  50:  Обновить план (3 дня, medium)\n'
            '  40:  Подготовить упражнения (5 дней, low)\n'
            '  30:  Групповая сессия (7 дней, medium)\n'
            '  30:  Итоговая встреча (30 дней, high)\n'
            '  10:  Заметки по результатам (30 дней, low)\n'
            '  —:   Вводная встреча (завершена, внизу)'
        )
