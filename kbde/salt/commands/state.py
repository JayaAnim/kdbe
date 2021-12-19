from kbde.kbde_cli import command
from kbde.shell import mixins as shell_mixins
from kbde import constants

import os


class Command(shell_mixins.RunCommand, command.Command):
    
    def add_arguments(self, parser):
        parser.add_argument(
            "state_name",
            help="The name of the state to apply",
        )

    def handle(self, state_name):
        file_root = os.path.join(constants.BASE_DIR, "salt", "srv")
        command = (
            f"salt-call --local "
            f"--file-root {file_root} "
            f"state.apply {state_name}"
        )
        return self.run_command(command)
