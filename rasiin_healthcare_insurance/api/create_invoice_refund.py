import frappe
from frappe import _
from erpnext.stock.get_item_details import get_pos_profile

@frappe.whitelist()
def create_inv_refund(doc_name, dt, que, is_sales_return=False, is_credit=False):
    cash_sales = frappe.get_doc(dt, doc_name)
    pos_profile = get_pos_profile(cash_sales.company)
    mode_of_payment = frappe.db.get_value('POS Payment Method', {"parent": pos_profile.name}, 'mode_of_payment')

    # Ensure refund is valid
    if cash_sales.paid_amount <= 0:
        frappe.throw(_("Refund cannot be processed because no payment has been made."))

    # Check if the patient is insured
    is_insured = bool(cash_sales.get("insurance_company"))

    # Prepare the items for the refund
    items = []
    for item in cash_sales.items:
        qty = item.qty if not is_sales_return else float(item.qty) * (-1)
        items.append({
            "item_code": item.item_code,
            "rate": item.rate,
            "qty": qty
        })

    # Calculate the refund amount (only refund what the patient has paid)
    patient_paid_amount = cash_sales.paid_amount if not is_sales_return else cash_sales.paid_amount * (-1)

    payments = []
    if is_sales_return:
        payments.append({
            "mode_of_payment": mode_of_payment,
            "amount": patient_paid_amount
        })

    # Check if there is an outstanding amount before enabling write-off
    write_off_outstanding = 0
    if cash_sales.outstanding_amount > 0:
        write_off_outstanding = 1  # Enable write-off only if outstanding balance exists

    # Create a new Sales Invoice for the return
    sales_doc = frappe.get_doc({
        "doctype": "Sales Invoice",
        "is_return": 1,
        "posting_date": cash_sales.posting_date,
        "customer": cash_sales.customer,
        "patient": cash_sales.patient,
        "is_pos": 1,
        "write_off_outstanding_amount_automatically": write_off_outstanding,  # Write-off based on condition
        "return_against": cash_sales.name,     # Link to original sales invoice
        "payments": payments,
        "items": items,
    })
    
    frappe.errprint(sales_doc)

    sales_doc.insert(ignore_permissions=True)
    sales_doc.submit()

    # Mark the Que status as 'Refunded'
    frappe.db.set_value('Que', que, 'status', 'Refunded')

    # Handle Journal Entry Reversal if there are linked Journal Entries
    if is_insured:
        handle_journal_entry_refund(cash_sales)

    return sales_doc


def handle_journal_entry_refund(cash_sales):
    # Fetch the linked journal entries
    linked_journal_entries = frappe.get_all('Journal Entry', filters={
        'reference_invoice': cash_sales.name,
        'docstatus': 1  # Only get submitted journal entries
    })

    if linked_journal_entries:
        for journal_entry in linked_journal_entries:
            je_doc = frappe.get_doc("Journal Entry", journal_entry.name)
            
            if je_doc.docstatus == 1:
                # Prepare reversal entries, making debit and credit values negative
                reverse_entries = []
                for account in je_doc.accounts:
                    reverse_entries.append({
                        "account": account.account,
                        "party_type": account.party_type,
                        "party": account.party,
                        "debit_in_account_currency": -1 * account.debit_in_account_currency,
                        "credit_in_account_currency": -1 * account.credit_in_account_currency,
                        "cost_center": account.cost_center,
                        "reference_type": account.reference_type,
                        "reference_name": account.reference_name,
                    })

                # Create new reversal Journal Entry with negative values
                reverse_journal_entry = frappe.get_doc({
                    "doctype": "Journal Entry",
                    "voucher_type": "Journal Entry",
                    "company": je_doc.company,
                    "posting_date": frappe.utils.nowdate(),
                    "accounts": reverse_entries,
                    "user_remark": _("Reversal of Journal Entry {0} for Sales Invoice {1}.").format(je_doc.name, cash_sales.name),
                    "reference_invoice": cash_sales.name,
                })

                # Insert and submit the reversal journal entry
                reverse_journal_entry.insert(ignore_permissions=True)
                reverse_journal_entry.submit()

                frappe.msgprint(_("Reversal Journal Entry {0} created for linked Journal Entry {1}.").format(reverse_journal_entry.name, je_doc.name))
    else:
        frappe.msgprint(_("No linked Journal Entry found for Sales Invoice {0}.").format(cash_sales.name))


def handle_journal_entry_refund_invoice(cash_sales, method=None):
    
    is_return = cash_sales.is_return
    
    if is_return and cash_sales.return_against:
        # Fetch the linked journal entries
        linked_journal_entries = frappe.get_all('Journal Entry', filters={
            'reference_invoice': cash_sales.return_against,
            'docstatus': 1  # Only get submitted journal entries
        })

        if linked_journal_entries:
            for journal_entry in linked_journal_entries:
                je_doc = frappe.get_doc("Journal Entry", journal_entry.name)
                
                if je_doc.docstatus == 1:
                    # Prepare reversal entries, making debit and credit values negative
                    reverse_entries = []
                    for account in je_doc.accounts:
                        reverse_entries.append({
                            "account": account.account,
                            "party_type": account.party_type,
                            "party": account.party,
                            "debit_in_account_currency": -1 * account.debit_in_account_currency,
                            "credit_in_account_currency": -1 * account.credit_in_account_currency,
                            "cost_center": account.cost_center,
                            "reference_type": account.reference_type,
                            "reference_name": account.reference_name,
                        })

                    # Create new reversal Journal Entry with negative values
                    reverse_journal_entry = frappe.get_doc({
                        "doctype": "Journal Entry",
                        "voucher_type": "Journal Entry",
                        "company": je_doc.company,
                        "posting_date": frappe.utils.nowdate(),
                        "accounts": reverse_entries,
                        "user_remark": _("Reversal of Journal Entry {0} for Sales Invoice {1}.").format(je_doc.name, cash_sales.name),
                        "reference_invoice": cash_sales.name,
                    })

                    # Insert and submit the reversal journal entry
                    reverse_journal_entry.insert(ignore_permissions=True)
                    reverse_journal_entry.submit()

                    frappe.msgprint(_("Reversal Journal Entry {0} created for linked Journal Entry {1}.").format(reverse_journal_entry.name, je_doc.name))
        else:
            frappe.msgprint(_("No linked Journal Entry found for Sales Invoice {0}.").format(cash_sales.name))


# def handle_journal_entry_refund(cash_sales):
#     # Fetch the linked journal entries
#     linked_journal_entries = frappe.get_all('Journal Entry', filters={
#         'reference_invoice': cash_sales.name,
#         'docstatus': 1  # Only get submitted journal entries
#     })

#     if linked_journal_entries:
#         for journal_entry in linked_journal_entries:
#             je_doc = frappe.get_doc("Journal Entry", journal_entry.name)
            
#             if je_doc.docstatus == 1:
#                 # Instead of reversing the journal entry, apply a write-off or adjustment
#                 reverse_entries = []
#                 for account in je_doc.accounts:
#                     reverse_entries.append({
#                         "account": account.account,
#                         "party_type": account.party_type,
#                         "party": account.party,
#                         "debit_in_account_currency": account.credit_in_account_currency,  # Swap debit and credit
#                         "credit_in_account_currency": account.debit_in_account_currency,  # Swap debit and credit
#                         "cost_center": account.cost_center,
#                     })

#                 # Create new reversal Journal Entry
#                 reverse_journal_entry = frappe.get_doc({
#                     "doctype": "Journal Entry",
#                     "voucher_type": "Journal Entry",
#                     "company": je_doc.company,
#                     "posting_date": frappe.utils.nowdate(),
#                     "accounts": reverse_entries,
#                     "user_remark": _("Reversal of Journal Entry {0} for Sales Invoice {1}.").format(je_doc.name, cash_sales.name),
#                     "reference_invoice": cash_sales.name,
#                 })

#                 reverse_journal_entry.insert(ignore_permissions=True)
#                 reverse_journal_entry.submit()

#                 frappe.msgprint(_("Reversal Journal Entry {0} created for linked Journal Entry {1}.").format(reverse_journal_entry.name, je_doc.name))


# def handle_journal_entry_refund(cash_sales):
#     linked_journal_entries = frappe.get_all('Journal Entry', filters={
#         'reference_invoice': cash_sales.name,
#         'docstatus': 1  # Only get submitted journal entries
#     })

#     if linked_journal_entries:
#         for journal_entry in linked_journal_entries:
#             je_doc = frappe.get_doc("Journal Entry", journal_entry.name)
#             if je_doc.docstatus == 1:
#                 je_doc.cancel()
#                 frappe.msgprint(_("Linked Journal Entry {0} has been canceled.").format(je_doc.name))
