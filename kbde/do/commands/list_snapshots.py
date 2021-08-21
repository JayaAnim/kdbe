from . import command_base

from kbde.do.v2 import snapshots


class Command(command_base.GetCommand):

    api_client_class = snapshots.SnapshotList

    def add_arguments(self, parser):
        parser.add_argument(
            "--resource-type",
            help="Enum: \"droplet\" \"volume\". Used to filter snapshots by a resource type.",
        )
