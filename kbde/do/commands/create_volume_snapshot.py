from . import command_base

from kbde.do.v2 import block_storage


class Command(command_base.PostCommand):
    
    api_client_class = block_storage.VolumeSnapshotList

    def add_arguments(self, parser):
        parser.add_argument("volume_id")
        parser.add_argument(
            "name",
            help="A human-readable name for the volume snapshot.",
        )
