from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class ClaimNumber(fields.Field):
    ems_version = 1.0
    item_number = 28
    subgroup_name = "Claim Information"
    field_name = "Claim Number"
    cieca_field_name = "CLM_NO"
    data_type = str
    description = "Claim Number"
    kbde_field_name = kbde_fields.CLAIM_NUMBER


class InsuranceCompanyName(fields.Field):
    ems_version = 1.0
    item_number = 2
    subgroup_name = "Insurance Company"
    field_name = "Company Name"
    cieca_field_name = "INS_CO_NM"
    data_type = str
    description = "Insurance company name"
    kbde_field_name = kbde_fields.INSURANCE_COMPANY_NAME


class OwnerLastName(fields.Field):
    ems_version = 1.0
    item_number = 101
    subgroup_name = "Owner"
    field_name = "Last Name"
    cieca_field_name = "OWNR_LN"
    data_type = str
    description = "Owner last name"
    kbde_field_name = kbde_fields.OWNER_LAST_NAME


class OwnerFirstName(fields.Field):
    ems_version = 1.0
    item_number = 102
    subgroup_name = "Owner"
    field_name = "First Name"
    cieca_field_name = "OWNR_FN"
    data_type = str
    description = "Owner first name"
    kbde_field_name = kbde_fields.OWNER_FIRST_NAME


class DbfReader(dbf.DbfReader):
    field_list = [
        ClaimNumber,
        InsuranceCompanyName,
        OwnerLastName,
        OwnerFirstName,
    ]
    file_extension = "ad1"
