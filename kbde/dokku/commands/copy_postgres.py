from kbde.kbde_cli import command
from kbde.shell import mixins as shell_mixins


class Command(shell_mixins.RunCommand, command.Command):
    
    def add_arguments(self, parser):
        parser.add_argument(
            "source_db",
            type=str,
            help="The source database's name",
        )
        parser.add_argument(
            "--source-host",
            type=str,
            help=(
                "The hostname of the system from which the database will be "
                "copied. Default is 'localhost'."
            ),
            default="localhost",
        )
        parser.add_argument(
            "--destination-db",
            type=str,
            help=(
                "The destination database's name. Default is the same as "
                "'source_db'"
            ),
        )
        parser.add_argument(
            "--destination-host",
            type=str,
            help=(
                "The hostname of the system to which the database will be "
                "copied. Default is 'localhost'."
            ),
            default="localhost",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help=(
                "When set, overwrite the contents of the destination_db with "
                "the contents of the source_db"
            ),
        )

    def handle(self, source_host,
                     source_db,
                     destination_host,
                     destination_db,
                     overwrite):

        if not destination_db:
            destination_db = source_db

        # See if there is a database with the destination_db
        try:
            self.run_command(
                f"DOKKU_HOST={destination_host} dokku_client.sh "
                f"postgres:list "
                f"| grep {destination_db}"
            )

            assert overwrite, (
                f"The destination_db '{destination_db}' already exists. "
                f"Cannot copy data to it without the --overwrite flag."
            )
        except self.CommandException as e:
            # The database was not found
            # Create it
            result = self.run_command(
                f"DOKKU_HOST={destination_host} dokku_client.sh "
                f"postgres:create {destination_db}"
            )
            self.stdout.write(result)

        # Take a dump of the source
        self.run_command(
            f"DOKKU_HOST={source_host} dokku_client.sh "
            f"postgres:export {source_db} > {source_db}.dump"
        )

        # Load the dump into the destination
        self.run_command(
            f"cat {source_db}.dump | "
            f"DOKKU_HOST={destination_host} dokku_client.sh "
            f"postgres:import {destination_db}"
        )

        # Remove the dump file
        self.run_command(
            f"rm {source_db}.dump"
        )
