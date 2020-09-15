from kbde.shell import mixins as shell_mixins


class Installer(shell_mixins.RunCommand):
    
    package_names = []

    def __init__(self):
        assert self.package_names, f"{self.__class__.__name__} must define one or more .package_names"

    def run(self):
        package_names = " ".join(self.package_names)
        command = f"apt-get install -y {package_names}"
        return self.run_command(command)
