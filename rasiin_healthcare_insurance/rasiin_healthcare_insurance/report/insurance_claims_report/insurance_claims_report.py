# Copyright (c) 2024, Ahmed Ibar and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    if filters.get("detailed"):
        # Columns for the detailed view
        return [
            {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
            {"label": "Hospital Name", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 200},
            {"label": "Patient", "fieldname": "patient", "fieldtype": "Data", "width": 150},
            {"label": "Patient Name", "fieldname": "patient_name", "fieldtype": "Data", "width": 200},
            {"label": "Date of Birth", "fieldname": "dob", "fieldtype": "Data", "width": 150},
            {"label": "Policy Number", "fieldname": "policy_number", "fieldtype": "Data", "width": 150},
            {"label": "Date of Service", "fieldname": "invoice_date", "fieldtype": "Data", "width": 150},
            {"label": "Coverage Limit", "fieldname": "coverage_limits", "fieldtype": "Data", "options": "Insurance Company", "width": 150},
            {"label": "Invoice Number", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 200},
            {"label": "Journal Number", "fieldname": "reference_journal", "fieldtype": "Link", "options": "Journal Entry", "width": 200},
            {"label": "Invoice Amount", "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 150},
            {"label": "Patient Amount", "fieldname": "patient_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Covered Amount", "fieldname": "insurance_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Paid Amount", "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Outstanding Amount", "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
        ]
    else:
        # Columns for the summary view
        return [
            # {"label": "Claim Number", "fieldname": "claim_number", "fieldtype": "Link", "options": "Insurance Claim", "width": 200},
            # {"label": "Claim Date", "fieldname": "claimed_date", "fieldtype": "Date", "width": 150},
            {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
            {"label": "Number of Invoices", "fieldname": "total_invoices", "fieldtype": "Number", "width": 150},
            # {"label": "Claim Total Amount", "fieldname": "claim_total", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Covered Amount", "fieldname": "total_insurance_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Paid Amount", "fieldname": "total_payment_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Outstanding Amount", "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
            # {"label": "Claim Status", "fieldname": "claim_status", "fieldtype": "Data", "width": 100},
        ]

def get_data(filters):
    conditions = []
    params = {}

    if filters.get("insurance_company"):
        conditions.append("si.insurance_company = %(insurance_company)s")
        params["insurance_company"] = filters["insurance_company"]
    else:
        # Ensure only invoices with an insurance company are included
        conditions.append("si.insurance_company IS NOT NULL AND si.insurance_company != ''")

    if filters.get("patient"):
        conditions.append("si.patient = %(patient)s")
        params["patient"] = filters["patient"]

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("si.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params["from_date"] = filters["from_date"]
        params["to_date"] = filters["to_date"]

    if filters.get("invoice_status"):
        conditions.append("si.status = %(invoice_status)s")
        params["invoice_status"] = filters["invoice_status"]

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE si.docstatus = 1 And si.coverage_limits >0 AND " + where_clause
    else:
        where_clause = "WHERE si.docstatus = 1 and si.coverage_limits> 0 "

    if filters.get("detailed"):
        query = f"""
            SELECT 
                si.company AS company,
                si.name AS sales_invoice,
                si.reference_journal AS reference_journal,
                si.posting_date AS invoice_date,
                si.patient AS patient,
                si.patient_name AS patient_name,
                si.insurance_company,
                si.coverage_limits,
                si.grand_total AS total_invoiced,
                si.insurance_coverage_amount AS insurance_amount,
                si.payable_amount AS patient_amount,
                si.patient_paid AS patient_paid,
                si.insurance_paid AS insurance_paid,
                (si.payable_amount - si.patient_paid) AS patient_outstanding,
                (si.insurance_coverage_amount - si.insurance_paid) AS insurance_outstanding,
                si.status AS invoice_status,
                p.dob AS dob,
                si.policy_number AS policy_number

            FROM 
                `tabSales Invoice` si
            LEFT JOIN `tabPatient` p ON p.name = si.patient
            {where_clause}
            ORDER BY 
                p.patient_name ASC
        """
    else:
        query = f"""
            SELECT 
                si.insurance_company,
                COUNT(si.name) AS total_invoices,
                SUM(si.insurance_coverage_amount) AS total_insurance_amount,
                SUM(si.insurance_paid) AS total_payment_amount,
                (SUM(si.insurance_coverage_amount) - SUM(si.insurance_paid)) AS insurance_outstanding
            FROM 
                `tabSales Invoice` si
            {where_clause}
            GROUP BY 
                si.insurance_company
            ORDER BY 
                si.posting_date DESC
        """

    return frappe.db.sql(query, params, as_dict=True)

