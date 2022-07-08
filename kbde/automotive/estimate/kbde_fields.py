LIST = [
    "claim_number",
    "insurance_company_name",
    "owner_first_name",
    "owner_last_name",
    "gross_deductible",
    "gross_customer_responsibility",
    "net_total",
    "total_type",
    "total_type_code",
    "type_total",
    "gross_total",
    "gross_tax",
    "vin",
    "year",
    "make_code",
    "make",
    "model",
    "labor_type",
]


for field_name in LIST:
    globals()[field_name.upper()] = field_name
