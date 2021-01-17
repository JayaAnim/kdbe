from kbde.kbde_cli import command
from kbde.shell import mixins as shell_mixins


class Command(shell_mixins.RunCommand, command.Command):

    def handle(self, **options):
        return self.run_command("python manage.py migrate")
