from kbde.kbde_cli import command
from kbde.shell import mixins as shell_mixins

import os


class Command(shell_mixins.RunCommand, command.Command):
    
    def handle(self):
        # Install bash completion
        apt_output = self.run_command("apt-get install -y bash-completion")

        # Install argcomplete
        pip_output = self.run_command("pip install argcomplete")
        
        # Activate argcomplete
        activate_output = self.run_command(
            "activate-global-python-argcomplete"
        )

        # Fix bashrc for root
        with open("/root/.bashrc", "a") as f:
            f.write(
                "\n\n"
                "if [ -f /etc/bash_completion ] && ! shopt -oq posix; then\n"
                "    . /etc/bash_completion\n"
                "fi\n"
            )

        return "\n\n".join([
            apt_output,
            pip_output,
            activate_output,
        ])
