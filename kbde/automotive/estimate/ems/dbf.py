import os


class DbfReader:
    field_list = None
    file_extension = None

    @classmethod
    def from_estimate_path(cls, estimate_path):
        file_names = os.listdir(estimate_path)

        file_extension = cls.get_file_extension()

        for file_name in file_names:
            if file_name.lower().endswith(f".{file_extension}"):
                file_path = os.path.join(estimate_path, file_name)
                return cls(file_path)

        raise cls.FileNotFound(
            f"{cls} could not find a file with a file extension of "
            f"'.{file_extension}' within {estimate_path}"
        )

    @classmethod
    def get_file_extension(cls):
        assert cls.file_extension is not None, (
            f"{cls} must define .file_extension"
        )

        return cls.file_extension
    
    def __init__(self, path):
        self.path = path
        self.dbf = self.get_dbf()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"
    
    def __str__(self):
        return self.get_file_extension()

    def get_dbf(self):
        import dbfread

        return dbfread.DBF(self.path)

    def get_kbde_data(self):
        for record in self.get_data():
            yield {field.get_kbde_field_name(): field for field in record}

    def get_data(self):
        for record in self.dbf:
            yield self.get_fields_from_record(record)
            
    def get_fields_from_record(self, record):
        return [
            field_class.from_dbf_record(record)
            for field_class in self.get_field_list()
        ]

    def get_field_list(self):
        assert self.field_list is not None, (
            f"{self.__class__} must define .field_list"
        )

        return self.field_list.copy()

    class DbfReaderException(Exception):
        pass

    class FileNotFound(DbfReaderException):
        pass
