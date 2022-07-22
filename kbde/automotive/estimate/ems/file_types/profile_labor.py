from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class LaborTypeCode(fields.Field):
    cieca_field_name = "LBR_TYPE"
    kbde_field_name = kbde_fields.LABOR_TYPE_CODE


class LaborRate(fields.Field):
    cieca_field_name = "LBR_RATE"
    kbde_field_name = kbde_fields.LABOR_RATE


class PflReader(dbf.DbfReader):
    field_list = [
        LaborTypeCode,
        LaborRate,
    ]
    file_extension = "pfl"

