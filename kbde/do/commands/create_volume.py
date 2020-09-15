from . import command_base

from kbde.do.v2 import block_storage


class Command(command_base.PostCommand):
    
    api_client_class = block_storage.Volume

    def add_arguments(self, parser):
        parser.add_argument(
            "size_gigabytes",
            type=int,
            help="The size of the block storage volume in GiB (1024^3)"
        )
        parser.add_argument(
            "name",
            help=("A human-readable name for the block storage volume. Must be lowercase and be "
                  'composed only of numbers, letters and "-", up to a limit of 64 characters.'),
        )
        parser.add_argument(
            "--description",
            help="An optional free-form text field to describe a block storage volume",
        )
        parser.add_argument(
            "region",
            help=("The region where the block storage volume will be created. When setting a "
                  "region, the value should be the slug identifier for the region. When you query "
                  "a block storage volume, the entire region object will be returned."),
        )
        parser.add_argument(
            "--snapshot-id",
            help=("The unique identifier for the volume snapshot from which to create the volume. "
                  "Should not be specified with a region_id."),
        )
        parser.add_argument(
            "--filesystem-type",
            help=("The name of the filesystem type to be used on the volume. When provided, the "
                  "volume will automatically be formatted to the specified filesystem type. "
                  'Currently, the available options are "ext4" and "xfs". Pre-formatted volumes '
                  "are automatically mounted when attached to Ubuntu, Debian, Fedora, Fedora "
                  "Atomic, and CentOS Droplets created on or after April 26, 2018. Attaching "
                  "pre-formatted volumes to other Droplets is not recommended."),
        )
        parser.add_argument(
            "--filesystem-label",
            help=("The label to be applied to the filesystem. Labels for ext4 type filesystems "
                  "may contain 16 characters while lables for xfs type filesystems are limited to "
                  "12 characters. May only be used in conjunction with filesystem_type."),
        )
        parser.add_argument(
            "--tags",
            help=("A flat array of tag names as comma-delimited strings to apply to the Volume "
                  "after it is created. Tag names can either be existing or new tags."),
        )

    def handle(self, **options):
        if options["tags"]:
            options["tags"] = [opt.strip() for opt in options["tags"].split(",")]

        return super().handle(**options)
