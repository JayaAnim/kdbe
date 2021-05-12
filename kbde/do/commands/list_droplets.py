from . import command_base

from kbde.do.v2 import droplets


class Command(command_base.GetCommand):
    
    api_client_class = droplets.DropletList

    def add_arguments(self, parser):
        parser.add_argument(
            "--tag-name",
            help="Used to filter Droplets by a specific tag.",
        )
