from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class Vin(fields.Field):
    cieca_field_name = "V_VIN"
    kbde_field_name = kbde_fields.VIN


class Year(fields.Field):
    cieca_field_name = "V_MODEL_YR"
    kbde_field_name = kbde_fields.YEAR


class MakeCode(fields.Field):
    cieca_field_name = "V_MAKECODE"
    kbde_field_name = kbde_fields.MAKE_CODE


class MakeDescription(fields.Field):
    cieca_field_name = "V_MAKEDESC"
    kbde_field_name = kbde_fields.MAKE


class Model(fields.Field):
    cieca_field_name = "V_MODEL"
    kbde_field_name = kbde_fields.MODEL


class DbfReader(dbf.DbfReader):
    field_list = [
        Vin,
        Year,
        MakeCode,
        MakeDescription,
        Model,
    ]
    file_extension = "veh"
