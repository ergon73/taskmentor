# TaskMentor — Оперативный план

## Обозначения
- `[ ]` — не начато
- `[~]` — в процессе
- `[x]` — выполнено
- `[!]` — заблокировано / требует внимания
- 🔴 CRITICAL | 🟡 MEDIUM | 🟢 LOW — приоритет

---

## Статус: ЭТАП 5 ЗАВЕРШЁН ✅ — ПРОЕКТ ГОТОВ К СДАЧЕ 🎉

---

## Этап 0: Подготовка ✅

- [x] 🔴 Изучить спецификацию (CURSOR_AGENT_INSTRUCTIONS.md, WORKFLOW_GUIDE.md, wireframes)
- [x] 🔴 Получить ответы на вопросы перед стартом
- [x] 🔴 Создать venv — `py -3.12 -m venv venv` → Python 3.12
- [x] 🔴 Установить пакеты — Django 4.2.29 + python-dotenv
- [x] 🔴 `django-admin startproject config .`
- [x] 🔴 `python manage.py startapp core`
- [x] 🔴 Создать структуру папок (templates, static, management, templatetags, fixtures, docs)
- [~] 🟡 `git init` + первый коммит — запланировано в конце Этапа 1

---

## Этап 1: Каркас + аутентификация ✅

- [x] 🔴 Настроить `config/settings.py` (INSTALLED_APPS, AUTH, локаль, static, MESSAGE_TAGS, .env)
- [x] 🔴 Настроить `config/urls.py` — корневые маршруты
- [x] 🔴 Создать `core/models.py` — заглушка
- [x] 🔴 Создать `core/admin.py` — заглушка
- [x] 🔴 Создать `core/context_processors.py` (счётчик = 0, активируется на Этапе 4)
- [x] 🔴 Создать `core/forms.py` — RegisterForm
- [x] 🔴 Создать `core/views.py` — index, register, user_login, user_logout, dashboard
- [x] 🔴 Создать `core/urls.py` — маршруты Этапа 1
- [x] 🔴 Создать `core/templates/base.html` — навбар, Bootstrap 5.3 CDN, flash-сообщения
- [x] 🔴 Создать `core/templates/registration/login.html`
- [x] 🔴 Создать `core/templates/registration/register.html`
- [x] 🔴 Создать `core/templates/core/dashboard.html` — заглушка
- [x] 🔴 Создать `core/static/core/css/style.css` — оранжевая тема
- [x] 🔴 Создать `.gitignore`, `.env`
- [x] 🔴 Создать templatetags/__init__.py, core_extras.py, management/__init__ файлы
- [x] 🔴 `python manage.py check` → 0 ошибок
- [x] 🔴 `python manage.py migrate` → 18 миграций применено
- [x] 🔴 Импорт views, forms, context_processors → OK
- [x] 🟡 `git init` + первый коммит (fd1bd96)
- [x] 🟡 Ожидание ОК от пользователя → ОК получен

---

## Этап 2: Клиенты и задачи ✅

- [x] 🔴 `core/models.py` — Client, Task (score/is_overdue properties, точно по спецификации)
- [x] 🔴 `python manage.py makemigrations && migrate` → core.0001_initial OK
- [x] 🔴 `core/forms.py` — ClientForm, TaskForm (user= kwargs, фильтрация по owner)
- [x] 🔴 `core/admin.py` — ClientAdmin, TaskAdmin
- [x] 🔴 Views: client_list/detail/create/update/delete
- [x] 🔴 Views: task_list/create/update/delete/change_status
- [x] 🔴 Шаблоны: client_list/detail/form/confirm_delete
- [x] 🔴 Шаблоны: task_list/form/confirm_delete
- [x] 🔴 base.html — рабочие URL-names ({% url 'core:client_list' %} и др.)
- [x] 🔴 core/urls.py — все маршруты клиентов и задач
- [x] 🔴 create_demo_data (3 клиента, 10 задач, проверен score)
- [x] 🔴 manage.py check → 0 ошибок
- [x] 🔴 Импорты models/forms/views/admin → все OK
- [x] 🔴 Score test: 130/80/10 → OK
- [x] 🟡 git commit 74e5793
- [x] 🟡 ОК получен → переход к Этапу 3

---

## Этап 3: Самочувствие + дашборд ✅

- [x] 🔴 MoodEntry: unique_together(client,date), ordering=['-date'], SCORE_CHOICES
- [x] 🔴 makemigrations → 0002_moodentry, migrate → OK
- [x] 🔴 MoodForm: ChoiceField score c метками, default=today, clean_score→int
- [x] 🔴 MoodEntryAdmin с фильтрами date/score
- [x] 🔴 mood_create: update_or_create, flash «добавлена/обновлена»
- [x] 🔴 mood_history: полная таблица по -date
- [x] 🔴 client_detail: спарклайн Chart.js 30 дн, последние 10 записей, кнопка активна
- [x] 🔴 dashboard view: 4 метрики, status_data/mood_labels/mood_values (raw dict→json_script)
- [x] 🔴 dashboard.html: Doughnut + Line Chart.js 4.4.4, топ-5, json_script XSS-safe
- [x] 🔴 create_demo_data: 60 записей (3 клиента × 20 дней, разные паттерны)
- [x] 🔴 manage.py check → 0 ошибок; импорты всех классов → OK
- [x] 🔴 Данные дашборда: 3 кл / 9 акт / 2 просроч / настроение 3.8 / 20 точек на графике
- [x] 🟡 git commit e2873bb
- [x] 🟡 ОК получен → переход к Этапу 4

---

## Этап 4: Уведомления ✅

- [x] 🔴 `core/models.py` — модель `Notification`
- [x] 🔴 `python manage.py makemigrations && migrate` → 0003_notification OK
- [x] 🔴 Активировать `context_processors.py` — реальный счётчик из БД
- [x] 🔴 Обновить `base.html` — бейдж уведомлений активен, href на url-name
- [x] 🔴 Views: `notification_list`, `notification_mark_read`
- [x] 🔴 Шаблон: `notification_list.html`
- [x] 🔴 `core/admin.py` — `NotificationAdmin`
- [x] 🔴 Management command: `notify_deadlines` → создано 4 уведомления на demo-данных
- [x] 🔴 Обновить `core/urls.py`
- [x] 🔴 `python manage.py check` — 0 ошибок
- [x] 🟡 `git commit 918c3b4 "этап 4: уведомления, бейдж, management command"`
- [ ] 🟡 Показать пользователю → ждать ОК

---

## Этап 5: Финальная полировка ✅

- [x] 🟡 Адаптивность — `table-responsive` на всех таблицах (добавлено в client_detail.html mood-таблица), бургер-меню ✅
- [x] 🟡 Пустые состояния — все списки: clients, tasks, mood_history, notification_list, dashboard ✅
- [x] 🟡 Flash-сообщения — все CRUD: клиенты, задачи, mood, уведомления, auth ✅
- [x] 🟡 Fixtures: `demo_data.json` — 1 user / 5 clients / 15 tasks / 30 mood / 5 notifs ✅
- [x] 🟡 `pip freeze > requirements.txt` — Django 4.2.29, python-dotenv, tzdata ✅
- [x] 🟢 README.md — установка, запуск, демо-данные, management commands ✅
- [x] 🟡 Финальный `python manage.py check` — 0 ошибок ✅
- [x] 🟡 `git commit "этап 5: полировка, fixtures, requirements.txt"`
- [x] 🟡 Проект готов к сдаче ✅

---

## Решения и допущения

| # | Решение | Обоснование |
|---|---------|-------------|
| 1 | Django 4.2.29 на Python 3.12 | Точно по спецификации курса, подтверждено пользователем |
| 2 | Chart.js: raw Python dict в шаблон + `json_script` фильтр в шаблоне | Избегает двойной сериализации (`json.dumps` в view + `json_script` = двойное кодирование). Raw dict + `json_script` — корректно и защищает от XSS |
| 3 | MoodEntry.date: `default=datetime.date.today` (не `auto_now_add`) | Пользователь может захотеть внести вчерашнюю дату задним числом |
| 4 | MoodEntry «одна в день»: `update_or_create(client=..., date=...)` | Чище, чем отдельная проверка + create/update. Атомарно |
| 5 | Смена статуса: отдельная POST-view `/tasks/<id>/status/` | В task_list «умные» кнопки: new→«▶ В работу», in_progress→«✅ Завершить». Откат статуса — только через форму редактирования |
| 6 | task_list сортировка: Python sort (не DB ORDER BY) | `score` — вычисляемое свойство, не поле БД. `sorted(active, key=lambda t: t.score, reverse=True)`. Done-задачи в конце |
| 7 | Login/logout: кастомные FBV (`user_login`, `user_logout`) | Правило «только FBV» применяю строго — включая auth. Использую `authenticate()`, `login()`, `logout()` из `django.contrib.auth` |
| 8 | TaskForm: одна форма для create/edit. При create — `status='new'` форсится в view | Не нужна отдельная форма создания. Шаблон create не рендерит поле status |
| 9 | `notification_list` ordering: `order_by('is_read', '-created_at')` | False(0) < True(1), значит непрочитанные сверху. Внутри группы — свежие первыми |
| 10 | Ссылки в base.html на Клиенты/Задачи/Уведомления: hardcoded path на Этапах 1–3 | `{% url %}` бросает NoReverseMatch для незарегистрированных имён. Обновляю на URL-names в Этапах 2 и 4 |
| 11 | MESSAGE_TAGS: `ERROR → 'danger'` | Bootstrap не имеет класса `alert-error`, только `alert-danger`. Маппинг в settings.py |
| 12 | .env + python-dotenv | SECRET_KEY вне кода, .env в .gitignore. `load_dotenv()` в settings.py |
