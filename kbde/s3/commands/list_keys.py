from kbde.kbde_cli import command


class Command(command.Command):
    
    def add_arguments(self, parser):
        parser.add_argument("--bucket-name", type=str)
        parser.add_argument("--path", type=str, default="")

        parser.add_argument("--aws-access-key-id", type=str)
        parser.add_argument("--aws-secret-access-key", type=str)
        parser.add_argument("--endpoint-url", type=str)

    def handle(self,
               bucket_name,
               path,
               aws_access_key_id,
               aws_secret_access_key,
               endpoint_url):
        from kbde.s3 import client

        s3_client = client.Client(
            bucket_name=bucket_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
        )

        for key in s3_client.get_source_keys(path):
            self.stdout.write(key)
