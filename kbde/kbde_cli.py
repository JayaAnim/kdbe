import kbde, argparse, pkgutil, importlib, inspect


class KbdeCli:
    """
    A cli application for kbde
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers()

        self.process_commands_modules()

    def run(self):
        self.parser.parse_args()
        print(self.parser)

    def process_commands_modules(self):
        commands_modules = self.get_commands_modules()

        for commands_module in commands_modules:
            self.process_commands_module(commands_module)
        
    def process_commands_module(self, commands_module):
        command_modules = self.get_command_modules_from_commands_module(commands_module)

        # Add subparser for this command
        module_name = commands_module.__name__.split(".")[1]
        module_parser = self.subparsers.add_parser(module_name)

        for command_module in command_modules:
            self.process_command_module(command_module)

    def process_command_module(self, command_module):
        print("    ", command_module)

    def get_command_modules_from_commands_module(self, commands_module):
        module_infos = pkgutil.iter_modules(commands_module.__path__)

        command_modules = []

        for module_info in module_infos:
            
            # Import the module
            module = importlib.import_module(
                f"{commands_module.__name__}.{module_info.name}"
            )

            if not hasattr(module, "Command"):
                continue

            command_modules.append(module)

        return command_modules

    def get_commands_modules(self):
        kbde_modules = self.get_kbde_modules()

        commands_modules = []

        for module in kbde_modules:
            
            commands_module = self.get_commands_module_for_module(module)

            if commands_module is None:
                continue

            commands_modules.append(commands_module)

        return commands_modules

    def get_commands_module_for_module(self, module):
        """
        Takes a module
        Checks to see if it has a `command` submodule
        """
        try:
            commands_module = importlib.import_module(f"{module.__name__}.commands")

        except ModuleNotFoundError:
            return None
            
        if not hasattr(commands_module, "__path__"):
            return None

        return commands_module

    def get_kbde_modules(self):
        module_infos = pkgutil.iter_modules(kbde.__path__)

        modules = []

        for module_info in module_infos:

            # Import the module
            module = importlib.import_module(f"kbde.{module_info.name}")

            # Check if the module has a path
            # File-based modules will not have this attribute, but
                # directory-based modules will
            if not hasattr(module, "__path__"):
                continue

            modules.append(module)
            
        return modules


class Command:
    """
    A base command to be picked up by kbde_cli
    """

    def add_arguments(self, parser):
        """
        Adds commands to the parser
        """
        return None

    def handle(self, **options):
        """
        Execute this command
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement `.handle(self, **options)`")
