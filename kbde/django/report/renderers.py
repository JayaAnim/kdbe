import csv, json


class Renderer:
    title = None
    description = None
    file_extension = None

    def __init__(self, output_file, field_names):
        assert self.title, f"{self.__class__.__name__} must define self.title"
        assert self.file_extension, f"{self.__class__.__name__} must define self.file_extension"

        # The file where data will be written
        self.output_file = output_file

        # The field names, in order, for the output file
        self.field_names = field_names

        # The writer instance
        self.writer = self.get_writer()

    def get_writer(self):
        """
        Returns a writer instance for the output file
        """
        raise NotImplementedError
        
    def write_row(self, row):
        """
        Writes a single row
        """
        raise NotImplementedError

    def finalize(self):
        """
        Do anything needed to close off this renderer
        """
        return None


class HeaderRowMixin:
    
    def __init__(self, *args, **kwargs):
        self.header_written = False
        super().__init__(*args, **kwargs)

    def write_row(self, row):
        if not self.header_written:
            self.write_header()
            self.header_written = True

        self.write_body(row)

    def write_header(self):
        """
        Writes the header to the file
        """
        raise NotImplementedError

    def write_body(self, row):
        """
        Writes a line to the body of the file (below the header)
        """
        raise NotImplementedError


class CsvRenderer(HeaderRowMixin, Renderer):
    title = "CSV"
    file_extension = "csv"

    def get_writer(self):
        return csv.DictWriter(self.output_file, fieldnames=self.field_names)

    def write_header(self):
        self.writer.writeheader()
    
    def write_body(self, row):
        self.writer.writerow(row)


class NewlineJsonRenderer(Renderer):
    title = "Newline-delimited JSON"
    file_extension = "txt"
    
    def get_writer(self):
        return None

    def write_row(self, row):
        row_string = json.dumps(row)
        self.output_file.write(f"{row_string}\n")


LIST = [
    CsvRenderer,
    NewlineJsonRenderer,
    ]
