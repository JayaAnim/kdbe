import subprocess, shlex, tempfile


class Pdftk:

    def __init__(self, pdf):
        self.pdf = pdf

    def set_passwords(self, owner_password="", user_password=""):
        output_file = self.get_new_tempfile()

        self.pdf = self.run_command([self.pdf],
                                    output_file=output_file,
                                    owner_password=owner_password,
                                    user_password=user_password)

    def add_background(self, background_pdf_file):
        output_file = self.get_new_tempfile()

        self.pdf = self.run_command([self.pdf],
                                    operation="background",
                                    operation_arguments=[shlex.quote(background_pdf_file.name)],
                                    output_file=output_file)
    
    def generate_fdf(self):
        """
        Generates an fdf file from self.pdf
        """
        # Generate a new named tempfile for the fdf file
        output_file = self.get_new_tempfile()

        return self.run_command([self.pdf], operation="generate_fdf", output_file=output_file)

    def get_new_tempfile(self):
        with tempfile.NamedTemporaryFile(delete=False) as new_tempfile:
            pass

        return new_tempfile

    def run_command(self, input_pdf_files,
                          operation="",
                          operation_arguments=[],
                          output_file=None,
                          owner_password="",
                          user_password=""):
        # Concatenate input file names
        input_pdf_file_names = " ".join([shlex.quote(f.name) for f in input_pdf_files])

        # Concatenate operation_arguments
        operation_arguments = " ".join(operation_arguments)

        # Output command
        if output_file is not None:
            output = f"output {output_file.name}"
        else:
            output = ""

        # Passwords
        if owner_password:
            owner_password = f"owner_pw {owner_password}"

        if user_password:
            user_password = f"user_pw {user_password}"

        command = (f"pdftk {input_pdf_file_names} "
                   f"{operation} {operation_arguments} "
                   f"{output} "
                   f"{owner_password} {user_password}")

        command = shlex.split(command)
        subprocess.check_output(command)

        return output_file
