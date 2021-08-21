from . import command_base

from kbde.do.v2 import block_storage


class Command(command_base.DeleteCommand):

    api_client_class = block_storage.VolumeDetail

    def add_arguments(self, parser):
        parser.add_argument(
            "volume_id",
        )
