import boto3, botocore, tempfile, os, posixpath, multiprocessing, sys, mimetypes


class Client:

    def __init__(self,
                 bucket_name=None,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 endpoint_url=None,
                 thread_count=1):
        self.bucket_name = bucket_name or os.getenv("AWS_STORAGE_BUCKET_NAME")
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url or os.getenv("AWS_S3_ENDPOINT_URL")
        self.thread_count = thread_count

        assert self.bucket_name, (
            f"S3 client requires that a `bucket_name` param is given or that "
            f"an `AWS_STORAGE_BUCKET_NAME` env var is set"
        )
        assert self.endpoint_url, (
            f"S3 client requires that an `endpoint_url` param is given, or "
            f"that an `AWS_S3_ENDPOINT_URL` env var is set"
        )

    def copy_recursive(self,
                       src_prefix,
                       dest_prefix,
                       dest_bucket=None,
                       dest_client_config=None,
                       dry_run=True,
                       overwrite=False,
                       **upload_extra_args):
        
        dest_bucket = dest_bucket or self.bucket_name

        src_client_config = self.get_client_config()

        if not dest_client_config:
            dest_client_config = src_client_config

        keys = self.get_source_keys(src_prefix)

        copy_arg_list = self.map_copy_args(
            src_client_config,
            self.bucket_name,
            src_prefix,
            dest_client_config,
            dest_bucket,
            dest_prefix,
            upload_extra_args,
            dry_run,
            overwrite,
            keys,
        )

        with multiprocessing.Pool(self.thread_count) as pool:
            pool.starmap(self.copy_object, copy_arg_list)

    def get_source_keys(self, prefix):
        client = self.get_client()

        # The prefix needs to end with a slash, but if the root is empty,
        # leave it.
        if prefix and not prefix.endswith('/'):
            prefix += '/'

        paginator = client.get_paginator("list_objects")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

        for page in pages:
            
            for entry in page.get("Contents", ()):
                key = entry["Key"]

                if key != prefix:
                    yield posixpath.relpath(key, prefix)

    def map_copy_args(self,
                      src_client_config,
                      src_bucket,
                      src_prefix,
                      dest_client_config,
                      dest_bucket,
                      dest_prefix,
                      upload_extra_args,
                      dry_run,
                      overwrite,
                      keys):

        for key in keys:
            yield [
                src_client_config,
                src_bucket,
                os.path.join(src_prefix, key),
                dest_client_config,
                dest_bucket,
                os.path.join(dest_prefix, key),
                upload_extra_args,
                dry_run,
                overwrite,
            ]

    def copy_object(self,
                    src_client_config,
                    src_bucket,
                    src_key,
                    dest_client_config,
                    dest_bucket,
                    dest_key,
                    upload_extra_args,
                    dry_run=True,
                    overwrite=False):
        src_client = self.get_client(**src_client_config)
        dest_client = self.get_client(**dest_client_config)

        mimetype, encoding = mimetypes.guess_type(dest_key)

        if mimetype:
            upload_extra_args["ContentType"] = mimetype
        
        if encoding:
            upload_extra_args["ContentEncoding"] = encoding

        if overwrite:
            needs_copy = True
        else:
            needs_copy = not self.check_key_exists(
                dest_client,
                dest_bucket,
                dest_key,
            )

        if not dry_run and needs_copy:

            with tempfile.TemporaryFile() as temp:
                # Download the src file
                src_client.download_fileobj(src_bucket, src_key, temp)

                temp.seek(0)

                # Upload the file to the dest
                dest_client.upload_fileobj(
                    temp,
                    dest_bucket,
                    dest_key,
                    ExtraArgs=upload_extra_args,
                )

        if needs_copy:
            sys.stdout.write(f"copied {src_bucket}:{src_key} to {dest_bucket}:{dest_key}\n")
        else:
            sys.stdout.write(f"skipped {src_bucket}:{src_key} to {dest_bucket}:{dest_key}\n")

    def check_key_exists(self, client, bucket, key):
        try:
            client.head_object(Bucket=bucket, Key=key)
            return True

        except botocore.exceptions.ClientError as e:

            if e.response['Error']['Code'] == "404":
                return False

            raise

    def get_client(self, **kwargs):
        config = self.get_client_config(**kwargs)

        return boto3.client("s3", **config)

    def get_client_config(self, **kwargs):
        config = {
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
            "endpoint_url": self.endpoint_url,
        }
        
        config.update(kwargs)

        return config
