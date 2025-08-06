# from frappe import _
# import frappe
# from frappe.utils import flt

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     detailed = filters.get("detailed")

#     insurance_data = get_insurance_journal_summary(filters)

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

#         # ✅ Sort by patient ID
#         results = sorted(results, key=lambda x: x.get("patient") or "")
#         return get_detailed_columns(), results


#     else:
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
#             summary[key]["total_invoices"] += 1

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
#             je.company AS company,
#             je.name AS journal_entry,
#             je.reference_invoice AS reference_invoice,
#             je.patient AS patient,
#             p.patient_name AS patient_name,
#             p.dob AS dob,
#             si.policy_number AS policy_number,
#             si.coverage_limits AS coverage_limits,
#             si.grand_total AS total_invoiced,
#             si.payable_amount AS patient_amount,
#             je.posting_date AS invoice_date,
#             SUM(jea.debit) AS insurance_covered,
#             SUM(jea.credit) AS insurance_returned
#         FROM `tabJournal Entry` je
#         INNER JOIN `tabJournal Entry Account` jea ON jea.parent = je.name
#         LEFT JOIN `tabSales Invoice` si ON si.name = je.reference_invoice
#         LEFT JOIN `tabPatient` p ON p.name = je.patient
#         WHERE {conditions}
#         AND jea.party = (
#             SELECT customer FROM `tabInsurance Company`
#             WHERE name = je.insurance_company LIMIT 1
#         )
#         GROUP BY je.name
#         ORDER BY je.posting_date DESC
#     """.format(conditions=" AND ".join(conditions))

#     return frappe.db.sql(query, filters, as_dict=True)

# # ----------------------------------------
# # 2. Insurance Payments (JEA + PE)
# # ----------------------------------------
# def get_insurance_payment_map(filters, journal_customer_map):
#     payment_map = {}

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
#         {"label": _("Hospital Name"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
#         {"label": _("Patient"), "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 120},
#         {"label": _("Patient Name"), "fieldname": "patient_name", "fieldtype": "Data", "width": 180},
#         {"label": _("Date of Birth"), "fieldname": "dob", "fieldtype": "Date", "width": 120},
#         {"label": _("Policy Number"), "fieldname": "policy_number", "fieldtype": "Data", "width": 150},
#         {"label": _("Date of Service"), "fieldname": "invoice_date", "fieldtype": "Date", "width": 130},
#         {"label": _("Coverage Limit (%)"), "fieldname": "coverage_limits", "fieldtype": "Float", "width": 120},
#         {"label": _("Invoice Number"), "fieldname": "reference_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
#         {"label": _("Journal Number"), "fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "width": 150},
#         {"label": _("Invoice Amount"), "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 130},
#         {"label": _("Patient Amount"), "fieldname": "patient_amount", "fieldtype": "Currency", "width": 130},
#         {"label": _("Insurance Covered Amount"), "fieldname": "insurance_covered", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Returned Amount"), "fieldname": "insurance_returned", "fieldtype": "Currency", "width": 150},
#         {"label": _("Insurance Paid"), "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 130},
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

# --------------------------------------------------
# Main Report Execution
# --------------------------------------------------
def execute(filters=None):
    if not filters:
        filters = {}

    detailed = filters.get("detailed")

    insurance_data = get_insurance_journal_summary(filters)
    journal_customer_map = get_all_journal_customer_map()
    payment_map = get_insurance_payment_map(filters, journal_customer_map)

    results = []

    # ------------------------------------------
    # DETAILED VIEW
    # ------------------------------------------
    if detailed:
        included_journals = {row["journal_entry"] for row in insurance_data}

        # Add extra journals paid during filter range but not in insurance_data
        extra_journals = [j for j in payment_map if j not in included_journals]

        if extra_journals:
            additional_data = frappe.db.sql("""
                SELECT
                    je.insurance_company AS insurance_company,
                    je.company AS company,
                    je.name AS journal_entry,
                    je.reference_invoice AS reference_invoice,
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
                LEFT JOIN `tabSales Invoice` si ON si.name = je.reference_invoice
                LEFT JOIN `tabPatient` p ON p.name = je.patient
                WHERE je.name IN %(extra_journals)s
                AND je.docstatus = 1
                AND je.reference_invoice IS NOT NULL
                AND jea.party = (
                    SELECT customer FROM `tabInsurance Company`
                    WHERE name = je.insurance_company LIMIT 1
                )
                GROUP BY je.name
            """, {"extra_journals": extra_journals}, as_dict=True)

            for row in additional_data:
                if filters.get("insurance_company") and row["insurance_company"] != filters["insurance_company"]:
                    continue
                if filters.get("company") and row["company"] != filters["company"]:
                    continue
                if filters.get("patient") and row["patient"] != filters["patient"]:
                    continue
                
                # ✅ FIX: prevent double-counting coverage from past journals
                row["insurance_covered"] = 0
                row["insurance_returned"] = 0
                
                insurance_data.append(row)

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

        results = sorted(results, key=lambda x: x.get("patient") or "")
        return get_detailed_columns(), results

    # ------------------------------------------
    # SUMMARY VIEW
    # ------------------------------------------
    else:
        summary = {}
        for row in insurance_data:
            journal = row.get("journal_entry")
            patient = row.get("patient")
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

        used_journals = {row.get("journal_entry") for row in insurance_data}

        for journal, paid_amount in payment_map.items():
            if journal not in used_journals:
                company, insurance_company, patient, patient_name = frappe.db.get_value(
                    "Journal Entry", journal, ["company", "insurance_company", "patient", "patient_name"]
                )
                
                if filters.get("patient") and patient != filters["patient"]:
                    continue
                patient_name = frappe.db.get_value("Patient", patient_name, "patient_name") or ""

                if filters.get("company") and company != filters["company"]:
                    continue
                if filters.get("insurance_company") and insurance_company != filters["insurance_company"]:
                    continue

                key = (insurance_company, company)
                if key not in summary:
                    summary[key] = {
                        "patient_name": patient_name,
                        "insurance_company": insurance_company,
                        "company": company,
                        "insurance_covered": 0,
                        "insurance_returned": 0,
                        "insurance_paid": 0,
                        "total_invoices": 0
                    }

                summary[key]["insurance_paid"] += flt(paid_amount)

        for row in summary.values():
            row["insurance_outstanding"] = (
                row["insurance_covered"]
                - row["insurance_returned"]
                - row["insurance_paid"]
            )
            results.append(row)

        return get_summary_columns(), results

# --------------------------------------------------
# Supporting Query Functions
# --------------------------------------------------
def get_insurance_journal_summary(filters):
    conditions = ["je.docstatus = 1", "je.reference_invoice IS NOT NULL"]

    if filters.get("from_date"):
        conditions.append("je.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("je.posting_date <= %(to_date)s")
    if filters.get("insurance_company"):
        conditions.append("je.insurance_company = %(insurance_company)s")
    if filters.get("patient"):
        conditions.append("je.patient = %(patient)s")
    if filters.get("company"):
        conditions.append("je.company = %(company)s")

    query = """
        SELECT
            je.insurance_company AS insurance_company,
            je.company AS company,
            je.name AS journal_entry,
            je.reference_invoice AS reference_invoice,
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
        LEFT JOIN `tabSales Invoice` si ON si.name = je.reference_invoice
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


def get_insurance_payment_map(filters, journal_customer_map):
    payment_map = {}
    

    # -- Journal Entry Payments --
    jea_query = """
        SELECT
            jea.reference_name AS insurance_journal,
            je.posting_date AS payment_date,
            jea.party,
            (SELECT patient FROM `tabJournal Entry`
             WHERE name = jea.reference_name) AS patient,
            SUM(jea.credit) AS paid
        FROM `tabJournal Entry Account` jea
        INNER JOIN `tabJournal Entry` je ON je.name = jea.parent
        WHERE je.docstatus = 1
        AND jea.reference_type = 'Journal Entry'
        {date_conditions}
        GROUP BY jea.reference_name, jea.party, je.posting_date
    """.format(date_conditions=get_date_conditions("je", filters))

    jea_rows = frappe.db.sql(jea_query, filters, as_dict=True)
    for row in jea_rows:
        journal = row.insurance_journal
        if journal and journal in journal_customer_map and row.party == journal_customer_map[journal] and (not filters.get("patient") or row.patient == filters["patient"]):
            payment_map[journal] = payment_map.get(journal, 0) + flt(row.paid)

    # -- Payment Entry Payments --
    pe_query = """
        SELECT
            per.reference_name AS insurance_journal,
            pe.posting_date AS payment_date,
            pe.party,
            (SELECT je.patient FROM `tabJournal Entry` je
                WHERE je.name = per.reference_name) AS patient,
            SUM(per.allocated_amount) AS paid
        FROM `tabPayment Entry Reference` per
        INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
        WHERE pe.docstatus = 1
        {date_conditions}
        GROUP BY per.reference_name, pe.party, pe.posting_date
    """.format(date_conditions=get_date_conditions("pe", filters))

    pe_rows = frappe.db.sql(pe_query, filters, as_dict=True)
    for row in pe_rows:
        journal = row.insurance_journal
        if journal and journal in journal_customer_map and row.party == journal_customer_map[journal] and (not filters.get("patient") or row.patient == filters["patient"]):
            payment_map[journal] = payment_map.get(journal, 0) + flt(row.paid)

    return payment_map


def get_all_journal_customer_map():
    query = """
        SELECT
            je.name AS journal_entry,
            ic.customer AS customer
        FROM `tabJournal Entry` je
        JOIN `tabInsurance Company` ic ON je.insurance_company = ic.name
        WHERE je.docstatus = 1
    """
    rows = frappe.db.sql(query, as_dict=True)
    return {row.journal_entry: row.customer for row in rows}


def get_date_conditions(alias, filters):
    conds = []
    if filters.get("from_date"):
        conds.append(f"{alias}.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conds.append(f"{alias}.posting_date <= %(to_date)s")
    return "AND " + " AND ".join(conds) if conds else ""

# --------------------------------------------------
# Column Definitions
# --------------------------------------------------
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
        {"label": _("Invoice Number"), "fieldname": "reference_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
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
