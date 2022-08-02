LIST = [
    "repair_order_id",
    "estimate_file_id",

    "claim_number",
    "insurance_company_name",
    "owner_first_name",
    "owner_last_name",
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
    "labor_hours",
    "labor_hours_judgment",
    "labor_type_judgment",
    "labor_included_indicator",
    "labor_operation",
    
    "line_number",
    "line_description",

    "oem_part_number",
    "alt_part_number",
    "part_quantity",
    "part_price",
    "part_price_judgment",
    "part_price_included_indicator",
    "part_description_judgment",
]


for field_name in LIST:
    globals()[field_name.upper()] = field_name

