# core/views.py
"""Views приложения TaskMentor.

Все views — function-based (FBV), Class-Based Views не используются.
Комментарии и docstrings — на русском языке.

Этап 1: index, register, user_login, user_logout, dashboard (заглушка).
Этапы 2–4: добавляются views клиентов, задач, настроения, уведомлений.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm


def index(request):
    """Главная страница — редирект на дашборд или страницу входа."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return redirect('core:login')


def register(request):
    """Регистрация нового пользователя.

    GET: показывает форму регистрации.
    POST: создаёт пользователя, выполняет вход, редиректит на дашборд.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Аккаунт успешно создан.')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    """Вход в систему.

    GET: показывает форму входа.
    POST: аутентифицирует пользователя и выполняет вход.
    Поддерживает параметр next для редиректа после входа.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Редирект на next, если он задан, иначе на дашборд
            next_url = request.POST.get('next') or request.GET.get('next') or 'core:dashboard'
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный логин или пароль.')

    return render(request, 'registration/login.html', {
        'next': request.GET.get('next', ''),
    })


def user_logout(request):
    """Выход из системы. Работает по GET и POST."""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('core:login')


@login_required
def dashboard(request):
    """Дашборд — главная страница приложения после входа.

    Этап 1: заглушка.
    Этап 3: полная реализация с метриками и графиками Chart.js.
    """
    return render(request, 'core/dashboard.html')
