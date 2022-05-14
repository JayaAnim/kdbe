from kbde.kbde_cli import command
from kbde.shell import mixins as shell_mixins

import json


class Command(shell_mixins.RunCommand, command.Command):
    config_key_blacklist = [
        "DATABASE_URL",
        "REDIS_URL",
        "GIT_REV",
        "DOKKU_APP_RESTORE",
        "DOKKU_APP_TYPE",
        "DOKKU_DOCKERFILE_CMD",
        "DOKKU_PROXY_PORT",
        "DOKKU_PROXY_PORT_MAP",
        "DOKKU_PROXY_SSL_PORT",
    ]
    
    def add_arguments(self, parser):
        parser.add_argument(
            "source_app",
            type=str,
            help="The source app's name",
        )
        parser.add_argument(
            "--source-host",
            type=str,
            help=(
                "The hostname of the system from which the app will be "
                "copied. Default is 'localhost'."
            ),
            default="localhost",
        )
        parser.add_argument(
            "--destination-app",
            type=str,
            help=(
                "The destination app name. Default is the same as "
                "'source_app'"
            ),
        )
        parser.add_argument(
            "--destination-host",
            type=str,
            help=(
                "The hostname of the system to which the app will be "
                "copied. Default is 'localhost'."
            ),
            default="localhost",
        )

    def handle(self, source_host,
                     source_app,
                     destination_host,
                     destination_app):

        if not destination_app:
            destination_app = source_app

        # Clone the app from the source
        source_git_remote = f"dokku@{source_host}:{source_app}"
        self.run_command(
            f"git clone {source_git_remote}"
        )

        # Set up the destination as a remote
        destination_git_remote = f"dokku@{destination_host}:{destination_app}"
        self.run_command(
            f"cd {source_app} && "
            f"git remote add destination {destination_git_remote}"
        )

        # Export the old config
        config_json = self.run_command(
            f"DOKKU_HOST={source_host} "
            f"dokku_client.sh config:export --format=json {source_app}"
        )
        config = json.loads(config_json)

        # Set the config on the destination host
        config_values = [
            f"{key}='{value}'" for key, value in config.items()
            if key not in self.config_key_blacklist
        ]
        config_values_str = " ".join(config_values)

        # Create the app on the destination host
        self.run_command(
            f"cd {source_app} && "
            f"DOKKU_HOST={destination_host} "
            f"dokku_client.sh apps:create {destination_app}"
        )

        self.run_command(
            f"DOKKU_HOST={destination_host} "
            f"dokku_client.sh config:set {destination_app} {config_values_str}"
        )

        # Link the database
        try:
            self.run_command(
                f"DOKKU_HOST={destination_host} "
                f"dokku_client.sh postgres:link {destination_app} {destination_app}"
            )
        except self.CommandException:
            pass

        # Link redis
        try:
            self.run_command(
                f"DOKKU_HOST={destination_host} "
                f"dokku_client.sh redis:link {destination_app} {destination_app}"
            )
        except self.CommandException:
            pass

        # Push the source to the new host
        result = self.run_command(
            f"cd {source_app} && "
            f"git push destination"
        )
        self.stdout.write(result)

        # Remove the git repo
        self.run_command(
            f"rm {source_app} -rf"
        )
