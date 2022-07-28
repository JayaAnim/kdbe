from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class EstimatorFirstName(fields.Field):
    cieca_field_name = "EST_CT_FN"
    kbde_field_name = kbde_fields.ESTIMATOR_FIRST_NAME


class EstimatorLastName(fields.Field):
    cieca_field_name = "EST_CT_LN"
    kbde_field_name = kbde_fields.ESTIMATOR_LAST_NAME


class DbfReader(dbf.DbfReader):
    field_list = [
        EstimatorLastName,
        EstimatorFirstName,
    ]
    file_extension = "ad2"

