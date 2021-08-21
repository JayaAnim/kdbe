import sys


class OutputWrapper:

    def write(self, message):
        sys.stdout.write(f"{message}\n")


class Command:
    """
    A base command to be picked up by kbde_cli
    """

    def __init__(self):
        self.stdout = OutputWrapper()

    def add_arguments(self, parser):
        """
        Adds commands to the parser
        """
        return None

    def handle(self, **options):
        """
        Execute this command
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement `.handle(self, **options)`")
