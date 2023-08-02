import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_KEY', get_random_secret_key())

DEBUG = os.getenv('DEBUG', True)

hosts_allow = os.getenv('ALLOWED_HOSTS')
if hosts_allow:
    ALLOWED_HOSTS = hosts_allow.split(',')
else:
    ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'adminlte3',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'api.apps.ApiConfig',
    'products.apps.ProductsConfig'
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

ROOT_URLCONF = 'OzonParseApp.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'OzonParseApp.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE', 'mysql'),
        'USER': 'root',
        'PASSWORD': os.getenv('MYSQL_ROOT_PASSWORD', ''),
        'HOST': os.getenv('MYSQL_URL', 'db'),
        'PORT': os.getenv('MYSQL_PORT', 3306),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_URL = os.getenv('REDIS_URL', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
CELERY_BROKER_URL = f'redis://{REDIS_URL}:{REDIS_PORT}'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
