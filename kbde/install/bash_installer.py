from kbde.shell import mixins as shell_mixins


class Installer(shell_mixins.RunCommand):

    commands = []

    def __init__(self):
        assert self.commands, f"{self.__class__.__name__} must define one or more .commands"

    def run(self):
        for command in commands:
            self.run_command(command)
