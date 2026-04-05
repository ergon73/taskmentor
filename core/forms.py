# core/forms.py
"""Формы приложения TaskMentor.

RegisterForm — регистрация пользователя.
ClientForm   — создание и редактирование клиента.
TaskForm     — создание и редактирование задачи.
MoodForm     — добавляется на Этапе 3.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Client, Task


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

    Требует передачи user= в конструктор, чтобы фильтровать список клиентов.
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
