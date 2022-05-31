from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

import posixpath


class MediaStorage(S3Boto3Storage):
    location = f"{settings.APP_NAME}/media"
    file_overwrite = False

    def get_all_keys(self, name):
        """
        Returns the keys of all objects which fall under the `name` given
        """

        path = self._normalize_name(self._clean_name(name))

        # The path needs to end with a slash, but if the root is empty, leave it.
        if path and not path.endswith('/'):
            path += '/'

        paginator = self.connection.meta.client.get_paginator('list_objects')
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=path)

        for page in pages:

            for entry in page.get('Contents', ()):
                key = entry['Key']

                if key != path:
                    yield posixpath.relpath(key, path)
