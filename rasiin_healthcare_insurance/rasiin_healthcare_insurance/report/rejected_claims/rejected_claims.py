# Copyright (c) 2024, Ahmed Ibar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    # Define columns for the report
    columns = get_columns()

    # Fetch data based on filters
    data = get_data(filters)

    # Calculate summary (totals for key fields)
    summary = calculate_summary(data)

    # Return data with summary rows
    return columns, data, summary

def get_columns():
    # Define columns for the report
    return [
        {"label": "Invoice Number", "fieldname": "invoice_number", "fieldtype": "Data", "width": 150},
        {"label": "Patient Name", "fieldname": "patient_name", "fieldtype": "Data", "width": 200},
        {"label": "Policy Number", "fieldname": "policy_number", "fieldtype": "Data", "width": 150},
        {"label": "Invoice Date", "fieldname": "invoice_date", "fieldtype": "Date", "width": 120},
        {"label": "Invoice Amount", "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Insurance Amount", "fieldname": "insurance_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Patient Amount", "fieldname": "patient_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Is Rejected", "fieldname": "is_rejected", "fieldtype": "Check", "width": 100},
    ]

def get_data(filters):
    # Query data based on the provided filters
    conditions = get_conditions(filters)

    return frappe.db.sql(f"""
        SELECT
            d.invoice_number,
            d.patient_name,
            d.policy_number,
            d.invoice_date,
            d.invoice_amount,
            d.insurance_amount,
            d.patient_amount,
            d.is_rejected
        FROM
            `tabInsurance Claim` c
        INNER JOIN
            `tabDetailed Claim Invoices` d ON c.name = d.parent
        WHERE
            d.is_rejected = 1
            {conditions}
    """, filters, as_dict=True)

def get_conditions(filters):
    # Build dynamic filter conditions
    conditions = ""
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND d.invoice_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("insurance_company"):
        conditions += " AND c.insurance_company = %(insurance_company)s"
    return conditions

def calculate_summary(data):
    # Compute summary totals
    total_invoice_amount = sum(flt(row["invoice_amount"]) for row in data)
    total_insurance_amount = sum(flt(row["insurance_amount"]) for row in data)
    total_patient_amount = sum(flt(row["patient_amount"]) for row in data)

    return [
        {"label": "Total Invoice Amount", "value": total_invoice_amount, "datatype": "Currency"},
        {"label": "Total Insurance Amount", "value": total_insurance_amount, "datatype": "Currency"},
        {"label": "Total Patient Amount", "value": total_patient_amount, "datatype": "Currency"},
    ]

