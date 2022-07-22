from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class TotalType(fields.Field):
    cieca_field_name = "TTL_TYPE"
    kbde_field_name = kbde_fields.TOTAL_TYPE


class TotalTypeCode(fields.Field):
    cieca_field_name = "TTL_TYPECD"
    kbde_field_name = kbde_fields.TOTAL_TYPE_CODE


class TotalTypeAmount(fields.Field):
    cieca_field_name = "TTL_AMT"
    kbde_field_name = kbde_fields.TOTAL_TYPE_AMOUNT


class TotalTypeHours(fields.Field):
    cieca_field_name = "TTL_HRS"
    kbde_field_name = kbde_fields.TOTAL_TYPE_HOURS


class StlDbfReader(dbf.DbfReader):
    field_list = [
        TotalType,
        TotalTypeCode,
        TotalTypeAmount,
        TotalTypeHours,
    ]
    file_extension = "stl"


class GrossTotalAmount(fields.Field):
    cieca_field_name = "G_TTL_AMT"
    kbde_field_name = kbde_fields.GROSS_TOTAL


class GrossDeductibleAmount(fields.Field):
    cieca_field_name = "G_DED_AMT"
    kbde_field_name = kbde_fields.GROSS_DEDUCTIBLE


class GrossCustomerResponsibilityAmount(fields.Field):
    cieca_field_name = "G_CUST_AMT"
    kbde_field_name = kbde_fields.GROSS_CUSTOMER_RESPONSIBILITY


class NetTotalAmount(fields.Field):
    cieca_field_name = "N_TTL_AMT"
    kbde_field_name = kbde_fields.NET_TOTAL


class GrossTaxAmount(fields.Field):
    cieca_field_name = "G_TAX"
    kbde_field_name = kbde_fields.GROSS_TAX


class TtlDbfReader(dbf.DbfReader):
    field_list = [
        GrossTotalAmount,
        GrossDeductibleAmount,
        GrossCustomerResponsibilityAmount,
        NetTotalAmount,
        GrossTaxAmount,
    ]
    file_extension = "ttl"
