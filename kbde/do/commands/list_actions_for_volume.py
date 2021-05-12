from . import command_base

from kbde.do.v2 import block_storage_actions


class Command(command_base.GetCommand):
    
    api_client_class = block_storage_actions.VolumeActionList

    def add_arguments(self, parser):
        parser.add_argument("volume_id")
