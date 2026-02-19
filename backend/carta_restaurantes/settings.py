from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Variables de entorno
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-clave')

DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'adminsortable2',
    'carta_restaurantes',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'carta_restaurantes.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'carta_restaurantes.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# Directorio donde se recopilarán los archivos estáticos para producción
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Directorios adicionales de archivos estáticos (si los tienes)
STATICFILES_DIRS = [
    # BASE_DIR / 'static',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración para producción
if not DEBUG:
    ALLOWED_HOSTS = ['*']  # Configura esto con tus dominios específicos
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

CORS_ALLOW_ALL_ORIGINS = True

# CSRF Configuration for Railway
CSRF_TRUSTED_ORIGINS = [
    'https://cartas-para-negocios-production.up.railway.app',
    'http://cartas-para-negocios-production.up.railway.app',
    'https://*.railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# También asegurar que las cookies CSRF funcionen correctamente
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False  # Permitir acceso desde JavaScript
CSRF_COOKIE_SAMESITE = 'Lax'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'