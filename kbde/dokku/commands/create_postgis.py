from kbde.kbde_cli import command
from kbde.shell import mixins as shell_mixins


class Command(shell_mixins.RunCommand, command.Command):
    
    def add_arguments(self, parser):
        parser.add_argument(
            "db_name",
            type=str,
            help="The database's name",
        )
        parser.add_argument(
            "--host",
            type=str,
            help=(
                "The hostname of the system from which the database will be "
                "created. Default is 'localhost'."
            ),
            default="localhost",
        )
        parser.add_argument(
            "--postgis-image",
            type=str,
            help="The name of the postgis image to be installed.",
            default="postgis/postgis",
        )
        parser.add_argument(
            "--postgis-version",
            type=str,
            help="The version of the posgis image to be installed.",
            default="13-3.1",
        )

    def handle(self, db_name,
                     host,
                     postgis_image,
                     postgis_version):
        # SSH to the host, and execute the create postgres command
        # Export the image and version into the shell on the remote host
        create_postgres_command = f"dokku postgres:create {db_name}"
        export_env_vars = (
            f"POSTGRES_IMAGE={postgis_image} "
            f"POSTGRES_IMAGE_VERSION={postgis_version} "
            f"{create_postgres_command}"
        )
        dokku_user_command = f"sudo -u dokku '{export_env_vars}'"
        ssh_command = f"ssh {host} '{dokku_user_command}'"

        result = self.run_command(ssh_command)

        self.stdout.write(result)
