"""
A Python module for interacting with the gcloud command
"""

import subprocess, json


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

        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)

        return result.stdout
