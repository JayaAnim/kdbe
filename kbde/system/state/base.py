from kbde.shell import mixins as shell_mixins


class OutputWrapper:

    def __init__(self, stdout=None):
        self.stdout = stdout

    def write(self, message):
        if self.stdout:
            self.stdout.write(message)


class State:
    dependencies = []
    
    def __init__(self, stdout=None):
        self.make_run = False
        self.stdout = OutputWrapper(stdout)

    def run(self):
        for state_class in self.get_dependencies():
            state = state_class(stdout=self.stdout)
            state.run()

        if not self.check(self.make_run):
            self.make()
            self.make_run = True
            
            if not self.check(self.make_run):
                raise self.StateMakeException(
                    f"{self.__class__} .make() method did not change the "
                    f"system state so that the .check() method would return "
                    f"True. It reutrned False instead."
                )
    
    def check(self, make_run):
        """
        Perform a state check to see if the state should be executed
        """
        raise NotImplementedError(
            f"{self.__class__} must implement a .check() method, which "
            f"returns a True or a False depending on if the state is valid."
        )

    def make(self):
        """
        Make the state so that the .check() method will return True if run
        again
        """
        raise NotImplementedError(
            f"{self.__class__} must implement a .make() method, which "
            f"changes the system so that the .check() method would return "
            f"True if it were run afterwards."
        )

    def get_dependencies(self):
        return self.dependencies.copy()

    class StateException(Exception):
        pass

    class StateCheckError(StateException):
        pass

    class StateMakeException(StateException):
        pass


class AlwaysMakeMixin:
    
    def check(self, make_run):
        return make_run


# Filesystem

class FileMixin:

    def file_contains_string(self, file_path, string):
        with open(file_path) as open_file:
            return string in open_file.read()

    def file_icontains_string(self, file_path, string):
        with open(file_path) as open_file:
            return string.lower() in open_file.read().lower()

    def add_line_to_file(self, file_path, line):
        with open(file_path, "a") as open_file:
            open_file.write(f"{line}\n")


class LineInFile(FileMixin, State):
    file_path = None
    file_line = None

    def check(self, make_run):
        return self.file_contains_string(
            self.get_file_path(),
            self.get_file_line(),
        )

    def make(self):
        return self.add_line_to_file(
            self.get_file_path(),
            self.get_file_line(),
        )

    def get_file_path(self):
        assert self.file_path is not None, (
            f"{self.__class__} must define .file_path or override .get_file_path()"
        )
        return self.file_path

    def get_file_line(self):
        assert self.file_line is not None, (
            f"{self.__class__} must define .file_line or override .get_file_line()"
        )
        return self.file_line


# Apt

class AptMixin(shell_mixins.RunCommand):
    update_command = "apt-get update"
    install_command = "apt-get install -y {package_names}"
    add_repository_command = "add-apt-repository -y {repository_uri}"

    def update(self):
        return self.run_command(self.update_command)
        
    def install_packages(self, package_names):
        package_names = " ".join(package_names)
        return self.run_command(
            self.install_command.format(package_names=package_names)
        )

    def add_apt_repository(self, repository_uri):
        command = self.add_repository_command.format(repository_uri=repository_uri)

        SoftwarePropertiesCommonInstalled().run()

        return self.run_command(command)


class AptUpdated(AlwaysMakeMixin, AptMixin, State):
    
    def make(self):
        self.stdout.write(self.update())


class AptInstalled(AlwaysMakeMixin, AptMixin, State):
    package_names = None

    def make(self):
        self.stdout.write(self.install_packages(self.get_package_names()))

    def get_package_names(self):
        assert self.package_names, (
            f"{self.__class__} must define .package_names or override "
            f".get_package_names()"
        )
        return self.package_names.copy()


class AptRepositoryAdded(AlwaysMakeMixin, AptMixin, State):
    repository_uri = None

    def make(self):
        self.stdout.write(self.add_apt_repository(self.get_repository_uri()))

    def get_repository_uri(self):
        assert self.repository_uri, (
            f"{self.__class__} must define .repository_uri or override "
            f".get_repository_uri()"
        )
        return self.repository_uri


class SoftwarePropertiesCommonInstalled(AptInstalled):
    package_names = [
        "software-properties-common",
    ]

    def run_command(self, command):
        return super().run_command(
            f"DEBIAN_FRONTEND=noninteractive {command}"
        )


# User

class UserMixin:
    user_environment_params = None
    
    def check_user_exists(self):
        pass

    def create_user(self, username, password=None):
        pass

    def check_user_in_group(self, username, groupname):
        pass

    def add_user_to_group(self, username, groupname):
        pass

    def get_user_params_from_environment(self):
        params = self.get_user_envionrment_params()

    def get_user_envionrment_params(self):
        return 
