# rasiin_healthcare_insurance/utils.py

import frappe
from frappe import _

def handle_linked_journal_entries(reference_invoice, reverse=False):
    """
    Cancel or reverse linked Journal Entries based on the provided reference invoice.
    :param reference_invoice: The name of the Sales Invoice for which Journal Entries are linked.
    :param reverse: If True, reverse the Journal Entries. If False, cancel them.
    """
    linked_journal_entries = frappe.get_all('Journal Entry', filters={
        'reference_invoice': reference_invoice,
        'docstatus': 1
    })

    if linked_journal_entries:
        for journal_entry in linked_journal_entries:
            je_doc = frappe.get_doc("Journal Entry", journal_entry.name)
            if je_doc.docstatus == 1:
                if reverse:
                    # Reverse the journal entry
                    reverse_journal_entry(je_doc, reference_invoice)
                else:
                    # Cancel the journal entry
                    je_doc.cancel()
                    frappe.msgprint(_("Journal Entry {0} has been canceled.").format(je_doc.name))
    else:
        frappe.msgprint(_("No linked Journal Entries found for {0}.").format(reference_invoice))


def reverse_journal_entry(je_doc, reference_invoice):
    """
    Reverse a Journal Entry by swapping the debit and credit accounts.
    :param je_doc: The Journal Entry document to be reversed.
    :param reference_invoice: The reference invoice associated with the Journal Entry.
    """
    reverse_entries = []
    for account in je_doc.accounts:
        reverse_entries.append({
            "account": account.account,
            "party_type": account.party_type,
            "party": account.party,
            "debit_in_account_currency": account.credit_in_account_currency,  # Swap debit and credit
            "credit_in_account_currency": account.debit_in_account_currency,  # Swap debit and credit
            "cost_center": account.cost_center,
        })

    reverse_journal_entry = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Journal Entry",
        "company": je_doc.company,
        "posting_date": frappe.utils.nowdate(),
        "accounts": reverse_entries,
        "user_remark": _("Reversal of Journal Entry {0} for Sales Invoice {1}.").format(je_doc.name, reference_invoice),
        "reference_invoice": reference_invoice,
    })

    reverse_journal_entry.insert(ignore_permissions=True)
    reverse_journal_entry.submit()

    frappe.msgprint(_("Reversal Journal Entry {0} created for linked Journal Entry {1}.").format(reverse_journal_entry.name, je_doc.name))
