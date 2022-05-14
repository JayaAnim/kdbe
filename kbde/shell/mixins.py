import subprocess, sys


class RunCommand:

    def run_command(self, command):
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            raise self.CommandException(**e.__dict__)

        return result.stdout.decode("latin1").strip()

    class CommandException(subprocess.CalledProcessError):

        def get_stdout(self):
            return self.output.decode(sys.getfilesystemencoding())

        def get_stderr(self):
            return self.stderr.decode(sys.getfilesystemencoding())

        def error_has_terms(self, *terms):
            return all(term.lower() in self.get_stderr().lower() for term in terms)
