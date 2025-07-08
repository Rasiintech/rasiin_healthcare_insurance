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
            key = (row.get("patient_name"), row.get("insurance_company"))

            if key not in summary:
                summary[key] = {
                    "patient_name": row.get("patient_name"),
                    "insurance_company": row.get("insurance_company"),
                    "coverage_limits": row.get("coverage_limits"),
                    "total_invoices": 0,
                    "total_invoiced": 0,
                    "total_insurance_amount": 0,
                    "total_returned": 0,
                    "total_paid": 0,
                }

            summary[key]["total_invoices"] += 1
            summary[key]["total_invoiced"] += flt(row.get("total_invoiced") or 0)
            summary[key]["total_insurance_amount"] += flt(row.get("insurance_covered") or 0)
            summary[key]["total_returned"] += flt(row.get("insurance_returned") or 0)
            summary[key]["total_paid"] += flt(payment_map.get(journal, 0))

        for row in summary.values():
            row["insurance_outstanding"] = (
                row["total_insurance_amount"] - row["total_returned"] - row["total_paid"]
            )
            results.append(row)

        return get_summary_columns(), results

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
            si.coverage_limits AS coverage_limits,
            si.grand_total AS total_invoiced,
            SUM(CASE WHEN jea.debit > 0 THEN jea.debit ELSE 0 END) AS insurance_covered,
            SUM(CASE WHEN jea.credit > 0 THEN jea.credit ELSE 0 END) AS insurance_returned,
            je.posting_date AS invoice_date
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
    """.format(conditions=" AND ".join(conditions))

    return frappe.db.sql(query, filters, as_dict=True)

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

def get_detailed_columns():
    return [
        {"label": "Invoice Number", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 200},
        {"label": "Invoice Date", "fieldname": "invoice_date", "fieldtype": "Date", "width": 150},
        {"label": "Patient Name", "fieldname": "patient_name", "fieldtype": "Data", "width": 200},
        {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
        {"label": "Coverage Limit", "fieldname": "coverage_limits", "fieldtype": "Percentage", "width": 150},
        {"label": "Total Invoiced Amount", "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 150},
        {"label": "Insurance Amount", "fieldname": "insurance_covered", "fieldtype": "Currency", "width": 150},
        {"label": "Insurance Returned", "fieldname": "insurance_returned", "fieldtype": "Currency", "width": 150},
        {"label": "Insurance Paid", "fieldname": "insurance_paid", "fieldtype": "Currency", "width": 150},
        {"label": "Insurance Outstanding", "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
    ]

def get_summary_columns():
    return [
        {"label": "Patient Name", "fieldname": "patient_name", "fieldtype": "Data", "width": 200},
        {"label": "Insurance Company", "fieldname": "insurance_company", "fieldtype": "Link", "options": "Insurance Company", "width": 200},
        {"label": "Total Invoices", "fieldname": "total_invoices", "fieldtype": "Int", "width": 120},
        {"label": "Total Invoiced Amount", "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 150},
        {"label": "Total Insurance Amount", "fieldname": "total_insurance_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Total Insurance Returned", "fieldname": "total_returned", "fieldtype": "Currency", "width": 150},
        {"label": "Total Insurance Paid Amount", "fieldname": "total_paid", "fieldtype": "Currency", "width": 150},
        {"label": "Total Insurance Outstanding", "fieldname": "insurance_outstanding", "fieldtype": "Currency", "width": 150},
    ]