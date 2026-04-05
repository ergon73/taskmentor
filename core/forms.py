# core/forms.py
"""Формы приложения TaskMentor.

RegisterForm — регистрация пользователя.
ClientForm   — создание и редактирование клиента.
TaskForm     — создание и редактирование задачи.
MoodForm     — запись самочувствия клиента.
"""

import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Client, Task, MoodEntry


class RegisterForm(UserCreationForm):
    """Форма регистрации нового пользователя.

    Расширяет стандартный UserCreationForm — добавляет обязательное поле email.
    """

    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Имя пользователя'
        self.fields['password1'].widget.attrs['placeholder'] = 'Пароль'
        self.fields['password2'].widget.attrs['placeholder'] = 'Повторите пароль'


class ClientForm(forms.ModelForm):
    """Форма создания и редактирования клиента."""

    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'notes']
        labels = {
            'name': 'Имя клиента',
            'email': 'Email',
            'phone': 'Телефон',
            'notes': 'Заметки',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Иванов Алексей',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'client@example.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 900 000-00-00',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Краткая информация о клиенте, цели, особенности...',
            }),
        }


class TaskForm(forms.ModelForm):
    """Форма создания и редактирования задачи.

    Требует передачи user= в конструктор для фильтрации списка клиентов.
    Пример: TaskForm(request.POST, user=request.user)
    """

    class Meta:
        model = Task
        fields = ['title', 'description', 'client', 'due_date', 'priority', 'status']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'client': 'Клиент',
            'due_date': 'Дедлайн',
            'priority': 'Приоритет',
            'status': 'Статус',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Подготовить план занятий',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Подробности задачи...',
            }),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только клиентов текущего пользователя
        if user is not None:
            self.fields['client'].queryset = Client.objects.filter(owner=user)
        else:
            self.fields['client'].queryset = Client.objects.none()


class MoodForm(forms.ModelForm):
    """Форма добавления записи самочувствия клиента.

    Дефолтная дата — сегодня, но пользователь может изменить
    (например, ввести вчерашнюю дату задним числом).
    Логика «одна запись в день» реализована через update_or_create во view.
    """

    # Переопределяем score с читаемыми метками
    score = forms.ChoiceField(
        label='Оценка самочувствия',
        choices=[
            (1, '1 — Очень плохо'),
            (2, '2 — Плохо'),
            (3, '3 — Нормально'),
            (4, '4 — Хорошо'),
            (5, '5 — Отлично'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = MoodEntry
        fields = ['date', 'score', 'comment']
        labels = {
            'date': 'Дата',
            'comment': 'Комментарий (необязательно)',
        }
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Как прошёл день, что заметили...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Дефолтная дата — сегодня (только при создании, не при редактировании)
        if not self.instance.pk:
            self.initial.setdefault('date', datetime.date.today())

    def clean_score(self):
        """Приводим score к int (ChoiceField возвращает строку)."""
        return int(self.cleaned_data['score'])
