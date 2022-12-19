from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class TaxType1(fields.Field):
    cieca_field_name = "TAX_TYPE1"
    kbde_field_name = kbde_fields.TAX_TYPE_1


class TaxRate1(fields.Field):
    cieca_field_name = "TY1_RATE1"
    kbde_field_name = kbde_fields.TAX_RATE_1


class TaxType2(fields.Field):
    cieca_field_name = "TAX_TYPE2"
    kbde_field_name = kbde_fields.TAX_TYPE_2


class TaxRate2(fields.Field):
    cieca_field_name = "TY2_RATE1"
    kbde_field_name = kbde_fields.TAX_RATE_2


class TaxType3(fields.Field):
    cieca_field_name = "TAX_TYPE3"
    kbde_field_name = kbde_fields.TAX_TYPE_3


class TaxRate3(fields.Field):
    cieca_field_name = "TY3_RATE1"
    kbde_field_name = kbde_fields.TAX_RATE_3


class TaxType4(fields.Field):
    cieca_field_name = "TAX_TYPE4"
    kbde_field_name = kbde_fields.TAX_TYPE_4


class TaxRate4(fields.Field):
    cieca_field_name = "TY4_RATE1"
    kbde_field_name = kbde_fields.TAX_RATE_4


class TaxType5(fields.Field):
    cieca_field_name = "TAX_TYPE5"
    kbde_field_name = kbde_fields.TAX_TYPE_5


class TaxRate5(fields.Field):
    cieca_field_name = "TY5_RATE1"
    kbde_field_name = kbde_fields.TAX_RATE_5


class TaxType6(fields.Field):
    cieca_field_name = "TAX_TYPE6"
    kbde_field_name = kbde_fields.TAX_TYPE_6


class TaxRate6(fields.Field):
    cieca_field_name = "TY6_RATE1"
    kbde_field_name = kbde_fields.TAX_RATE_6


class DbfReader(dbf.DbfReader):
    field_list = [
        TaxType1,
        TaxRate1,
        TaxType2,
        TaxRate2,
        TaxType3,
        TaxRate3,
        TaxType4,
        TaxRate4,
        TaxType5,
        TaxRate5,
        TaxType6,
        TaxRate6,
    ]
    file_extension = "pft"

