from kbde import constants

from os import path


class Dockerfile:
    template_path = path.join(
        constants.BASE_DIR,
        "docker",
        "Dockerfile",
    )

    def render_to_file(self, file_path):

        with open(file_path, "w") as f:
            f.write(self.render())

    def render(self):
        template_path = self.get_template_path()

        with open(template_path, "r") as f:
            template_content = f.read()

        return template_content

    def get_template_path(self):
        return self.template_path
