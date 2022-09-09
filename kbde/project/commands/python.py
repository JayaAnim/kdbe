from kbde.kbde_cli import command
from kbde.shell import mixins as shell_mixins


class Command(shell_mixins.RunCommand, command.Command):

    def add_arguments(self, parser):
        parser.add_argument("args", type=str)
    
    def handle(self, args):
        python_version = self.get_python_version()

        command = f"{python_version} {args}"

        return self.run_command(command)

    def get_python_version(self):
        with open("python.txt") as f:
            return f.read().strip()
