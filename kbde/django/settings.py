from django import urls

from config.settings_base import *

import os


# App name

APP_NAME = os.getenv("APP_NAME")
assert APP_NAME, "must define APP_NAME environement variable"


# KBDE Timezone

MIDDLEWARE += [
    "kbde.django.middleware.TimezoneMiddleware",
    ]


# Whitenoise config

try:
    import whitenoise

    INSTALLED_APPS += [
        "whitenoise.runserver_nostatic",
        ]

    MIDDLEWARE += [
        "whitenoise.middleware.WhiteNoiseMiddleware",
        ]

except ImportError:
    pass


# Database url config

try:
    import dj_database_url

    db_from_env = dj_database_url.config()
    DATABASES['default'].update(db_from_env)

except ImportError:
    pass


# Auth

AUTH_USER_MODEL = "user.User"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Media storage config

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = APP_NAME
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_QUERYSTRING_AUTH = False

try:
    import storages

    INSTALLED_APPS += [
        "storages",
        ]

    DEFAULT_FILE_STORAGE = "kbde.django.storage_backends.MediaStorage"
    MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/media/"

except ImportError:
    pass


# Debug

DEBUG = bool(os.getenv("DEBUG"))

TEMPLATE_DEBUG = DEBUG

DEBUG_EMAIL = os.getenv("DEBUG_EMAIL")


# Logging

APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
            },
        },
    "formatters": {
        "verbose": {
            "format": ("[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s"),
            "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            },
        },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": APP_LOG_LEVEL,
            },
        },
    }


# Email

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.sendgrid.net")
EMAIL_PORT = os.getenv("EMAIL_PORT", "587")
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_USERNAME", "apikey")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SUBJECT_PREFIX = f"[{APP_NAME}] "


# Staticfiles config

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# SSL

SECURE_PROXY_SSL_HEADER = os.getenv("SECURE_PROXY_SSL_HEADER")
if SECURE_PROXY_SSL_HEADER is not None:
    SECURE_PROXY_SSL_HEADER = SECURE_PROXY_SSL_HEADER.split(":")

if SECURE_PROXY_SSL_HEADER:
    SECURE_SSL_REDIRECT = True
