from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class MaterialTypeCode(fields.Field):
    cieca_field_name = "MATL_TYPE"
    kbde_field_name = kbde_fields.MATERIAL_TYPE_CODE


class MaterialLaborRate(fields.Field):
    cieca_field_name = "CAL_LBRRTE"
    kbde_field_name = kbde_fields.MATERIAL_LABOR_RATE


class DbfReader(dbf.DbfReader):
    field_list = [
        MaterialTypeCode,
        MaterialLaborRate,
    ]
    file_extension = "pfm"

