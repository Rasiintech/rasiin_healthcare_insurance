# Copyright (c) 2024, Ahmed Ibar and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
    ]

    if filters.get("detailed"):
        # Detailed Report Columns
        columns.extend([
            {"label": "Patient Name", "fieldname": "patient_name", "fieldtype": "Data", "width": 200},
            {"label": "Policy Number", "fieldname": "policy_number", "fieldtype": "Data", "width": 150},
            {"label": "Expiry Date", "fieldname": "expiration_date", "fieldtype": "Date", "width": 150},
            {"label": "Coverage Limit", "fieldname": "coverage_limit", "fieldtype": "Currency", "width": 150},
        ])
    else:
        # Summary Report Columns
        columns.append(
            {"label": "Number of Patients", "fieldname": "patient_count", "fieldtype": "Int", "width": 150}
        )

    return columns

def get_data(filters):
    conditions = ""
    if filters.get("insurance_company"):
        conditions += " AND ip.insurance_company=%(insurance_company)s"
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND ip.creation BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("detailed"):
        # Fetch detailed patient and policy data
        query = """
            SELECT 
                ip.insurance_company,
                p.patient_name AS patient_name,
                ip.name AS policy_number,
                ip.expiration_date,
                ip.coverage_limits AS coverage_limit
            FROM 
                `tabInsurance Policy` ip
            LEFT JOIN 
                `tabPatient` p ON ip.policyholder = p.name
            WHERE 
                ip.docstatus < 2 {conditions}
            ORDER BY 
                ip.insurance_company, p.patient_name
        """.format(conditions=conditions)
    else:
        # Fetch summary data
        query = """
            SELECT 
                ip.insurance_company,
                COUNT(DISTINCT ip.policyholder) as patient_count
            FROM 
                `tabInsurance Policy` ip
            WHERE 
                ip.docstatus < 2 {conditions}
            GROUP BY 
                ip.insurance_company
        """.format(conditions=conditions)

    return frappe.db.sql(query, filters, as_dict=True)
