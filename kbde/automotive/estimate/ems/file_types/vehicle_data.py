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


class LicensePlateNumber(fields.Field):
    cieca_field_name = "PLATE_NO"
    kbde_field_name = kbde_fields.LICENSE_PLATE_NUMBER


class LicensePlateState(fields.Field):
    cieca_field_name = "PLATE_ST"
    kbde_field_name = kbde_fields.LICENSE_PLATE_STATE


class ExteriorColor(fields.Field):
    cieca_field_name = "V_COLOR"
    kbde_field_name = kbde_fields.EXTERIOR_COLOR


class ProductionDate(fields.Field):
    cieca_field_name = "V_PROD_DT"
    kbde_field_name = kbde_fields.PRODUCTION_DATE


class MileageIn(fields.Field):
    cieca_field_name = "V_MILEAGE"
    kbde_field_name = kbde_fields.MILEAGE_IN


class Condition(fields.Field):
    cieca_field_name = "V_COND"
    kbde_field_name = kbde_fields.CONDITION


class DbfReader(dbf.DbfReader):
    field_list = [
        Vin,
        Year,
        MakeCode,
        MakeDescription,
        Model,
        LicensePlateNumber,
        LicensePlateState,
        ExteriorColor,
        ProductionDate,
        MileageIn,
        Condition,
    ]
    file_extension = "veh"

