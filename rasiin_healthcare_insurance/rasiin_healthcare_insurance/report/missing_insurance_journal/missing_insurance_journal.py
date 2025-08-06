# missing_insurance_journal.py
# Report: “Insurance Invoices Without Journal Entry”

import frappe
from frappe.utils import nowdate, add_months


def execute(filters=None):
    """
    Frappe report entrypoint.

    Returns (columns, data) where:
      • columns – list[dict] column definitions
      • data    – list[dict] result rows
    """
    filters = filters or {}
    filters.setdefault("from_date", add_months(nowdate(), -1))  # default: 1 month back
    filters.setdefault("to_date",   nowdate())                  # default: today

    return get_columns(), get_data(filters)


# --------------------------------------------------------------------------- #
# Columns
# --------------------------------------------------------------------------- #

def get_columns():
    return [
        # core invoice info
        {"label": "Invoice",       "fieldname": "name",
         "fieldtype": "Link",      "options": "Sales Invoice", "width": 200},
        {"label": "Posting Date",  "fieldname": "posting_date",
         "fieldtype": "Date",                             "width": 100},
        {"label": "Patient",       "fieldname": "patient",
         "fieldtype": "Link",      "options": "Patient",       "width": 130},
        {"label": "Patient Name",  "fieldname": "patient_name",
         "fieldtype": "Data",                              "width": 200},

        # insurance-specific
        {"label": "Insurance Company", "fieldname": "insurance_company",
         "fieldtype": "Link",      "options": "Insurance Company", "width": 180},
        {"label": "Policy",        "fieldname": "insurance_policy",
         "fieldtype": "Data",                              "width": 120},
        {"label": "Coverage Amt",  "fieldname": "insurance_coverage_amount",
         "fieldtype": "Currency",                          "width": 120},
        {"label": "Patient Amt",   "fieldname": "payable_amount",
         "fieldtype": "Currency",                          "width": 120},

        # financials
        {"label": "Grand Total",   "fieldname": "grand_total",
         "fieldtype": "Currency",                          "width": 120},
        {"label": "Paid Amount",   "fieldname": "paid_amount",
         "fieldtype": "Currency",                          "width": 120},
        {"label": "Status",        "fieldname": "status",
         "fieldtype": "Data",                              "width": 90},
    ]


# --------------------------------------------------------------------------- #
# Data query
# --------------------------------------------------------------------------- #


# def get_data(filters):
#     """
#     Return invoices that…
#       • meet the insurance criteria
#       • have reference_journal blank
#       • have NO submitted Journal Entry pointing to them
#           – neither in a JE Account line, NOR in the JE’s reference_invoice field
#     """
#     return frappe.db.sql(
#         """
#         SELECT
#             si.name,
#             si.posting_date,
#             si.patient,
#             si.patient_name,
#             si.insurance_company,
#             si.insurance_policy,
#             si.insurance_coverage_amount,
#             si.payable_amount,
#             si.grand_total,
#             si.paid_amount,
#             si.status
#         FROM `tabSales Invoice` si
#         WHERE
#               si.docstatus = 1
#           AND si.insurance_company IS NOT NULL  AND si.insurance_company  != ''
#           AND si.insurance_policy  IS NOT NULL  AND si.insurance_policy   != ''
#           AND si.insurance_coverage_amount IS NOT NULL
#           AND si.payable_amount IS NOT NULL
#           AND (si.reference_journal IS NULL OR si.reference_journal = '')
#           AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s

#           /* ▸▸ exclude invoices that ARE already referenced in ANY submitted JE */
#           AND NOT EXISTS (
#                 /* 1️⃣ child-row link via Journal Entry Account */
#                 SELECT 1
#                   FROM `tabJournal Entry Account` jea
#                   JOIN `tabJournal Entry` je ON je.name = jea.parent
#                  WHERE je.docstatus      = 1
#                    AND jea.reference_type = 'Sales Invoice'
#                    AND jea.reference_name = si.name
#               UNION ALL
#                 /* 2️⃣ parent-doc link via Journal Entry.reference_invoice */
#                 SELECT 1
#                   FROM `tabJournal Entry` je
#                  WHERE je.docstatus        = 1
#                    AND je.reference_invoice = si.name
#           )

#         ORDER BY si.posting_date DESC
#         """,
#         filters,
#         as_dict=True,
#     )

# --------------------------------------------------------------------------- #
# Data query
# --------------------------------------------------------------------------- #

def get_data(filters):
    """
    Invoices that …
      • meet insurance criteria
      • have reference_journal blank
      • have NO submitted Journal Entry referencing them
      • (optionally) match insurance_company / patient filters
    """

    # base conditions (always applied)
    conditions = [
        "si.docstatus = 1",
        "si.insurance_company IS NOT NULL AND si.insurance_company != ''",
        "si.insurance_policy  IS NOT NULL AND si.insurance_policy  != ''",
        "si.insurance_coverage_amount IS NOT NULL",
        "si.payable_amount IS NOT NULL",
        "(si.reference_journal IS NULL OR si.reference_journal = '')",
        "si.posting_date BETWEEN %(from_date)s AND %(to_date)s",
    ]

    # optional UI filters
    if filters.get("insurance_company"):
        conditions.append("si.insurance_company = %(insurance_company)s")
    if filters.get("patient"):
        conditions.append("si.patient = %(patient)s")

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(
        f"""
        SELECT
            si.name,
            si.posting_date,
            si.patient,
            si.patient_name,
            si.insurance_company,
            si.insurance_policy,
            si.insurance_coverage_amount,
            si.payable_amount,
            si.grand_total,
            si.paid_amount,
            si.status
        FROM `tabSales Invoice` si
        WHERE {where_clause}

          /* exclude invoices already referenced in a submitted Journal Entry */
          AND NOT EXISTS (
                /* child-row link via Journal Entry Account */
                SELECT 1
                  FROM `tabJournal Entry Account` jea
                  JOIN `tabJournal Entry` je ON je.name = jea.parent
                 WHERE je.docstatus      = 1
                   AND jea.reference_type = 'Sales Invoice'
                   AND jea.reference_name = si.name
              UNION ALL
                /* parent-doc link via Journal Entry.reference_invoice */
                SELECT 1
                  FROM `tabJournal Entry` je
                 WHERE je.docstatus        = 1
                   AND je.reference_invoice = si.name
          )

        ORDER BY si.posting_date DESC
        """,
        filters,
        as_dict=True,
    )
