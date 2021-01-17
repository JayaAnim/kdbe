from kbde.kbde_cli import command

from kbde.install import (
    base,
    desktop,
    dev,
    dokku,
    python,
)


class Command(command.Command):

    module_list = [
        base,
        desktop,
        dev,
        dokku,
        python,
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "installer_name",
            help="The name of the installer module to run",
            choices=self.get_module_map().keys(),
        )

    def handle(self, **options):
        class_map = self.get_installer_class_map()

        module_name = options["installer_name"]

        assert module_name in class_map, f"no module `{module_name}` found"

        installer_class = class_map[module_name]

        return installer_class().run()

    def get_installer_class_map(self):
        module_map = self.get_module_map()

        return {name: getattr(mod, "Installer") for name, mod in module_map.items()}

    def get_module_map(self):
        return {mod.__name__.split(".")[-1]: mod for mod in self.module_list}
