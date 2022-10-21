"""
Django settings for valentina project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import django
from valentina.settings_conf import *
from django.db import models
from valentina.version import APP_VERSION

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_ROOT = os.path.join(BASE_DIR, 'output/')

LOGIN_REDIRECT_URL = 'validation'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

ENV_FILE_URL_TEMPLATE = "https://github.com/awst-austria/qa4sm/blob/v{}/environment/qa4sm_env.yml"

ORICD_REGEX = "^([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9Xx]{3}[0-9Xx])$"

# Expected ping frequency in minutes. !Do not change this unless you fully understand the code that use this property!
UPTIME_PING_INTERVAL = 5
USER_DATA_DIR = USER_DATA_DIR

# Default primary key field type can be set here, but only if they solve 'Migrating auto-created through tables' issue
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Application definition
INSTALLED_APPS = [
    'api.apps.ApiConfig',
    'validator.apps.ValidatorConfig',
    'drf_yasg',
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'django_rest_passwordreset'

]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # make all views private
    ),
    'EXCEPTION_HANDLER': 'api.api_exception_handler.custom_exception_handler'
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
}

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'valentina.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # include default django templates and widgets, see https://docs.djangoproject.com/en/2.1/ref/forms/renderers/#templatessetting
        'DIRS': [django.__path__[0] + '/forms/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'validator.context_processors.globals_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'valentina.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DB_HOST = os.getenv('QA4SM_DB_HOST')
DB_ENV_PASSWORD = os.getenv('QA4SM_DB_PASSWORD')
if DB_ENV_PASSWORD is not None:
    DB_PASSWORD=DB_ENV_PASSWORD

if DB_HOST is None:
    DB_HOST='localhost'

if DBSM == "postgresql":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'valentina',
            'USER': 'django',
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': '',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

AUTH_USER_MODEL = 'validator.User'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

FORMAT_MODULE_PATH = [
    'validator.formats',
]

# Logging, see https://docs.djangoproject.com/en/2.1/topics/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {module}:{funcName}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_FILE,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'validator': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        #         'py.warnings': {
        #             'handlers': ['file', 'console'],
        #             'level': 'DEBUG',
        #             'propagate': True,
        #         },
    },
}

## Security settings

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
try:
    CSRF_COOKIE_SECURE = not DEBUG
except NameError:
    CSRF_COOKIE_SECURE = True
# print("Running with CSRF_COOKIE_SECURE = {}".format(CSRF_COOKIE_SECURE))

PASSWORD_RESET_TIMEOUT_DAYS = 1

VALIDATION_EXPIRY_DAYS = 60
VALIDATION_EXPIRY_WARNING_DAYS = 7
