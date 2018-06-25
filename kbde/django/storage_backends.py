try:
    from storages.backends.s3boto3 import S3Boto3Storage
except ImportError:
    raise Exception("must install django-storages")


class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False
