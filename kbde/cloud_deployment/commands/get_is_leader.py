from kbde.kbde_cli import command


class Command(command.Command):

    def handle(self, **options):
        from kbde.cloud_deployment.leader import gcp
        
        results = [
            gcp.GcpLeader().get_is_leader(),
        ]

        if any(results):
            print("yes")
        else:
            print("no")
