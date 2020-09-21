from kbde import kbde_cli
from kbde.shell import mixins as shell_mixins


class Command(shell_mixins.RunCommand, kbde_cli.Command):

    def handle(self, **options):
        
        return self.run_command("python manage.py migrate")
