import subprocess, shlex, tempfile


class Pdftk:

    def __init__(self, pdf_path, temp_directory=None):
        self.pdf_path = pdf_path
        self.temp_directory = temp_directory

    def concatenate(self, pdf_path):
        output_path = self.create_tempfile()

        self.pdf_path = self.run_command(
            [self.pdf_path, pdf_path],
            operation="cat",
            output_path=output_path,
        )

    def set_passwords(self, owner_password="", user_password=""):
        output_path = self.create_tempfile()

        self.pdf_path = self.run_command(
            [self.pdf_path],
            output_path=output_path,
            owner_password=owner_password,
            user_password=user_password,
        )

    def add_background(self, background_pdf_path):
        output_path = self.create_tempfile()

        self.pdf_path = self.run_command(
            [self.pdf_path],
            operation="background",
            operation_arguments=[shlex.quote(background_pdf_path)],
            output_path=output_path,
        )
    
    def generate_fdf(self):
        """
        Generates an fdf file from self.pdf_path
        """
        # Generate a new named tempfile for the fdf file
        output_path = self.create_tempfile()

        return self.run_command(
            [self.pdf_path],
            operation="generate_fdf",
            output_path=output_path,
        )

    def fill_form(self, fdf_path):
        return self.run_command(
            [self.pdf_path],
            operation="fill_form",
            operation_arguments=[fdf_path],
            output_path=self.create_tempfile()
        )

    def create_tempfile(self):
        with tempfile.NamedTemporaryFile(dir=self.temp_directory, delete=False) as temp:
            pass

        return temp.name

    def run_command(self, input_pdf_paths,
                          operation="",
                          operation_arguments=[],
                          output_path=None,
                          owner_password="",
                          user_password=""):
        # Concatenate input file names
        input_pdf_paths = [
            shlex.quote(path) for path in input_pdf_paths
        ]
        input_pdf_file_names = " ".join(input_pdf_paths)

        # Concatenate operation_arguments
        operation_arguments = " ".join(operation_arguments)

        # Output command
        if output_path is not None:
            output = f"output {output_path}"
        else:
            output = ""

        # Passwords
        if owner_password:
            owner_password = f"owner_pw {owner_password}"

        if user_password:
            user_password = f"user_pw {user_password}"

        if owner_password or user_password:
            password_printing = "allow printing"
        else:
            password_printing = ""

        command = (f"pdftk {input_pdf_file_names} "
                   f"{operation} {operation_arguments} "
                   f"{output} "
                   f"{owner_password} {user_password} {password_printing}")

        command = shlex.split(command)
        subprocess.check_output(command)

        return output_path
