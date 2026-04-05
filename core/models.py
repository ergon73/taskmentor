# core/models.py
"""Модели данных TaskMentor: клиенты, задачи, самочувствие, уведомления.

Этап 2: Client, Task
Этап 3: MoodEntry
Этап 4: Notification
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Client(models.Model):
    """Клиент специалиста (коуча, психолога, тренера)."""

    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20, blank=True, default='')
    notes = models.TextField('Заметки', max_length=2000, blank=True, default='')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='clients',
        verbose_name='Специалист'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['name']

    def __str__(self):
        return self.name

    def active_tasks_count(self):
        """Количество незавершённых задач клиента."""
        return self.tasks.exclude(status='done').count()


class Task(models.Model):
    """Задача, привязанная к клиенту специалиста."""

    PRIORITY_CHOICES = [
        ('high', 'Высокий'),
        ('medium', 'Средний'),
        ('low', 'Низкий'),
    ]
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('done', 'Завершена'),
    ]
    # Весовые коэффициенты для умной сортировки
    PRIORITY_WEIGHTS = {'high': 30, 'medium': 20, 'low': 10}

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', max_length=2000, blank=True, default='')
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='tasks',
        verbose_name='Клиент'
    )
    due_date = models.DateField('Дедлайн')
    priority = models.CharField(
        'Приоритет', max_length=10, choices=PRIORITY_CHOICES, default='medium'
    )
    status = models.CharField(
        'Статус', max_length=15, choices=STATUS_CHOICES, default='new'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Просрочена ли задача (дедлайн прошёл, задача не завершена)."""
        return self.due_date < timezone.now().date() and self.status != 'done'

    @property
    def score(self):
        """Числовой score для умной сортировки задач.

        score = вес_приоритета + бонус_за_близость_дедлайна
        """
        base = self.PRIORITY_WEIGHTS.get(self.priority, 10)
        days_left = (self.due_date - timezone.now().date()).days

        if days_left < 0:
            bonus = 100   # просрочено
        elif days_left <= 1:
            bonus = 50    # ≤ 1 день
        elif days_left <= 3:
            bonus = 30    # ≤ 3 дня
        elif days_left <= 7:
            bonus = 10    # ≤ 7 дней
        else:
            bonus = 0     # > 7 дней

        return base + bonus


class MoodEntry(models.Model):
    """Запись самочувствия клиента (одна в день)."""

    SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='mood_entries',
        verbose_name='Клиент'
    )
    date = models.DateField('Дата')
    score = models.IntegerField('Оценка', choices=SCORE_CHOICES)
    comment = models.TextField('Комментарий', max_length=500, blank=True, default='')

    class Meta:
        verbose_name = 'Запись самочувствия'
        verbose_name_plural = 'Записи самочувствия'
        unique_together = ('client', 'date')  # одна запись в день на клиента
        ordering = ['-date']

    def __str__(self):
        return f'{self.client.name} — {self.date} — {self.score}/5'
