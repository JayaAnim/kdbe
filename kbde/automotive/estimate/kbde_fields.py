LIST = [
    "repair_order_id",
    "estimate_file_id",

    "claim_number",
    "insurance_company_name",

    "owner_first_name",
    "owner_last_name",
    "owner_phone_number",
    "owner_address_1",
    "owner_address_2",
    "owner_city",
    "owner_state",
    "owner_zip_code",

    "estimating_system",
    "estimator_first_name",
    "estimator_last_name",

    "gross_deductible",
    "gross_customer_responsibility",
    "net_total",
    "total_type",
    "total_type_code",
    "total_type_amount",
    "total_type_hours",
    "gross_total",
    "gross_tax",

    "vin",
    "year",
    "make_code",
    "make",
    "model",

    "labor_type",
    "labor_type_code",
    "labor_rate",
    "labor_description",
    "labor_hours",
    "labor_hours_judgment",
    "labor_type_judgment",
    "labor_included_indicator",
    "labor_operation",
    
    "line_number",
    "unique_sequence_number",
    "line_description",

    "oem_part_number",
    "alt_part_number",
    "part_quantity",
    "part_price",
    "part_price_judgment",
    "part_price_included_indicator",
    "part_description_judgment",
    "sublet_flag",
    "sublet_amount",

    "material_type_code",
    "material_labor_rate",

    "tax_type_1",
    "tax_rate_1",
    "tax_type_2",
    "tax_rate_2",
    "tax_rate_3",
    "tax_type_3",
    "tax_rate_4",
    "tax_type_4",
    "tax_rate_5",
    "tax_type_5",
    "tax_type_6",
    "tax_rate_6",
]


for field_name in LIST:
    globals()[field_name.upper()] = field_name

