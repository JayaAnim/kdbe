from kbde import constants

from os import path


class Dockerfile:
    template_path = path.join(
        constants.BASE_DIR,
        "docker",
        "Dockerfile",
    )

    def __init__(self, python_version):
        self.python_version = python_version

    def render_to_file(self, file_path):

        with open(file_path, "w") as f:
            f.write(self.render())

    def render(self):
        template_content = self.get_template_content()

        return template_content.format(
            python_version=self.python_version,
        )

    def get_template_content(self):
        template_path = self.get_template_path()

        with open(template_path, "r") as f:
            template_content = f.read()

        return template_content

    def get_template_path(self):
        return self.template_path
