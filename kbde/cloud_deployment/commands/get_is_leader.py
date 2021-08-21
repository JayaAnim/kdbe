from kbde.kbde_cli import command

from kbde.cloud_deployment.leader import gcp


class Command(command.Command):

    def handle(self, **options):
        
        results = [
            gcp.GcpLeader().get_is_leader(),
        ]

        if any(results):
            print("yes")
        else:
            print("no")
