from kbde.kbde_cli import command
from .. import base, sudo, python


class Command(command.Command):
    state_classes = [
        sudo.SudoNoPassword,
        python.Python_3_6,
        python.Python_3_7,
        python.Python_3_8,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_class_map = {
            cls.__name__: cls for cls in self.state_classes
        }

    def add_arguments(self, parser):
        parser.add_argument(
            "class_name",
            type=str,
            choices=self.state_class_map.keys(),
        )

    def handle(self, class_name, **options):
        state_class = self.state_class_map[class_name]
        state = state_class(stdout=self.stdout)
        state.run()
