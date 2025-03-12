import frappe
from frappe import _
# from erpnext.stock.get_item_details import get_pos_profile

@frappe.whitelist()
def create_journal_entry_for_insurance(doc, method=None):
    sales_invoice = frappe.get_doc("Sales Invoice", doc.name)
    his_settings = frappe.get_doc("HIS Settings", "HIS Settings")
    insurance_account = ""
    debtor_account = ""
    if his_settings.insurance_receivable_account:
        insurance_account = his_settings.insurance_receivable_account
    if his_settings.debtors_account:
        debtor_account = his_settings.debtors_account
    # Ensure the Sales Invoice has an insurance portion and outstanding amount
    if sales_invoice.insurance_coverage_amount > 0 and sales_invoice.outstanding_amount > 0:
        # Check if a journal entry has already been created for this insurance portion
        existing_journal_entry = frappe.db.exists({
            "doctype": "Journal Entry",
            "reference_invoice": sales_invoice.name
        })

        if not existing_journal_entry:
            abbr = frappe.db.get_value("Company", sales_invoice.company, "abbr")
            patient_name = frappe.db.get_value('Patient', sales_invoice.patient, 'customer')
            insurance_name = frappe.db.get_value('Insurance Company', sales_invoice.insurance_company, 'customer')
            # frappe.errprint(patient_name)
            # frappe.errprint(insurance_name)
            # frappe.throw("STOP")

            # Accounts to be used in the Journal Entry
            insurance_receivable_account = frappe.db.get_value("Party Account", {"parent": insurance_name}, "account") or insurance_account
            patient_receivable_account = frappe.db.get_value("Party Account", {"parent": patient_name}, "account") or debtor_account

            # Ensure positive insurance coverage amount before proceeding
            if sales_invoice.insurance_coverage_amount <= 0:
                frappe.throw(_("Insurance coverage amount must be greater than zero."))

            accounts = [
                {
                    "account": insurance_receivable_account,
                    "party_type": "Customer",
                    "party": insurance_name,
                    "debit_in_account_currency": sales_invoice.insurance_coverage_amount,
                    "cost_center": sales_invoice.cost_center,
                },
                {
                    "account": patient_receivable_account,
                    "party_type": "Customer",
                    "party": patient_name,
                    "credit_in_account_currency": sales_invoice.insurance_coverage_amount,
                    "cost_center": sales_invoice.cost_center,
                },
            ]

            try:
                # Create the Journal Entry
                journal_entry = frappe.get_doc({
                    "doctype": "Journal Entry",
                    "voucher_type": "Journal Entry",
                    "company": sales_invoice.company,
                    "posting_date": sales_invoice.posting_date,
                    "accounts": accounts,
                    "user_remark": _("Transfer from Patient {0} to Insurance {1} for Sales Invoice {2}.").format(patient_name, insurance_name, sales_invoice.name),
                    "reference_invoice": sales_invoice.name,
                    "patient": sales_invoice.patient,
                    "patient_name": sales_invoice.patient_name,
                    "insurance": sales_invoice.insurance,
                    
                })

                journal_entry.insert(ignore_permissions=True)
                journal_entry.submit()
                frappe.db.set_value('Sales Invoice', sales_invoice.name, 'reference_journal', journal_entry.name)
                # frappe.msgprint(_("Journal Entry {0} created for insurance portion.").format(journal_entry.name))
                return journal_entry.name
            except Exception as e:
                frappe.log_error(f"Failed to create Journal Entry for Sales Invoice {sales_invoice.name}: {str(e)}", "Insurance Journal Entry Error")
                frappe.throw(_("An error occurred while creating the Journal Entry. Please try again or contact support."))
        else:
            # frappe.msgprint(_("A Journal Entry for the insurance portion has already been created."))
            pass
        
@frappe.whitelist()
def update_patient_amount(doc, method=None):
    sales_invoice = frappe.get_doc("Sales Invoice", doc.name)
    # frappe.errprint(sales_invoice.paid_amount)
    # frappe.throw("Stop!")
    if sales_invoice.paid_amount:
        frappe.db.set_value('Sales Invoice', sales_invoice.name, 'patient_paid', sales_invoice.paid_amount)
        
    return sales_invoice.reference_journal
