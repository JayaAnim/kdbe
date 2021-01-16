

class Command:
    """
    A base command to be picked up by obde_cli
    """

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
