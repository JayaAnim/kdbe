"""
A Python module for interacting with the gcloud command
"""

import subprocess, json, sys


class Gcloud:
    
    def run(self, *args, **kwargs):
        flag_args = {
            "format": "json",
            }
        flag_args.update(kwargs)

        output = self.run_raw(*args, **flag_args)

        return json.loads(output)

    def run_raw(self, *args, **kwargs):
        positional_args = " ".join(args)
        flags = " ".join([f"--{key} {value}" for key, value in kwargs.items()])

        command = f"gcloud {positional_args} {flags}"

        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise self.GcloudException(**e.__dict__)

        return result.stdout

    class GcloudException(subprocess.CalledProcessError):

        def get_stdout(self):
            return self.stderr.decode(sys.getfilesystemencoding())

        def get_stderr(self):
            return self.stderr.decode(sys.getfilesystemencoding())

        def error_has_terms(self, *terms):
            return all(term.lower() in self.get_stderr().lower() for term in terms)
