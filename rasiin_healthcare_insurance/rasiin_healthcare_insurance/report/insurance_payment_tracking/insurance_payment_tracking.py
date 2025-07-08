# from frappe import _
# import frappe
# from frappe.utils import flt

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     insurance_data = get_insurance_journal_summary(filters)

#     # Debug: print full insurance_data to error log
#     frappe.errprint("DEBUG: insurance_data fetched from DB:")
#     for row in insurance_data:
#         frappe.errprint(row)

#     payment_map = get_insurance_payment_map(filters)

#     results = []
#     for row in insurance_data:
#         journal = row.get("journal_entry")
        
#         # Debug: print insurance_covered and insurance_returned for each row
#         frappe.errprint(f"DEBUG: Journal: {journal} | Covered: {row.get('insurance_covered')} | Returned: {row.get('insurance_returned')}")

#         row["insurance_covered"] = flt(row.get("insurance_covered") or 0)
#         row["insurance_returned"] = flt(row.get("insurance_returned") or 0)
#         row["insurance_paid"] = flt(payment_map.get(journal, 0))
#         row["insurance_outstanding"] = (
#             row["insurance_covered"]
#             - row["insurance_returned"]
#             - row["insurance_paid"]
#         )
#         results.append(row)

#     return get_columns(), results


# # ----------------------------------------
# # 1. Get Insurance Journals (Coverage + Returns)
# # ----------------------------------------
# def get_insurance_journal_summary(filters):
#     conditions = ["je.docstatus = 1"]

#     if filters.get("from_date"):
#         conditions.append("je.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("je.posting_date <= %(to_date)s")
#     if filters.get("insurance_company"):
#         conditions.append("je.insurance_company = %(insurance_company)s")
#     if filters.get("patient"):
#         conditions.append("je.patient = %(patient)s")

#     query = """
#         SELECT
#             je.insurance_company AS insurance_company,
#             je.sales_invoice AS sales_invoice,
#             je.name AS journal_entry,
#             SUM(jea.debit) AS insurance_covered,
#             SUM(jea.credit) AS insurance_returned
#         FROM `tabJournal Entry` je
#         INNER JOIN `tabJournal Entry Account` jea ON jea.parent = je.name
#         WHERE {conditions}
#         AND jea.party = (
#             SELECT customer FROM `tabInsurance Company`
#             WHERE name = je.insurance_company LIMIT 1
#         )
#         GROUP BY je.name, je.sales_invoice, je.insurance_company
#         ORDER BY je.posting_date DESC
#     """.format(conditions=" AND ".join(conditions))

#     frappe.errprint(f"DEBUG: get_insurance_journal_summary SQL:\n{query}")
#     return frappe.db.sql(query, filters, as_dict=True)


# # ----------------------------------------
# # 2. Get Payments Linked to Insurance Journals
# # ----------------------------------------
# def get_insurance_payment_map(filters):
#     # Conditions for Journal Entry Account linked payments
#     conditions_jea = [
#         "je.docstatus = 1",
#         "jea.reference_type = 'Journal Entry'"
#     ]
#     if filters.get("from_date"):
#         conditions_jea.append("je.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions_jea.append("je.posting_date <= %(to_date)s")
#     if filters.get("insurance_company"):
#         conditions_jea.append("jea.party = (SELECT customer FROM `tabInsurance Company` WHERE name = %(insurance_company)s LIMIT 1)")

#     query_jea = """
#         SELECT
#             jea.reference_name AS insurance_journal,
#             SUM(jea.credit) AS paid
#         FROM `tabJournal Entry Account` jea
#         INNER JOIN `tabJournal Entry` je ON je.name = jea.parent
#         WHERE {conditions}
#         GROUP BY jea.reference_name
#     """.format(conditions=" AND ".join(conditions_jea))

#     frappe.errprint(f"DEBUG: get_insurance_payment_map (Journal Entry Account) SQL:\n{query_jea}")
#     payments_jea = frappe.db.sql(query_jea, filters, as_dict=True)

#     # Conditions for Payment Entry references
#     conditions_pe = ["pe.docstatus = 1"]
#     if filters.get("from_date"):
#         conditions_pe.append("pe.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions_pe.append("pe.posting_date <= %(to_date)s")
#     if filters.get("insurance_company"):
#         conditions_pe.append("pe.party = (SELECT customer FROM `tabInsurance Company` WHERE name = %(insurance_company)s LIMIT 1)")

#     query_pe = """
#         SELECT
#             per.reference_name AS insurance_journal,
#             SUM(per.allocated_amount) AS paid
#         FROM `tabPayment Entry Reference` per
#         INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
#         WHERE {conditions}
#         GROUP BY per.reference_name
#     """.format(conditions=" AND ".join(conditions_pe))

#     frappe.errprint(f"DEBUG: get_insurance_payment_map (Payment Entry Reference) SQL:\n{query_pe}")
#     payments_pe = frappe.db.sql(query_pe, filters, as_dict=True)

#     frappe.errprint("DEBUG: Payments fetched from Journal Entry Account:")
#     for p in payments_jea:
#         frappe.errprint(p)
#     frappe.errprint("DEBUG: Payments fetched from Payment Entry Reference:")
#     for p in payments_pe:
#         frappe.errprint(p)

#     # Combine both payment sources into one map
#     payment_map = {}

#     for row in payments_jea:
#         payment_map[row.insurance_journal] = payment_map.get(row.insurance_journal, 0) + flt(row.paid)

#     for row in payments_pe:
#         payment_map[row.insurance_journal] = payment_map.get(row.insurance_journal, 0) + flt(row.paid)

#     return payment_map


# # ----------------------------------------
# # 3. Report Columns (explicit fieldnames)
# # ----------------------------------------
# def get_columns():
#     return [
#         {"label": _("Insurance Company"), "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
#         {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
#         {"label": _("Insurance Journal"), "fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "width": 150},
#         {"label": _("Insurance Covered (Debit)"), "fieldname": "insurance_covered", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Returned (Credit)"), "fieldname": "insurance_returned", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Paid"), "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Outstanding"), "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
#     ]


# from frappe import _
# import frappe
# from frappe.utils import flt

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     detailed = filters.get("detailed")

#     insurance_data = get_insurance_journal_summary(filters)
#     frappe.errprint("DEBUG: insurance_data fetched from DB:")
#     for row in insurance_data:
#         frappe.errprint(row)

#     payment_map = get_insurance_payment_map(filters)

#     results = []

#     if detailed:
#         # Detailed view: row per journal entry
#         for row in insurance_data:
#             journal = row.get("journal_entry")
#             frappe.errprint(f"DEBUG: Journal: {journal} | Covered: {row.get('insurance_covered')} | Returned: {row.get('insurance_returned')}")

#             row["insurance_covered"] = flt(row.get("insurance_covered") or 0)
#             row["insurance_returned"] = flt(row.get("insurance_returned") or 0)
#             row["insurance_paid"] = flt(payment_map.get(journal, 0))
#             row["insurance_outstanding"] = (
#                 row["insurance_covered"]
#                 - row["insurance_returned"]
#                 - row["insurance_paid"]
#             )
#             results.append(row)
#         return get_detailed_columns(), results

#     else:
#         # Summary view: aggregated by insurance company & hospital
#         summary = {}
#         for row in insurance_data:
#             journal = row.get("journal_entry")
#             key = (row.get("insurance_company"), row.get("company"))

#             if key not in summary:
#                 summary[key] = {
#                     "insurance_company": row.get("insurance_company"),
#                     "company": row.get("company"),
#                     "insurance_covered": 0,
#                     "insurance_returned": 0,
#                     "insurance_paid": 0
#                 }

#             summary[key]["insurance_covered"] += flt(row.get("insurance_covered") or 0)
#             summary[key]["insurance_returned"] += flt(row.get("insurance_returned") or 0)
#             summary[key]["insurance_paid"] += flt(payment_map.get(journal, 0))

#         for row in summary.values():
#             row["insurance_outstanding"] = (
#                 row["insurance_covered"]
#                 - row["insurance_returned"]
#                 - row["insurance_paid"]
#             )
#             results.append(row)

#         return get_summary_columns(), results


# # ----------------------------------------
# # 1. Get Insurance Journals (Coverage + Returns)
# # ----------------------------------------
# def get_insurance_journal_summary(filters):
#     conditions = ["je.docstatus = 1"]

#     if filters.get("from_date"):
#         conditions.append("je.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("je.posting_date <= %(to_date)s")
#     if filters.get("insurance_company"):
#         conditions.append("je.insurance_company = %(insurance_company)s")
#     if filters.get("patient"):
#         conditions.append("je.patient = %(patient)s")

#     query = """
#         SELECT
#             je.insurance_company AS insurance_company,
#             je.company AS company,
#             je.sales_invoice AS sales_invoice,
#             je.name AS journal_entry,
#             SUM(jea.debit) AS insurance_covered,
#             SUM(jea.credit) AS insurance_returned
#         FROM `tabJournal Entry` je
#         INNER JOIN `tabJournal Entry Account` jea ON jea.parent = je.name
#         WHERE {conditions}
#         AND jea.party = (
#             SELECT customer FROM `tabInsurance Company`
#             WHERE name = je.insurance_company LIMIT 1
#         )
#         GROUP BY je.name, je.sales_invoice, je.insurance_company, je.company
#         ORDER BY je.posting_date DESC
#     """.format(conditions=" AND ".join(conditions))

#     frappe.errprint(f"DEBUG: get_insurance_journal_summary SQL:\n{query}")
#     return frappe.db.sql(query, filters, as_dict=True)


# # ----------------------------------------
# # 2. Get Payments Linked to Insurance Journals
# # ----------------------------------------
# def get_insurance_payment_map(filters):
#     # From Journal Entry Account
#     conditions_jea = [
#         "je.docstatus = 1",
#         "jea.reference_type = 'Journal Entry'"
#     ]
#     if filters.get("from_date"):
#         conditions_jea.append("je.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions_jea.append("je.posting_date <= %(to_date)s")
#     if filters.get("insurance_company"):
#         conditions_jea.append("jea.party = (SELECT customer FROM `tabInsurance Company` WHERE name = %(insurance_company)s LIMIT 1)")

#     query_jea = """
#         SELECT
#             jea.reference_name AS insurance_journal,
#             SUM(jea.credit) AS paid
#         FROM `tabJournal Entry Account` jea
#         INNER JOIN `tabJournal Entry` je ON je.name = jea.parent
#         WHERE {conditions}
#         GROUP BY jea.reference_name
#     """.format(conditions=" AND ".join(conditions_jea))

#     frappe.errprint(f"DEBUG: get_insurance_payment_map (Journal Entry Account) SQL:\n{query_jea}")
#     payments_jea = frappe.db.sql(query_jea, filters, as_dict=True)

#     # From Payment Entry
#     conditions_pe = ["pe.docstatus = 1"]
#     if filters.get("from_date"):
#         conditions_pe.append("pe.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions_pe.append("pe.posting_date <= %(to_date)s")
#     if filters.get("insurance_company"):
#         conditions_pe.append("pe.party = (SELECT customer FROM `tabInsurance Company` WHERE name = %(insurance_company)s LIMIT 1)")

#     query_pe = """
#         SELECT
#             per.reference_name AS insurance_journal,
#             SUM(per.allocated_amount) AS paid
#         FROM `tabPayment Entry Reference` per
#         INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
#         WHERE {conditions}
#         GROUP BY per.reference_name
#     """.format(conditions=" AND ".join(conditions_pe))

#     frappe.errprint(f"DEBUG: get_insurance_payment_map (Payment Entry Reference) SQL:\n{query_pe}")
#     payments_pe = frappe.db.sql(query_pe, filters, as_dict=True)

#     # Merge both sources
#     payment_map = {}
#     for row in payments_jea:
#         payment_map[row.insurance_journal] = payment_map.get(row.insurance_journal, 0) + flt(row.paid)
#     for row in payments_pe:
#         payment_map[row.insurance_journal] = payment_map.get(row.insurance_journal, 0) + flt(row.paid)

#     return payment_map


# # ----------------------------------------
# # 3. Columns
# # ----------------------------------------
# def get_detailed_columns():
#     return [
#         {"label": _("Insurance Company"), "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
#         {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
#         {"label": _("Insurance Journal"), "fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "width": 150},
#         {"label": _("Insurance Covered (Debit)"), "fieldname": "insurance_covered", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Returned (Credit)"), "fieldname": "insurance_returned", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Paid"), "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Outstanding"), "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
#     ]

# def get_summary_columns():
#     return [
#         {"label": _("Insurance Company"), "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
#         {"label": _("Hospital (Company)"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
#         {"label": _("Insurance Covered (Debit)"), "fieldname": "insurance_covered", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Returned (Credit)"), "fieldname": "insurance_returned", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Paid"), "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Outstanding"), "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
#     ]


# from frappe import _
# import frappe
# from frappe.utils import flt

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     detailed = filters.get("detailed")

#     insurance_data = get_insurance_journal_summary(filters)
#     frappe.errprint("DEBUG: insurance_data fetched from DB:")
#     for row in insurance_data:
#         frappe.errprint(row)

#     # Build journal -> customer map for correct payment filtering
#     journal_customer_map = {
#         row["journal_entry"]: frappe.db.get_value("Insurance Company", row["insurance_company"], "customer")
#         for row in insurance_data
#     }

#     payment_map = get_insurance_payment_map(filters, journal_customer_map)

#     results = []

#     if detailed:
#         for row in insurance_data:
#             journal = row.get("journal_entry")

#             row["insurance_covered"] = flt(row.get("insurance_covered") or 0)
#             row["insurance_returned"] = flt(row.get("insurance_returned") or 0)
#             row["insurance_paid"] = flt(payment_map.get(journal, 0))
#             row["insurance_outstanding"] = (
#                 row["insurance_covered"]
#                 - row["insurance_returned"]
#                 - row["insurance_paid"]
#             )
#             results.append(row)
#         return get_detailed_columns(), results

#     else:
#         # Summary: group by insurance company + hospital
#         summary = {}
#         for row in insurance_data:
#             journal = row.get("journal_entry")
#             key = (row.get("insurance_company"), row.get("company"))

#             if key not in summary:
#                 summary[key] = {
#                     "insurance_company": row.get("insurance_company"),
#                     "company": row.get("company"),
#                     "insurance_covered": 0,
#                     "insurance_returned": 0,
#                     "insurance_paid": 0,
#                     "total_invoices": 0
#                 }

#             summary[key]["insurance_covered"] += flt(row.get("insurance_covered") or 0)
#             summary[key]["insurance_returned"] += flt(row.get("insurance_returned") or 0)
#             summary[key]["insurance_paid"] += flt(payment_map.get(journal, 0))
#             summary[key]["total_invoices"] += 1  # <-- this counts journals per group

#         for row in summary.values():
#             row["insurance_outstanding"] = (
#                 row["insurance_covered"]
#                 - row["insurance_returned"]
#                 - row["insurance_paid"]
#             )
#             results.append(row)

#         return get_summary_columns(), results


# # ----------------------------------------
# # 1. Insurance Journal Summary
# # ----------------------------------------
# def get_insurance_journal_summary(filters):
#     conditions = ["je.docstatus = 1"]

#     if filters.get("from_date"):
#         conditions.append("je.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("je.posting_date <= %(to_date)s")
#     if filters.get("insurance_company"):
#         conditions.append("je.insurance_company = %(insurance_company)s")
#     if filters.get("patient"):
#         conditions.append("je.patient = %(patient)s")

#     query = """
#         SELECT
#             je.insurance_company AS insurance_company,
#             COUNT(je.name) AS total_invoices,
#             je.company AS company,
#             je.sales_invoice AS sales_invoice,
#             je.name AS journal_entry,
#             SUM(jea.debit) AS insurance_covered,
#             SUM(jea.credit) AS insurance_returned
#         FROM `tabJournal Entry` je
#         INNER JOIN `tabJournal Entry Account` jea ON jea.parent = je.name
#         WHERE {conditions}
#         AND jea.party = (
#             SELECT customer FROM `tabInsurance Company`
#             WHERE name = je.insurance_company LIMIT 1
#         )
#         GROUP BY je.name, je.sales_invoice, je.insurance_company, je.company
#         ORDER BY je.posting_date DESC
#     """.format(conditions=" AND ".join(conditions))

#     return frappe.db.sql(query, filters, as_dict=True)


# # ----------------------------------------
# # 2. Insurance Payments (JEA + PE)
# # ----------------------------------------
# def get_insurance_payment_map(filters, journal_customer_map):
#     payment_map = {}

#     # JEA-based payments
#     jea_query = """
#         SELECT
#             jea.reference_name AS insurance_journal,
#             jea.party,
#             SUM(jea.credit) AS paid
#         FROM `tabJournal Entry Account` jea
#         INNER JOIN `tabJournal Entry` je ON je.name = jea.parent
#         WHERE je.docstatus = 1
#         AND jea.reference_type = 'Journal Entry'
#         {date_conditions}
#         GROUP BY jea.reference_name, jea.party
#     """.format(date_conditions=get_date_conditions("je", filters))

#     jea_rows = frappe.db.sql(jea_query, filters, as_dict=True)

#     for row in jea_rows:
#         journal = row.insurance_journal
#         if not journal or journal not in journal_customer_map:
#             continue
#         if row.party == journal_customer_map[journal]:
#             payment_map[journal] = payment_map.get(journal, 0) + flt(row.paid)

#     # PE-based payments
#     pe_query = """
#         SELECT
#             per.reference_name AS insurance_journal,
#             pe.party,
#             SUM(per.allocated_amount) AS paid
#         FROM `tabPayment Entry Reference` per
#         INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
#         WHERE pe.docstatus = 1
#         {date_conditions}
#         GROUP BY per.reference_name, pe.party
#     """.format(date_conditions=get_date_conditions("pe", filters))

#     pe_rows = frappe.db.sql(pe_query, filters, as_dict=True)

#     for row in pe_rows:
#         journal = row.insurance_journal
#         if not journal or journal not in journal_customer_map:
#             continue
#         if row.party == journal_customer_map[journal]:
#             payment_map[journal] = payment_map.get(journal, 0) + flt(row.paid)

#     return payment_map


# def get_date_conditions(alias, filters):
#     conds = []
#     if filters.get("from_date"):
#         conds.append(f"{alias}.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conds.append(f"{alias}.posting_date <= %(to_date)s")
#     return "AND " + " AND ".join(conds) if conds else ""


# # ----------------------------------------
# # 3. Column Definitions
# # ----------------------------------------
# def get_detailed_columns():
#     return [
#         {"label": _("Insurance Company"), "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
#         {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
#         {"label": _("Insurance Journal"), "fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "width": 150},
#         {"label": _("Insurance Covered (Debit)"), "fieldname": "insurance_covered", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Returned (Credit)"), "fieldname": "insurance_returned", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Paid"), "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Outstanding"), "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
#     ]


# def get_summary_columns():
#     return [
#         {"label": _("Insurance Company"), "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
#         {"label": _("Hospital (Company)"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
#         {"label": _("Number of Invoices"), "fieldname": "total_invoices", "fieldtype": "Int", "width": 150},
#         {"label": _("Insurance Covered (Debit)"), "fieldname": "insurance_covered", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Returned (Credit)"), "fieldname": "insurance_returned", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Paid"), "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Outstanding"), "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
#     ]


from frappe import _
import frappe
from frappe.utils import flt

def execute(filters=None):
    if not filters:
        filters = {}

    detailed = filters.get("detailed")

    insurance_data = get_insurance_journal_summary(filters)

    journal_customer_map = {
        row["journal_entry"]: frappe.db.get_value("Insurance Company", row["insurance_company"], "customer")
        for row in insurance_data
    }

    payment_map = get_insurance_payment_map(filters, journal_customer_map)

    results = []

    if detailed:
        for row in insurance_data:
            journal = row.get("journal_entry")

            row["insurance_covered"] = flt(row.get("insurance_covered") or 0)
            row["insurance_returned"] = flt(row.get("insurance_returned") or 0)
            row["insurance_paid"] = flt(payment_map.get(journal, 0))
            row["insurance_outstanding"] = (
                row["insurance_covered"]
                - row["insurance_returned"]
                - row["insurance_paid"]
            )
            results.append(row)

        # ✅ Sort by patient ID
        results = sorted(results, key=lambda x: x.get("patient") or "")
        return get_detailed_columns(), results


    else:
        summary = {}
        for row in insurance_data:
            journal = row.get("journal_entry")
            key = (row.get("insurance_company"), row.get("company"))

            if key not in summary:
                summary[key] = {
                    "insurance_company": row.get("insurance_company"),
                    "company": row.get("company"),
                    "insurance_covered": 0,
                    "insurance_returned": 0,
                    "insurance_paid": 0,
                    "total_invoices": 0
                }

            summary[key]["insurance_covered"] += flt(row.get("insurance_covered") or 0)
            summary[key]["insurance_returned"] += flt(row.get("insurance_returned") or 0)
            summary[key]["insurance_paid"] += flt(payment_map.get(journal, 0))
            summary[key]["total_invoices"] += 1

        for row in summary.values():
            row["insurance_outstanding"] = (
                row["insurance_covered"]
                - row["insurance_returned"]
                - row["insurance_paid"]
            )
            results.append(row)

        return get_summary_columns(), results

# ----------------------------------------
# 1. Insurance Journal Summary
# ----------------------------------------
def get_insurance_journal_summary(filters):
    conditions = ["je.docstatus = 1"]

    if filters.get("from_date"):
        conditions.append("je.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("je.posting_date <= %(to_date)s")
    if filters.get("insurance_company"):
        conditions.append("je.insurance_company = %(insurance_company)s")
    if filters.get("patient"):
        conditions.append("je.patient = %(patient)s")

    query = """
        SELECT
            je.insurance_company AS insurance_company,
            je.company AS company,
            je.name AS journal_entry,
            je.sales_invoice AS sales_invoice,
            je.patient AS patient,
            p.patient_name AS patient_name,
            p.dob AS dob,
            si.policy_number AS policy_number,
            si.coverage_limits AS coverage_limits,
            si.grand_total AS total_invoiced,
            si.payable_amount AS patient_amount,
            je.posting_date AS invoice_date,
            SUM(jea.debit) AS insurance_covered,
            SUM(jea.credit) AS insurance_returned
        FROM `tabJournal Entry` je
        INNER JOIN `tabJournal Entry Account` jea ON jea.parent = je.name
        LEFT JOIN `tabSales Invoice` si ON si.name = je.sales_invoice
        LEFT JOIN `tabPatient` p ON p.name = je.patient
        WHERE {conditions}
        AND jea.party = (
            SELECT customer FROM `tabInsurance Company`
            WHERE name = je.insurance_company LIMIT 1
        )
        GROUP BY je.name
        ORDER BY je.posting_date DESC
    """.format(conditions=" AND ".join(conditions))

    return frappe.db.sql(query, filters, as_dict=True)

# ----------------------------------------
# 2. Insurance Payments (JEA + PE)
# ----------------------------------------
def get_insurance_payment_map(filters, journal_customer_map):
    payment_map = {}

    jea_query = """
        SELECT
            jea.reference_name AS insurance_journal,
            jea.party,
            SUM(jea.credit) AS paid
        FROM `tabJournal Entry Account` jea
        INNER JOIN `tabJournal Entry` je ON je.name = jea.parent
        WHERE je.docstatus = 1
        AND jea.reference_type = 'Journal Entry'
        {date_conditions}
        GROUP BY jea.reference_name, jea.party
    """.format(date_conditions=get_date_conditions("je", filters))

    jea_rows = frappe.db.sql(jea_query, filters, as_dict=True)

    for row in jea_rows:
        journal = row.insurance_journal
        if not journal or journal not in journal_customer_map:
            continue
        if row.party == journal_customer_map[journal]:
            payment_map[journal] = payment_map.get(journal, 0) + flt(row.paid)

    pe_query = """
        SELECT
            per.reference_name AS insurance_journal,
            pe.party,
            SUM(per.allocated_amount) AS paid
        FROM `tabPayment Entry Reference` per
        INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
        WHERE pe.docstatus = 1
        {date_conditions}
        GROUP BY per.reference_name, pe.party
    """.format(date_conditions=get_date_conditions("pe", filters))

    pe_rows = frappe.db.sql(pe_query, filters, as_dict=True)

    for row in pe_rows:
        journal = row.insurance_journal
        if not journal or journal not in journal_customer_map:
            continue
        if row.party == journal_customer_map[journal]:
            payment_map[journal] = payment_map.get(journal, 0) + flt(row.paid)

    return payment_map

def get_date_conditions(alias, filters):
    conds = []
    if filters.get("from_date"):
        conds.append(f"{alias}.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conds.append(f"{alias}.posting_date <= %(to_date)s")
    return "AND " + " AND ".join(conds) if conds else ""

# ----------------------------------------
# 3. Column Definitions
# ----------------------------------------
def get_detailed_columns():
    return [
        {"label": _("Insurance Company"), "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
        {"label": _("Hospital Name"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": _("Patient"), "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 120},
        {"label": _("Patient Name"), "fieldname": "patient_name", "fieldtype": "Data", "width": 180},
        {"label": _("Date of Birth"), "fieldname": "dob", "fieldtype": "Date", "width": 120},
        {"label": _("Policy Number"), "fieldname": "policy_number", "fieldtype": "Data", "width": 150},
        {"label": _("Date of Service"), "fieldname": "invoice_date", "fieldtype": "Date", "width": 130},
        {"label": _("Coverage Limit (%)"), "fieldname": "coverage_limits", "fieldtype": "Float", "width": 120},
        {"label": _("Invoice Number"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Journal Number"), "fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "width": 150},
        {"label": _("Invoice Amount"), "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 130},
        {"label": _("Patient Amount"), "fieldname": "patient_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Insurance Covered Amount"), "fieldname": "insurance_covered", "fieldtype": "Currency", "width": 150},
        {"label": _("Insurance Returned Amount"), "fieldname": "insurance_returned", "fieldtype": "Currency", "width": 150},
        {"label": _("Insurance Paid"), "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 130},
        {"label": _("Insurance Outstanding"), "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
    ]

def get_summary_columns():
    return [
        {"label": _("Insurance Company"), "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
        {"label": _("Hospital (Company)"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": _("Number of Invoices"), "fieldname": "total_invoices", "fieldtype": "Int", "width": 150},
        {"label": _("Insurance Covered (Debit)"), "fieldname": "insurance_covered", "fieldtype": "Currency", "width": 150},
        {"label": _("Insurance Returned (Credit)"), "fieldname": "insurance_returned", "fieldtype": "Currency", "width": 150},
        {"label": _("Insurance Paid"), "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
        {"label": _("Insurance Outstanding"), "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
    ]
