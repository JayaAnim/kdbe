from kbde.kbde_cli import command


class Command(command.Command):
    
    def add_arguments(self, parser):
        parser.add_argument("host", type=str)
        parser.add_argument("path", type=str)

    def handle(self, **options):
        from .. import client

        # Define a new client class
        class Client(client.Client):
            host = options["host"]
            path = options["path"]

        return Client().get()
