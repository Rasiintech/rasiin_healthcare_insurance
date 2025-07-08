import frappe
from frappe.utils import nowdate, add_months

def execute(filters=None):
    if not filters:
        filters = {}

    # Set default dates: from 1 month ago to today
    if not filters.get("from_date"):
        filters["from_date"] = add_months(nowdate(), -1)
    if not filters.get("to_date"):
        filters["to_date"] = nowdate()

    data = get_data(filters)
    columns = get_columns()
    return columns, data

def get_columns():
    return [
        {"label": "Invoice", "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": 250},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Patient", "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 120},
        {"label": "Patient Name", "fieldname": "patient_name", "fieldtype": "Data", "width": 250},
        {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 180},
        {"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
        {"label": "Paid Amount", "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    return frappe.db.sql("""
        SELECT
            si.name,
            si.posting_date,
            si.patient,
            si.patient_name,
            si.insurance_company,
            si.grand_total,
            si.paid_amount,
            si.status
        FROM `tabSales Invoice` si
        WHERE
            si.docstatus = 1
            AND si.insurance_company IS NOT NULL
            AND si.insurance_company != ''
            AND si.grand_total = si.paid_amount
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND NOT EXISTS (
                SELECT 1 FROM `tabJournal Entry Account` jea
                INNER JOIN `tabJournal Entry` je ON je.name = jea.parent
                WHERE
                    je.docstatus = 1
                    AND jea.reference_type = 'Sales Invoice'
                    AND jea.reference_name = si.name
                    AND jea.party = (
                        SELECT customer FROM `tabInsurance Company`
                        WHERE name = si.insurance_company LIMIT 1
                    )
            )
        ORDER BY si.posting_date DESC
    """, filters, as_dict=True)
