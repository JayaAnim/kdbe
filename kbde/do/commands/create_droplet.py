from . import command_base

from kbde.do.v2 import droplets


class Command(command_base.PostCommand):

    api_client_class = droplets.DropletList
    list_arguments = [
        "ssh_keys",
        "tags",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "name",
            help="The human-readable string you wish to use when displaying the Droplet name. The name, if set to a domain name managed in the DigitalOcean DNS management system, will configure a PTR record for the Droplet. The name set during creation will also determine the hostname for the Droplet in its internal configuration.",
        )
        parser.add_argument(
            "region",
            help="The slug identifier for the region that you wish to deploy the Droplet in.",
        )
        parser.add_argument(
            "size",
            help="The slug identifier for the size that you wish to select for this Droplet.",
        )
        parser.add_argument(
            "image",
            help="The image ID of a public or private image or the slug identifier for a public image. This image will be the base image for your Droplet.",
        )
        parser.add_argument(
            "--ssh-keys",
            help="An array containing the IDs or fingerprints of the SSH keys that you wish to embed in the Droplet's root account upon creation.",
        )
        parser.add_argument(
            "--backups",
            help="A boolean indicating whether automated backups should be enabled for the Droplet.",
            action="store_true",
        )
        parser.add_argument(
            "--ipv6",
            help="A boolean indicating whether to enable IPv6 on the Droplet.",
        )
        parser.add_argument(
            "--monitoring",
            help="A boolean indicating whether to install the DigitalOcean agent for monitoring.",
        )
        parser.add_argument(
            "--tags",
            help="A flat array of tag names as strings to apply to the Droplet after it is created. Tag names can either be existing or new tags.",
        )
        parser.add_argument(
            "--user-data",
            help="A string containing 'user data' which may be used to configure the Droplet on first boot, often a 'cloud-config' file or Bash script. It must be plain text and may not exceed 64 KiB in size.",
        )
        parser.add_argument(
            "--vpc-uuid",
            help="A string specifying the UUID of the VPC to which the Droplet will be assigned. If excluded, the Droplet will be assigned to your account's default VPC for the region.",
        )
