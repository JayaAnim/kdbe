from .file_types import (
    administrative_data_1,
    administrative_data_2,
    vehicle_data,
    profile_labor,
    profile_materials,
    totals,
    detail,
    envelope,
    tax_information,
)


class Estimate:
    dbf_readers = [
        administrative_data_1.DbfReader,
        administrative_data_2.DbfReader,
        vehicle_data.DbfReader,
        profile_labor.PflReader,
        totals.StlDbfReader,
        totals.TtlDbfReader,
        detail.LinDbfReader,
        envelope.DbfReader,

    ]
    
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __str__(self):
        return self.path

    def get_data(self):
        data = {}

        for dbf_reader_class in self.get_dbf_readers():
            dbf_reader = dbf_reader_class.from_estimate_path(self.path)
            data[dbf_reader.get_file_extension()] = dbf_reader

        return data

    def get_dbf_readers(self):
        return self.dbf_readers.copy()
