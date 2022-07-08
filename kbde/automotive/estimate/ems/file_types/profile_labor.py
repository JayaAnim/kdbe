from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class Type(fields.Field):
    cieca_field_name = "LBR_TYPE"
    kbde_field_name = kbde_fields.LABOR_TYPE


class DbfReader(dbf.DbfReader):
    field_list = [
        Type,
    ]
    file_extension = "pfl"
