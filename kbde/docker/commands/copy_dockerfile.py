from kbde.kbde_cli import command

from kbde.docker import dockerfile

from os import path


class Command(command.Command):
    
    def handle(self):
        df = dockerfile.Dockerfile()
        df.render_to_file(
            path.join(".", "Dockerfile")
        )
