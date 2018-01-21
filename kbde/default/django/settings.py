from config.settings import *

try:
    import whitenoise
except ImportError:
    raise Exception("must install whitenoise")

try:
    import dj_database_url
except ImportError:
    raise Exception("must install dj_database_url")

try:
    import storages
except ImportError:
    raise Exception("must install django-storages")

import os


#App name

APP_NAME = os.getenv("APP_NAME")

if APP_NAME is None:
    raise Exception("must define APP_NAME environement variable")


#Debug

SETTINGS_PROD = os.getenv("SETTINGS_PROD")
if SETTINGS_PROD:
    DEBUG = False
    TEMPLATE_DEBUG = DEBUG


#Email

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = "587"
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_USERNAME")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
SERVER_EMAIL = "{0}_system@kbuilds.com".format(APP_NAME)
ADMINS = [("Kurtis Jensen","k@kbuilds.com"),]


#Whitenoise used for serving static files

INSTALLED_APPS += [
    "whitenoise.runserver_nostatic",
    "storages",
    ]
MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    ]


#Databases set up

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)


#Media and staticfiles storage

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

AWS_ACCESS_KEY_ID = os.getenv("AWS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET")
AWS_STORAGE_BUCKET_NAME = APP_NAME
AWS_S3_ENDPOINT_URL = os.getenv("AWS_BUCKET_URL")
AWS_QUERYSTRING_AUTH = False
DEFAULT_FILE_STORAGE = 'kbde.default.django.storage_backends.MediaStorage'
MEDIA_URL = "{0}/{1}/".format(AWS_S3_ENDPOINT_URL,"media")
