from kbde.kbde_cli import command

from kbde.docker import dockerfile

from os import path


class Command(command.Command):
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--python-version",
            type=str,
            default="3.8",
        )
    
    def handle(self, python_version, **options):
        destination_path = path.join(
            ".",
            "Dockerfile",
        )
        df = dockerfile.Dockerfile(python_version=python_version)
        df.render_to_file(destination_path)
