from kbde.kbde_cli import command
from kbde.shell import mixins as shell_mixins


class Command(shell_mixins.RunCommand, command.Command):
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--size",
            type=str,
            help="The amount of swap to allocate. Default is 10G.",
            default="10G",
        )
        parser.add_argument(
            "--host",
            type=str,
            help=(
                "The hostname of the system from which the swap will be "
                "created. Default is 'localhost'."
            ),
            default="localhost",
        )

    def handle(self, host, size):
        # Allocate
        self.run_command(
            f"ssh {host} "
            f"'sudo fallocate -l {size} /swap.img'"
        )

        # Change permissions
        self.run_command(
            f"ssh {host} "
            "'sudo chmod 600 /swap.img'"
        )

        # Create swap
        self.run_command(
            f"ssh {host} "
            "'sudo mkswap /swap.img'"
        )

        # Enable swap
        self.run_command(
            f"ssh {host} "
            "'sudo swapon /swap.img'"
        )

        # Add to fstab
        self.run_command(
            f"ssh {host} "
            "'echo '/swap.img none swap sw 0 0' | sudo tee -a /etc/fstab'"
        )

        # Set swappiness
        self.run_command(
            f"ssh {host} "
            "'echo 'vm.swappiness=100' | sudo tee -a /etc/sysctl.conf'"
        )
