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
            {"label": "Claim Number", "fieldname": "claim_number", "fieldtype": "Link", "options": "Insurance Claim", "width": 200},
            {"label": "Claim Date", "fieldname": "claimed_date", "fieldtype": "Date", "width": 150},
            {"label": "Patient Name", "fieldname": "patient_name", "fieldtype": "Data", "width": 200},
            {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
            {"label": "Invoice Number", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 200},
            {"label": "Invoice Amount", "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Covered Amount", "fieldname": "insurance_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Paid Amount", "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Outstanding Amount", "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
            {"label": "Invoice Status", "fieldname": "invoice_status", "fieldtype": "Data", "width": 100},
            {"label": "Rejection Reason", "fieldname": "rejection_reason", "fieldtype": "Small Text", "width": 150},
        ]
    else:
        # Columns for the summary view
        return [
            {"label": "Claim Number", "fieldname": "claim_number", "fieldtype": "Link", "options": "Insurance Claim", "width": 200},
            {"label": "Claim Date", "fieldname": "claimed_date", "fieldtype": "Date", "width": 150},
            {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
            {"label": "Number of Invoices", "fieldname": "total_invoices", "fieldtype": "Number", "width": 150},
            # {"label": "Claim Total Amount", "fieldname": "claim_total", "fieldtype": "Currency", "width": 150},
            {"label": "Insurance Covered Amount", "fieldname": "total_insurance_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Paid Amount", "fieldname": "total_payment_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Outstanding Amount", "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
            {"label": "Claim Status", "fieldname": "claim_status", "fieldtype": "Data", "width": 100},
        ]

def get_data(filters):
    conditions = ""
    if filters.get("insurance_company"):
        conditions += " AND ic.insurance_company=%(insurance_company)s"
    if filters.get("patient"):
        conditions += " AND dci.patient=%(patient)s"
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND ic.claimed_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("claim_status"):
        conditions += " AND ic.claim_status=%(claim_status)s"

    
    if filters.get("detailed"):
        query = """
            SELECT 
				ic.name AS claim_number,
				ic.claimed_date,
				ic.insurance_company,
				p.patient_name,
				dci.invoice_number AS sales_invoice,
				si.grand_total AS total_invoiced,
				si.insurance_coverage_amount AS insurance_amount,
				si.payable_amount AS patient_amount,
				si.patient_paid AS patient_paid,
				si.insurance_paid AS insurance_paid,
				(si.payable_amount - si.patient_paid) AS patient_outstanding,
				(si.insurance_coverage_amount - si.insurance_paid) AS insurance_outstanding
			FROM 
				`tabInsurance Claim` ic
			LEFT JOIN 
				`tabDetailed Claim Invoices` dci ON ic.name = dci.parent
			LEFT JOIN 
				`tabSales Invoice` si ON dci.invoice_number = si.name
			LEFT JOIN 
				`tabPatient` p ON dci.patient = p.name
			WHERE 
				ic.docstatus = 1
				AND si.docstatus = 1
				{conditions}
			ORDER BY 
				ic.claimed_date DESC, si.name ASC
        """.format(conditions=conditions)
    else:
        query = """
            SELECT 
				ic.name AS claim_number,
				ic.claimed_date,
				ic.insurance_company,
				COUNT(dci.invoice_number) AS total_invoices,
				ic.total_insurance_amount AS total_insurance_amount,
				ic.total_payment_amount AS total_payment_amount,
				(ic.total_insurance_amount - ic.total_payment_amount) AS insurance_outstanding
			FROM 
				`tabInsurance Claim` ic
			LEFT JOIN 
				`tabDetailed Claim Invoices` dci ON ic.name = dci.parent
			LEFT JOIN 
				`tabSales Invoice` si ON dci.invoice_number = si.name
			WHERE 
				ic.docstatus = 1
				AND si.docstatus = 1
				{conditions}
			GROUP BY 
				ic.name, ic.insurance_company
			ORDER BY 
				ic.claimed_date DESC
        """.format(conditions=conditions)
    
    return frappe.db.sql(query, filters, as_dict=True)

