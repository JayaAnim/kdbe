from kbde import kbde_cli

from kbde.cloud_deployment.leader import gcp


class Command(kbde_cli.Command):

    def handle(self, **options):
        
        results = [
            gcp.GcpLeader().get_is_leader(),
        ]

        if any(results):
            print("yes")
        else:
            print("no")
