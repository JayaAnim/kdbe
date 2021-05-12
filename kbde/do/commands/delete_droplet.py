from . import command_base

from kbde.do.v2 import droplets


class Command(command_base.DeleteCommand):

    api_client_class = droplets.DropletDetail

    def add_arguments(self, parser):
        parser.add_argument(
            "droplet_id",
            help="A unique identifier for a Droplet instance.",
        )

