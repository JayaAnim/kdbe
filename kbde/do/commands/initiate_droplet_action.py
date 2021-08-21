from . import command_base

from kbde.do.v2 import droplet_actions


class Command(command_base.PostCommand):
    
    api_client_class = droplet_actions.DropletActionList

    def add_arguments(self, parser):
        parser.add_argument(
            "droplet_id",
            help="A unique identifier for a Droplet instance.",
        )
        parser.add_argument(
            "type",
            help="The type of action to initiate for the Droplet.",
        )
