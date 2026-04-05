# TaskMentor — Оперативный план

## Обозначения
- `[ ]` — не начато
- `[~]` — в процессе
- `[x]` — выполнено
- `[!]` — заблокировано / требует внимания
- 🔴 CRITICAL | 🟡 MEDIUM | 🟢 LOW — приоритет

---

## Статус: ЭТАП 2 — В ПРОЦЕССЕ

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

## Этап 2: Клиенты и задачи (дни 3–5) ← ТЕКУЩИЙ

- [~] 🔴 `core/models.py` — модели `Client`, `Task` (точно по спецификации)
- [ ] 🔴 `python manage.py makemigrations && migrate`
- [ ] 🔴 `core/forms.py` — `ClientForm`, `TaskForm` (фильтрация клиентов по owner)
- [ ] 🔴 `core/admin.py` — `ClientAdmin`, `TaskAdmin`
- [ ] 🔴 Views: `client_list`, `client_detail`, `client_create`, `client_update`, `client_delete`
- [ ] 🔴 Views: `task_list`, `task_create`, `task_update`, `task_delete`, `task_change_status`
- [ ] 🔴 Шаблоны: `client_list.html`, `client_detail.html`, `client_form.html`, `client_confirm_delete.html`
- [ ] 🔴 Шаблоны: `task_list.html`, `task_form.html`, `task_confirm_delete.html`
- [ ] 🔴 Обновить `base.html` — рабочие URL-names в навигации
- [ ] 🔴 Обновить `core/urls.py` — все маршруты клиентов и задач
- [ ] 🔴 Management command: `create_demo_data` (3 клиента, 10 задач)
- [ ] 🔴 `python manage.py check` — 0 ошибок
- [ ] 🔴 Проверить импорты: `python -c "from core.models import Client, Task"`
- [ ] 🟡 `git commit "этап 2: CRUD клиентов и задач, умная сортировка"`
- [ ] 🟡 Показать пользователю → ждать ОК

---

## Этап 3: Самочувствие + дашборд (дни 6–8)

- [ ] 🔴 `core/models.py` — модель `MoodEntry`
- [ ] 🔴 `python manage.py makemigrations && migrate`
- [ ] 🔴 `core/forms.py` — `MoodForm`
- [ ] 🔴 `core/admin.py` — `MoodEntryAdmin`
- [ ] 🔴 Views: `mood_create`, `mood_history`
- [ ] 🔴 Шаблоны: `mood_form.html`, `mood_history.html`
- [ ] 🔴 Обновить `client_detail.html` — задачи клиента + история настроения + мини-график
- [ ] 🔴 Реализовать полный `dashboard` view (метрики, данные для Chart.js)
- [ ] 🔴 Шаблон `dashboard.html` — 4 карточки, 2 графика Chart.js, топ-5 задач
- [ ] 🔴 Обновить `create_demo_data` — добавить MoodEntry за 20 дней
- [ ] 🔴 `python manage.py check` — 0 ошибок
- [ ] 🟡 `git commit "этап 3: самочувствие, дашборд, Chart.js"`
- [ ] 🟡 Показать пользователю → ждать ОК

---

## Этап 4: Уведомления (дни 9–11)

- [ ] 🔴 `core/models.py` — модель `Notification`
- [ ] 🔴 `python manage.py makemigrations && migrate`
- [ ] 🔴 Активировать `context_processors.py` — реальный счётчик из БД
- [ ] 🔴 Обновить `base.html` — бейдж уведомлений активен
- [ ] 🔴 Views: `notification_list`, `notification_mark_read`
- [ ] 🔴 Шаблон: `notification_list.html`
- [ ] 🔴 `core/admin.py` — `NotificationAdmin`
- [ ] 🔴 Management command: `notify_deadlines` (точно по спецификации)
- [ ] 🔴 Обновить `core/urls.py`
- [ ] 🔴 `python manage.py check` — 0 ошибок
- [ ] 🟡 `git commit "этап 4: уведомления, бейдж, management command"`
- [ ] 🟡 Показать пользователю → ждать ОК

---

## Этап 5: Финальная полировка (дни 12–14)

- [ ] 🟡 Адаптивность — `table-responsive`, бургер-меню на мобильном
- [ ] 🟡 Пустые состояния для всех списков
- [ ] 🟡 Flash-сообщения после всех CRUD-действий
- [ ] 🟡 Fixtures: `demo_data.json` (1 demo-пользователь, 5 клиентов, 15 задач, 30 mood-записей, 5 уведомлений)
- [ ] 🟡 `pip freeze > requirements.txt`
- [ ] 🟢 Обновить README.md
- [ ] 🟡 Финальный `python manage.py check`
- [ ] 🟡 `git commit "этап 5: полировка, fixtures, requirements.txt"`
- [ ] 🟡 Показать пользователю → финальная сдача

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
