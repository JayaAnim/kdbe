from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class RepairOrderId(fields.Field):
    cieca_field_name = "RO_ID"
    kbde_field_name = kbde_fields.REPAIR_ORDER_ID


class EstimateFileId(fields.Field):
    cieca_field_name = "ESTFILE_ID"
    kbde_field_name = kbde_fields.ESTIMATE_FILE_ID


class DbfReader(dbf.DbfReader):
    field_list = [
        RepairOrderId,
        EstimateFileId,
    ]
    file_extension = "env"

