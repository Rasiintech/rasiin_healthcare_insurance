from erpnext.stock.get_item_details import get_pos_profile
import frappe
from frappe import _

@frappe.whitelist()
def make_cancel(**args):
    # Set the Que status to 'Canceled'
    frappe.db.set_value('Que', args.get("que"), 'status', 'Canceled')

    # Get the Sales Invoice
    sales_invoice = frappe.get_doc("Sales Invoice", args.get("sales_invoice"))

    # Step 1: Check for any linked Journal Entries
    linked_journal_entries = frappe.get_all('Journal Entry',
                                            filters={
                                                'reference_invoice': args.get("sales_invoice"),
                                                'docstatus': 1  # Only get submitted journal entries
                                            })

    # Step 2: Cancel any linked Journal Entries if found
    if linked_journal_entries:
        for journal_entry in linked_journal_entries:
            je_doc = frappe.get_doc("Journal Entry", journal_entry.name)
            if je_doc.docstatus == 1:
                je_doc.cancel()
                # frappe.msgprint(_("Journal Entry {0} has been canceled.").format(je_doc.name))
    else:
        # frappe.msgprint(_("No linked Journal Entries found for the Sales Invoice."))
        pass

    # Step 3: Cancel the Sales Invoice
    if sales_invoice.docstatus == 1:
        sales_invoice.cancel()
        # frappe.msgprint(_("Sales Invoice {0} has been canceled.").format(sales_invoice.name))
        pass

    # Step 4: Cancel the Sales Order if it exists
    sales_order_id = args.get("sales_order")
    if sales_order_id:
        sales_order = frappe.get_doc("Sales Order", sales_order_id)
        if sales_order.docstatus == 1:
            sales_order.cancel()
            # frappe.msgprint(_("Sales Order {0} has been canceled.").format(sales_order.name))
    else:
        # frappe.msgprint(_("No Sales Order found for cancellation."))
        pass

    # Step 5: Cancel the Fee Validity if it exists
    fee = args.get("fee")
    if fee:
        try:
            fee_doc = frappe.get_doc("Fee Validity", fee)
            if fee_doc.docstatus == 1:
                fee_doc.cancel()
                # frappe.msgprint(_("Fee Validity {0} has been canceled.").format(fee_doc.name))
        except frappe.DoesNotExistError:
            # frappe.msgprint(_("Fee Validity not found for ID: {0}").format(fee))
            pass
    else:
        # frappe.msgprint(_("No Fee Validity found for cancellation."))
        pass

    # frappe.msgprint(_("Cancellation process completed successfully."))



@frappe.whitelist()
def cancel_journal(doc, method=None):
    """
    This function cancels linked Journal Entries for the provided Sales Invoice.
    """
    
    # Step 1: Check if there's any Journal Entry linked to this Sales Invoice via "against_sales_invoice" field.
    # Ensure the field is correctly used in your system, or change it based on your setup.
    linked_journal_entries = frappe.get_all('Journal Entry', filters={
        'reference_invoice': doc.name,  # Update the link field to match your use case
        'docstatus': 1  # Only get submitted journal entries
    })
    
    # Step 2: Cancel any linked Journal Entries if found
    if linked_journal_entries:
        for journal_entry in linked_journal_entries:
            je_doc = frappe.get_doc("Journal Entry", journal_entry.name)
            if je_doc.docstatus == 1:
                je_doc.cancel()
                # frappe.msgprint(_("Journal Entry {0} has been successfully canceled.").format(je_doc.name))
    else:
        # frappe.msgprint(_("No linked Journal Entries found for Sales Invoice {0}.").format(doc.name))
        pass