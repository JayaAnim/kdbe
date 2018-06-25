from config.settings import *
import os


#App name

APP_NAME = os.getenv("APP_NAME")
if APP_NAME is None:
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

    INSTALLED_APPS += [
        "storages",
        ]

    db_from_env = dj_database_url.config()
    DATABASES['default'].update(db_from_env)

except ImportError:
    pass


# Media storage config

try:
    import storages

    AWS_ACCESS_KEY_ID = os.getenv("AWS_KEY")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET")
    AWS_STORAGE_BUCKET_NAME = APP_NAME
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_BUCKET_URL")
    AWS_QUERYSTRING_AUTH = False
    DEFAULT_FILE_STORAGE = 'kbde.django.storage_backends.MediaStorage'
    MEDIA_URL = "{0}/{1}/".format(AWS_S3_ENDPOINT_URL,"media")

except ImportError:
    pass


#Debug

NO_DEBUG = os.getenv("NO_DEBUG")
if NO_DEBUG:
    DEBUG = False
    TEMPLATE_DEBUG = DEBUG


#Email

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = "587"
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_USERNAME")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
SERVER_EMAIL = "{0}@kbuilds.com".format(APP_NAME)
ADMINS = [("Kurtis Jensen","k@kbuilds.com"),]


#Staticfiles config

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
