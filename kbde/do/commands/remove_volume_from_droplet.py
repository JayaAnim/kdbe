from . import command_base

from kbde.do.v2 import block_storage_actions


class Command(command_base.PostCommand):
    
    api_client_class = block_storage_actions.VolumeActionList

    def add_arguments(self, parser):
        parser.add_argument("droplet_id")
        parser.add_argument("volume_id")
        parser.add_argument(
            "--region",
            help="The slug identifier for the region the volume is located in."
        )

    def handle(self, **options):
        options["type"] = "detach"
        return super().handle(**options)
