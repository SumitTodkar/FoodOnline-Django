"""
Django settings for the FoodOnline project.

Sensitive values (secret key, debug flag, allowed hosts) are read from
environment variables. For local development you can copy ``.env.example`` to
``.env`` in the project root; it is loaded automatically below.
"""
import os
from decimal import Decimal
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------
# Environment helpers (tiny .env loader, so no extra dependency is needed)
# --------------------------------------------------------------------------
def _load_env_file(path):
    if not path.exists():
        return
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(BASE_DIR / '.env')


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


# --------------------------------------------------------------------------
# Core security settings
# --------------------------------------------------------------------------
DEBUG = env_bool('DJANGO_DEBUG', True)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        # Development-only fallback. Never used when DJANGO_DEBUG is false.
        SECRET_KEY = 'django-insecure-development-only-key-change-me'
    else:
        raise ImproperlyConfigured(
            'Set the DJANGO_SECRET_KEY environment variable when DJANGO_DEBUG is off.'
        )

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS')

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', True)
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS', '3600'))
    X_FRAME_OPTIONS = 'DENY'


# --------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Project apps
    'accounts',
    'menu',
    'cart',
    'orders',
    'core',
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

ROOT_URLCONF = 'FoodOnline.urls'

# Templates are looked up in <project>/templates first. The inner
# FoodOnline/templates folder is also searched when it exists, so templates you
# already had keep working.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            path for path in (BASE_DIR / 'templates', BASE_DIR / 'FoodOnline' / 'templates')
            if path.exists()
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',
                'core.context_processors.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'FoodOnline.wsgi.application'


# --------------------------------------------------------------------------
# Database (SQLite for development)
# --------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'


# --------------------------------------------------------------------------
# Internationalisation
# --------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# --------------------------------------------------------------------------
# Static and media files
# --------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    path for path in (BASE_DIR / 'static', BASE_DIR / 'FoodOnline' / 'static')
    if path.exists()
]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# --------------------------------------------------------------------------
# FoodOnline business settings
# --------------------------------------------------------------------------
SITE_NAME = os.environ.get('FOODONLINE_SITE_NAME', 'FoodOnline')
# Path (inside a static folder) of your logo image. Hidden automatically if missing.
SITE_LOGO = os.environ.get('FOODONLINE_LOGO', 'logo/logo.png')
CURRENCY_SYMBOL = '₹'

DELIVERY_CHARGE = Decimal(os.environ.get('FOODONLINE_DELIVERY_CHARGE', '40.00'))
FREE_DELIVERY_ABOVE = Decimal(os.environ.get('FOODONLINE_FREE_DELIVERY_ABOVE', '500.00'))

CART_SESSION_ID = 'cart'
CART_MAX_QUANTITY = 20
