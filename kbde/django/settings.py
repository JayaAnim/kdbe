from config.settings_base import *
import os


config = globals()


#App name

APP_NAME = os.getenv("APP_NAME")
assert APP_NAME, "must define APP_NAME environement variable"


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

AWS_ACCESS_KEY_ID = config.get("AWS_ACCESS_KEY_ID", os.getenv("AWS_ACCESS_KEY_ID"))
AWS_SECRET_ACCESS_KEY = config.get("AWS_SECRET_ACCESS_KEY", os.getenv("AWS_SECRET_ACCESS_KEY"))
AWS_STORAGE_BUCKET_NAME = config.get("AWS_STORAGE_BUCKET_NAME", APP_NAME)
AWS_S3_ENDPOINT_URL = config.get("AWS_S3_ENDPOINT_URL", os.getenv("AWS_S3_ENDPOINT_URL"))
AWS_QUERYSTRING_AUTH = config.get("AWS_QUERYSTRING_AUTH", False)

try:
    import storages

    INSTALLED_APPS += [
        "storages",
        ]

    DEFAULT_FILE_STORAGE = config.get("DEFAULT_FILE_STORAGE",
                                      "kbde.django.storage_backends.MediaStorage")
    MEDIA_URL = config.get("MEDIA_URL", "{}/{}/".format(AWS_S3_ENDPOINT_URL, "media"))

except ImportError:
    pass


#Debug

DEBUG = os.getenv("DEBUG", "0")
try:
    DEBUG = bool(int(DEBUG))
except ValueError:
    raise Exception("DEBUG must be an int")

TEMPLATE_DEBUG = DEBUG


#Email

EMAIL_HOST = config.get("EMAIL_HOST", os.getenv("EMAIL_HOST", "smtp.sendgrid.net"))
EMAIL_PORT = config.get("EMAIL_PORT", os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = config.get("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = config.get("EMAIL_HOST_USER", os.getenv("EMAIL_USERNAME", "apikey"))
EMAIL_HOST_PASSWORD = config.get("EMAIL_HOST_PASSWORD", os.getenv("EMAIL_PASSWORD"))
SERVER_EMAIL = config.get("SERVER_EMAIL",
                          os.getenv("SERVER_EMAIL", "{}@kbuilds.com".format(APP_NAME)))


#Staticfiles config

STATIC_URL = config.get("STATIC_URL", '/static/')
STATIC_ROOT = config.get("STATIC_ROOT", os.path.join(BASE_DIR, 'staticfiles'))
