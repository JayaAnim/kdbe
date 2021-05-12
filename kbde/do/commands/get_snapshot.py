from . import command_base

from kbde.do.v2 import snapshots


class Command(command_base.GetCommand):
    
    api_client_class = snapshots.SnapshotDetail

    def add_arguments(self, parser):
        parser.add_argument(
            "snapshot_id",
            help="Either the ID of an existing snapshot. This will be an integer for a Droplet snapshot or a string for a volume snapshot.",
        )
