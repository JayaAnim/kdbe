from kbde.kbde_cli import command
from kbde.s3 import client


class Command(command.Command):
    
    def add_arguments(self, parser):
        parser.add_argument("source_path", type=str)
        parser.add_argument("destination_path", type=str)

        parser.add_argument("--source-bucket-name", type=str)
        parser.add_argument("--source-aws-access-key-id", type=str)
        parser.add_argument("--source-aws-secret-access-key", type=str)
        parser.add_argument("--source-endpoint-url", type=str)

        parser.add_argument("--destination-bucket-name", type=str)
        parser.add_argument("--destination-aws-access-key-id", type=str)
        parser.add_argument("--destination-aws-secret-access-key", type=str)
        parser.add_argument("--destination-endpoint-url", type=str)

        parser.add_argument("--acl", type=str)
        parser.add_argument("--thread-count", type=int, default=1)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self,
               source_path,
               destination_path,
               source_bucket_name,
               source_aws_access_key_id,
               source_aws_secret_access_key,
               source_endpoint_url,
               destination_bucket_name,
               destination_aws_access_key_id,
               destination_aws_secret_access_key,
               destination_endpoint_url,
               acl,
               thread_count,
               dry_run):

        s3_client = client.Client(
            bucket_name=source_bucket_name,
            aws_access_key_id=source_aws_access_key_id,
            aws_secret_access_key=source_aws_secret_access_key,
            endpoint_url=source_endpoint_url,
            thread_count=thread_count,
        )

        dest_client_config = {
            "aws_access_key_id": destination_aws_access_key_id,
            "aws_secret_access_key": destination_aws_secret_access_key,
            "endpoint_url": destination_endpoint_url,
        }
        dest_client_config = {
            key: value for key, value in dest_client_config.items() if value
        }

        upload_extra_args = {
            "ACL": acl
        }
        upload_extra_args = {
            key: value for key, value in upload_extra_args.items() if value
        }

        s3_client.copy_recursive(
            source_path,
            destination_path,
            dest_bucket=destination_bucket_name,
            dest_client_config=dest_client_config,
            dry_run=dry_run,
            **upload_extra_args,
        )
