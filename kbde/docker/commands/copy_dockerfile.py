from kbde.kbde_cli import command
from kbde import constants

import os, shutil


class Command(command.Command):
    
    def handle(self):
        dockerfile_path = os.path.join(
            constants.BASE_DIR,
            "docker",
            "Dockerfile",
        )
        destination_path = os.path.join(
            ".",
            "Dockerfile",
        )
        
        shutil.copyfile(dockerfile_path, destination_path)
