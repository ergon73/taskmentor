# core/views.py
"""Views приложения TaskMentor.

Все views — function-based (FBV). Class-Based Views не используются.
Комментарии и docstrings на русском языке.

Этап 1: index, register, user_login, user_logout, dashboard (заглушка).
Этап 2: client_list/detail/create/update/delete, task_list/create/update/delete/change_status.
Этап 3: mood_create, mood_history, полный dashboard с Chart.js.
Этап 4: notification_list, notification_mark_read.
"""

from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.utils import timezone

from .forms import RegisterForm, ClientForm, TaskForm, MoodForm
from .models import Client, Task, MoodEntry


# ===========================================================================
# Аутентификация
# ===========================================================================

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
    POST: аутентифицирует пользователя.
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


# ===========================================================================
# Дашборд
# ===========================================================================

@login_required
def dashboard(request):
    """Дашборд — метрики, графики Chart.js, топ-5 задач."""
    user = request.user
    today = timezone.now().date()

    # --- Метрики ---
    clients_count = Client.objects.filter(owner=user).count()

    active_tasks_qs = Task.objects.filter(
        client__owner=user
    ).exclude(status='done').select_related('client')
    active_count = active_tasks_qs.count()
    overdue_count = active_tasks_qs.filter(due_date__lt=today).count()

    # Среднее настроение за последние 7 дней
    week_ago = today - timedelta(days=7)
    avg_mood_result = MoodEntry.objects.filter(
        client__owner=user, date__gte=week_ago
    ).aggregate(avg=Avg('score'))['avg']
    avg_mood_display = f'{round(avg_mood_result, 1)}' if avg_mood_result else '—'

    # --- Данные для Doughnut-графика (задачи по статусам) ---
    all_tasks_qs = Task.objects.filter(client__owner=user)
    status_data = {
        'new': all_tasks_qs.filter(status='new').count(),
        'in_progress': all_tasks_qs.filter(status='in_progress').count(),
        'done': all_tasks_qs.filter(status='done').count(),
    }

    # --- Данные для Line-графика (среднее настроение за 30 дней) ---
    thirty_days_ago = today - timedelta(days=30)
    mood_qs = list(
        MoodEntry.objects
        .filter(client__owner=user, date__gte=thirty_days_ago)
        .values('date')
        .annotate(avg_score=Avg('score'))
        .order_by('date')
    )
    mood_labels = [entry['date'].isoformat() for entry in mood_qs]
    mood_values = [round(float(entry['avg_score']), 1) for entry in mood_qs]

    # --- Топ-5 задач по умной сортировке ---
    top_tasks = sorted(active_tasks_qs, key=lambda t: t.score, reverse=True)[:5]

    return render(request, 'core/dashboard.html', {
        'clients_count': clients_count,
        'active_count': active_count,
        'overdue_count': overdue_count,
        'avg_mood_display': avg_mood_display,
        # raw dict/list — json_script в шаблоне выполнит сериализацию безопасно
        'status_data': status_data,
        'mood_labels': mood_labels,
        'mood_values': mood_values,
        'top_tasks': top_tasks,
    })


# ===========================================================================
# Клиенты
# ===========================================================================

@login_required
def client_list(request):
    """Список клиентов текущего пользователя с поиском по имени и email."""
    query = request.GET.get('q', '').strip()
    clients = Client.objects.filter(owner=request.user)
    if query:
        clients = clients.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )
    return render(request, 'core/client_list.html', {
        'clients': clients,
        'query': query,
    })


@login_required
def client_detail(request, client_id):
    """Карточка клиента: информация, задачи, история настроения и спарклайн."""
    client = get_object_or_404(Client, id=client_id, owner=request.user)

    # Задачи клиента: активные по score, завершённые в конце
    client_tasks = list(client.tasks.all())
    active_tasks = sorted(
        [t for t in client_tasks if t.status != 'done'],
        key=lambda t: t.score,
        reverse=True
    )
    done_tasks = [t for t in client_tasks if t.status == 'done']

    # Последние 10 записей самочувствия (для таблицы)
    mood_entries = MoodEntry.objects.filter(client=client)[:10]

    # Данные для спарклайна (30 дней, упорядочены по дате возрастания)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    sparkline_qs = list(
        MoodEntry.objects.filter(client=client, date__gte=thirty_days_ago)
        .order_by('date').values('date', 'score')
    )
    spark_labels = [e['date'].isoformat() for e in sparkline_qs]
    spark_values = [e['score'] for e in sparkline_qs]

    return render(request, 'core/client_detail.html', {
        'client': client,
        'active_tasks': active_tasks,
        'done_tasks': done_tasks,
        'mood_entries': mood_entries,
        'spark_labels': spark_labels,
        'spark_values': spark_values,
    })


@login_required
def client_create(request):
    """Создание нового клиента. owner устанавливается автоматически."""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.owner = request.user
            client.save()
            messages.success(request, f'Клиент «{client.name}» успешно добавлен.')
            return redirect('core:client_detail', client_id=client.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ClientForm()

    return render(request, 'core/client_form.html', {'form': form, 'client': None})


@login_required
def client_update(request, client_id):
    """Редактирование данных клиента."""
    client = get_object_or_404(Client, id=client_id, owner=request.user)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Данные клиента «{client.name}» обновлены.')
            return redirect('core:client_detail', client_id=client.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ClientForm(instance=client)

    return render(request, 'core/client_form.html', {'form': form, 'client': client})


@login_required
def client_delete(request, client_id):
    """Удаление клиента с подтверждением. Каскадно удаляет задачи и записи настроения."""
    client = get_object_or_404(Client, id=client_id, owner=request.user)

    if request.method == 'POST':
        name = client.name
        client.delete()
        messages.success(request, f'Клиент «{name}» удалён.')
        return redirect('core:client_list')

    return render(request, 'core/client_confirm_delete.html', {'client': client})


# ===========================================================================
# Задачи
# ===========================================================================

@login_required
def task_list(request):
    """Список всех задач пользователя с умной сортировкой.

    Активные: сортируются по score (убывание).
    Завершённые: в конце таблицы, без сортировки по score.
    """
    all_tasks = Task.objects.filter(
        client__owner=request.user
    ).select_related('client')
    active_tasks = sorted(
        [t for t in all_tasks if t.status != 'done'],
        key=lambda t: t.score,
        reverse=True
    )
    done_tasks = list(all_tasks.filter(status='done'))

    return render(request, 'core/task_list.html', {
        'active_tasks': active_tasks,
        'done_tasks': done_tasks,
    })


@login_required
def task_create(request):
    """Создание новой задачи.

    Статус принудительно устанавливается в 'new' при создании.
    GET-параметр ?client=<id> позволяет предварительно выбрать клиента
    (используется при переходе из карточки клиента).
    """
    initial = {}
    client_id = request.GET.get('client')
    if client_id:
        initial['client'] = client_id

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'new'  # принудительно при создании
            task.save()
            messages.success(request, f'Задача «{task.title}» создана.')
            return redirect('core:task_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = TaskForm(initial=initial, user=request.user)

    return render(request, 'core/task_form.html', {'form': form, 'task': None})


@login_required
def task_update(request, task_id):
    """Редактирование задачи. Доступны все поля, включая статус."""
    task = get_object_or_404(Task, id=task_id, client__owner=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Задача «{task.title}» обновлена.')
            return redirect('core:task_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, 'core/task_form.html', {'form': form, 'task': task})


@login_required
def task_delete(request, task_id):
    """Удаление задачи с подтверждением."""
    task = get_object_or_404(Task, id=task_id, client__owner=request.user)

    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Задача «{title}» удалена.')
        return redirect('core:task_list')

    return render(request, 'core/task_confirm_delete.html', {'task': task})


@login_required
def task_change_status(request, task_id):
    """Смена статуса задачи: new → in_progress → done. Только POST.

    Редиректит обратно на страницу, с которой пришёл запрос (HTTP_REFERER),
    или на список задач, если referer не определён.
    """
    if request.method != 'POST':
        return redirect('core:task_list')

    task = get_object_or_404(Task, id=task_id, client__owner=request.user)

    next_status_map = {
        'new': 'in_progress',
        'in_progress': 'done',
    }
    next_status = next_status_map.get(task.status)

    if next_status:
        old_display = task.get_status_display()
        task.status = next_status
        task.save()
        new_display = task.get_status_display()
        messages.success(
            request,
            f'Задача «{task.title}»: {old_display} → {new_display}'
        )

    referer = request.META.get('HTTP_REFERER', '')
    if referer:
        return redirect(referer)
    return redirect('core:task_list')


# ===========================================================================
# Самочувствие
# ===========================================================================

@login_required
def mood_create(request, client_id):
    """Добавление (или обновление) записи самочувствия клиента.

    Ограничение «одна запись в день» реализовано через update_or_create:
    если запись за эту дату уже есть — обновляется, иначе создаётся новая.
    """
    client = get_object_or_404(Client, id=client_id, owner=request.user)

    if request.method == 'POST':
        form = MoodForm(request.POST)
        if form.is_valid():
            entry_date = form.cleaned_data['date']
            score = form.cleaned_data['score']
            comment = form.cleaned_data['comment']

            _, created = MoodEntry.objects.update_or_create(
                client=client,
                date=entry_date,
                defaults={'score': score, 'comment': comment},
            )

            verb = 'добавлена' if created else 'обновлена'
            messages.success(
                request,
                f'Запись самочувствия за {entry_date.strftime("%d.%m.%Y")} {verb}.'
            )
            return redirect('core:client_detail', client_id=client.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = MoodForm()

    return render(request, 'core/mood_form.html', {
        'form': form,
        'client': client,
    })


@login_required
def mood_history(request, client_id):
    """Полная история самочувствия клиента (все записи, по убыванию даты)."""
    client = get_object_or_404(Client, id=client_id, owner=request.user)
    entries = MoodEntry.objects.filter(client=client)  # ordering = ['-date'] из Meta

    return render(request, 'core/mood_history.html', {
        'client': client,
        'entries': entries,
    })
