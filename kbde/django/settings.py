from config.settings import *
import os


#App name

APP_NAME = os.getenv("APP_NAME")
if not APP_NAME:
    raise Exception("must define APP_NAME environement variable")


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


# Media storage config

try:
    import storages

    INSTALLED_APPS += [
        "storages",
        ]

    DEFAULT_FILE_STORAGE = 'kbde.django.storage_backends.MediaStorage'
    MEDIA_URL = "{}/{}/".format(AWS_S3_ENDPOINT_URL,"media")

except ImportError:
    pass

try:
    AWS_ACCESS_KEY_ID
except NameError:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_KEY")
try:
    AWS_SECRET_ACCESS_KEY
except NameError:
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET")
try:
    AWS_STORAGE_BUCKET_NAME = APP_NAME
except NameError:
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_BUCKET_URL")
try:
    AWS_QUERYSTRING_AUTH
except NameError:
    AWS_QUERYSTRING_AUTH = False


#Debug

NO_DEBUG = os.getenv("NO_DEBUG")
if NO_DEBUG:
    DEBUG = False
    TEMPLATE_DEBUG = DEBUG


#Email

try:
    EMAIL_HOST
except NameError:
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.sendgrid.net")
try:
    EMAIL_PORT
except NameError:
    EMAIL_PORT = os.getenv("EMAIL_PORT", "587")
try:
    EMAIL_USE_TLS
except NameError:
    EMAIL_USE_TLS = True
try:
    EMAIL_HOST_USER
except NameError:
    EMAIL_HOST_USER = os.getenv("EMAIL_USERNAME", "apikey")
try:
    EMAIL_HOST_PASSWORD
except NameError:
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
try:
    SERVER_EMAIL
except NameError:
    SERVER_EMAIL = os.getenv("SERVER_EMAIL", "{}@kbuilds.com".format(APP_NAME))


#Staticfiles config

try:
    STATIC_URL
except NameError:
    STATIC_URL = '/static/'
try:
    STATIC_ROOT
except NameError:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
