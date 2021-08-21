from . import command_base

from kbde.do.v2 import block_storage


class Command(command_base.GetCommand):
    
    api_client_class = block_storage.VolumeList

    def add_arguments(self, parser):
        parser.add_argument(
            "--region",
            help=("The region that the block storage volume is located in. When setting a region, "
                  "the value should be the slug identifier for the region. When you query a block "
                  "storage volume, the entire region object will be returned."),
        )
        parser.add_argument(
            "--name",
            help=("A human-readable name for the block storage volume. Must be lowercase and be "
                  'composed only of numbers, letters and "-", up to a limit of 64 characters. The '
                  "name must begin with a letter."),
        )
