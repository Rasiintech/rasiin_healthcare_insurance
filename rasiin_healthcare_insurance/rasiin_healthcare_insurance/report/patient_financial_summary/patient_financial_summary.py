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
            {"label": "Invoice Number", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 200},
            {"label": "Invoice Date", "fieldname": "invoice_date", "fieldtype": "Date", "width": 150},
            {"label": "Patient Name", "fieldname": "patient_name", "fieldtype": "Data", "width": 200},
            {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
            {"label": "Coverage Limit", "fieldname": "coverage_limits", "fieldtype": "Percentage", "width": 150},
            {"label": "Total Invoiced Amount", "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Amount", "fieldname": "insurance_amount", "fieldtype": "Currency", "width": 150},
            # {"label": "Patient Amount", "fieldname": "patient_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Paid", "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
            # {"label": "Patient Paid", "fieldname": "patient_paid", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Outstanding", "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
            # {"label": "Patient Outstanding", "fieldname": "patient_outstanding", "fieldtype": "Currency", "width": 150},
        ]
    else:
        # Columns for the summary view
        return [
            {"label": "Patient Name", "fieldname": "patient_name", "fieldtype": "Data", "width": 200},
            {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
            {"label": "Coverage Limit", "fieldname": "coverage_limits", "fieldtype": "Percentage", "width": 150},
            {"label": "Total Invoices", "fieldname": "sales_invoice", "fieldtype": "Number", "width": 150},
            {"label": "Total Invoiced Amount", "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 150},
            {"label": "Total Insurance Amount", "fieldname": "total_insurance_amount", "fieldtype": "Currency", "width": 150},
            # {"label": "Total Patient Amount", "fieldname": "total_patient_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Total Insurance Paid Amount", "fieldname": "total_insurance_paid", "fieldtype": "Currency", "width": 150},
            # {"label": "Total Patient Paid Amount", "fieldname": "total_patient_paid", "fieldtype": "Currency", "width": 150},
            {"label": "Total Insurance Outstanding", "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
            # {"label": "Total Patient Outstanding", "fieldname": "patient_outstanding", "fieldtype": "Currency", "width": 150},
        ]


def get_data(filters):
    conditions = ""
    if filters.get("insurance_company"):
        conditions += " AND si.insurance_company=%(insurance_company)s"
    if filters.get("patient"):
        conditions += " AND si.patient=%(patient)s"
    # if filters.get("coverage_limits"):
    #     conditions += " AND si.coverage_limits=%(coverage_limits)s"
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    # Only include invoices with a linked insurance policy
    conditions += " AND si.insurance_policy IS NOT NULL AND si.insurance_coverage_amount IS NOT NULL AND si.insurance_coverage_amount > 0"
    
    if filters.get("detailed"):
        # Detailed view query
        query = """
            SELECT 
                si.name AS sales_invoice,
                si.creation AS invoice_date,
                si.patient AS patient,
                p.patient_name AS patient_name,
                si.insurance_company,
                ip.coverage_limits,
                si.grand_total AS total_invoiced,
                si.insurance_coverage_amount AS insurance_amount,
                si.payable_amount AS patient_amount,
                si.patient_paid AS patient_paid,
                si.insurance_paid AS insurance_paid,
                (si.payable_amount - si.patient_paid) AS patient_outstanding,
                (si.insurance_coverage_amount - si.insurance_paid) AS insurance_outstanding
            FROM 
                `tabSales Invoice` si
            LEFT JOIN 
                `tabInsurance Policy` ip ON si.insurance_policy = ip.name
            LEFT JOIN 
                `tabPatient` p ON ip.policyholder = p.name
            WHERE 
                si.docstatus = 1 {conditions}
        """.format(conditions=conditions)
    else:
        # Summary view query
        query = """
            SELECT 
                COUNT(si.name) AS sales_invoice,
                p.patient_name AS patient_name,
                si.insurance_company,
                ip.coverage_limits,
                SUM(si.grand_total) AS total_invoiced,
                SUM(si.insurance_coverage_amount) AS total_insurance_amount,
                SUM(si.payable_amount) AS total_patient_amount,
                SUM(si.patient_paid) AS total_patient_paid,
                SUM(si.insurance_paid) AS total_insurance_paid,
                SUM(si.payable_amount - si.patient_paid) AS patient_outstanding,
                SUM(si.insurance_coverage_amount - si.insurance_paid) AS insurance_outstanding
            FROM 
                `tabSales Invoice` si
            LEFT JOIN 
                `tabInsurance Policy` ip ON si.insurance_policy = ip.name
            LEFT JOIN 
                `tabPatient` p ON ip.policyholder = p.name
            WHERE 
                si.docstatus = 1 {conditions}
            GROUP BY 
                p.name, si.insurance_company
        """.format(conditions=conditions)

    return frappe.db.sql(query, filters, as_dict=True)
