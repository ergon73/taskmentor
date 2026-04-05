# config/settings.py
"""Настройки Django-проекта TaskMentor.

Секреты читаются из файла .env через python-dotenv.
.env не коммитится в git — см. .gitignore.
"""

import os
from pathlib import Path
from django.contrib.messages import constants as messages_constants
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# === БЕЗОПАСНОСТЬ ===
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-insecure-key-set-in-env')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# === ПРИЛОЖЕНИЯ ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # основное приложение TaskMentor
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Бейдж уведомлений в навигации (активен с Этапа 1, счётчик = 0)
                'core.context_processors.unread_notifications_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# === БАЗА ДАННЫХ (SQLite) ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# === ВАЛИДАЦИЯ ПАРОЛЕЙ ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === ЛОКАЛИЗАЦИЯ ===
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# === СТАТИЧЕСКИЕ ФАЙЛЫ ===
STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'  # нужен при деплое

# === ПЕРВИЧНЫЙ КЛЮЧ ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === АУТЕНТИФИКАЦИЯ — редиректы ===
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# === MESSAGES — маппинг на Bootstrap CSS-классы ===
# Bootstrap использует 'danger' вместо 'error'
MESSAGE_TAGS = {
    messages_constants.DEBUG: 'secondary',
    messages_constants.INFO: 'info',
    messages_constants.SUCCESS: 'success',
    messages_constants.WARNING: 'warning',
    messages_constants.ERROR: 'danger',
}
