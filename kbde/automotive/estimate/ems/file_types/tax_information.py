from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class TaxType1(fields.Field):
    cieca_field_name = "TAX_TYPE1"
    kbde_field_name = kbde_fields.TAX_TYPE_1


class TaxRate1(fields.Field):
    cieca_field_name = "TY1_RATE1"
    kbde_field_name = kbde_fields.TAX_RATE_1


class PflReader(dbf.DbfReader):
    field_list = [
        TaxType1,
        TaxRate1,
    ]
    file_extension = "pft"

