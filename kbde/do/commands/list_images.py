from . import command_base

from kbde.do.v2 import images


class Command(command_base.GetCommand):

    api_client_class = images.ImageList

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            help="Filters results based on image type which can be either \"application\" or \"distribution\"",
        )
        parser.add_argument(
            "--private",
            help="Used to filter only user images.",
        )
        parser.add_argument(
            "--tag-name",
            help="Used to filter images by a specific tag.",
        )
