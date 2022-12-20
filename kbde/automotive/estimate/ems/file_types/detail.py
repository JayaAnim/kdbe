from kbde.automotive.estimate import kbde_fields
from kbde.automotive.estimate.ems import dbf, fields


class LineNumber(fields.Field):
    cieca_field_name = "LINE_NO"
    kbde_field_name = kbde_fields.LINE_NUMBER


class UniqueSequenceNumber(fields.Field):
    cieca_field_name = "UNQ_SEQ"
    kbde_field_name = kbde_fields.UNIQUE_SEQUENCE_NUMBER


class LineDescription(fields.Field):
    cieca_field_name = "LINE_DESC"
    kbde_field_name = kbde_fields.LINE_DESCRIPTION


class OemPartNumber(fields.Field):
    cieca_field_name = "OEM_PARTNO"
    kbde_field_name = kbde_fields.OEM_PART_NUMBER


class AltPartNumber(fields.Field):
    cieca_field_name = "ALT_PARTNO"
    kbde_field_name = kbde_fields.ALT_PART_NUMBER


class PartQuantity(fields.Field):
    cieca_field_name = "PART_QTY"
    kbde_field_name = kbde_fields.PART_QUANTITY


class PartPrice(fields.Field):
    cieca_field_name = "ACT_PRICE"
    kbde_field_name = kbde_fields.PART_PRICE


class PartPriceJudgement(fields.Field):
    cieca_field_name = "PRICE_J"
    kbde_field_name = kbde_fields.PART_PRICE_JUDGMENT


class PartPriceIncludedIndicator(fields.Field):
    cieca_field_name = "PRICE_INC"
    kbde_field_name = kbde_fields.PART_PRICE_INCLUDED_INDICATOR


class PartDescriptionJudgement(fields.Field):
    cieca_field_names = [
        "PART_DESCJ",
        "PART_DES_J",
    ]
    kbde_field_name = kbde_fields.PART_DESCRIPTION_JUDGMENT

    @classmethod
    def from_dbf_record(cls, record):
        for field_name in cls.cieca_field_names:

            try:
                field = cls()
                value = record[field_name]
                field.value = value
                return field

            except KeyError:
                continue

        raise AssertionError(
            'Could not find a value for the given cieca_field_names'
        )


class LaborType(fields.Field):
    cieca_field_name = "MOD_LBR_TY"
    kbde_field_name = kbde_fields.LABOR_TYPE


class LaborTypeJudgement(fields.Field):
    cieca_field_name = "LBR_TYP_J"
    kbde_field_name = kbde_fields.LABOR_TYPE_JUDGMENT


class LaborHours(fields.Field):
    cieca_field_name = "MOD_LB_HRS"
    kbde_field_name = kbde_fields.LABOR_HOURS


class LaborHoursJudgement(fields.Field):
    cieca_field_name = "LBR_HRS_J"
    kbde_field_name = kbde_fields.LABOR_HOURS_JUDGMENT


class LaborOperation(fields.Field):
    cieca_field_name = "LBR_OP"
    kbde_field_name = kbde_fields.LABOR_OPERATION


class LaborIncludedIndicator(fields.Field):
    cieca_field_name = "LBR_INC"
    kbde_field_name = kbde_fields.LABOR_INCLUDED_INDICATOR


class SubletFlag(fields.Field):
    cieca_field_name = "MISC_SUBLT"
    kbde_field_name = "sublet_flag"


class SubletAmount(fields.Field):
    cieca_field_name = "MISC_AMT"
    kbde_field_name = "sublet_amount"


class LinDbfReader(dbf.DbfReader):
    field_list = [
        LineNumber,
        UniqueSequenceNumber,
        LineDescription,
        OemPartNumber,
        AltPartNumber,
        PartQuantity,
        PartPrice,
        PartPriceJudgement,
        PartPriceIncludedIndicator,
        PartDescriptionJudgement,
        LaborType,
        LaborTypeJudgement,
        LaborHours,
        LaborHoursJudgement,
        LaborOperation,
        LaborIncludedIndicator,
        SubletFlag,
        SubletAmount,
    ]
    file_extension = "lin"

