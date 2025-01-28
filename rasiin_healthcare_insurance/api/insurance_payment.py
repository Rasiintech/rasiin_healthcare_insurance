import frappe

@frappe.whitelist()
def update_sales_invoice_on_payment(doc, method=None):
    try:
        # frappe.throw("update_sales_invoice_on_payment")
        frappe.errprint(f"Processing Payment Entry: {doc.name}")
        payment = frappe.get_doc("Payment Entry", doc.name)
        
        # Loop through references in the Payment Entry
        for reference in payment.references:
            allocated_amount = reference.allocated_amount  # Correctly get allocated amount from Payment Entry Reference

            if reference.reference_doctype == "Sales Invoice":
                update_sales_invoice(reference.reference_name, allocated_amount, "patient_paid")
            elif reference.reference_doctype == "Journal Entry":
                update_sales_invoice_via_journal_entry(reference.reference_name, allocated_amount)
                
    except Exception as e:
        frappe.errprint(f"Error in updating Sales Invoice: {str(e)}")
        frappe.throw(f"Error in updating Sales Invoice: {str(e)}")

def update_sales_invoice(reference, allocated_amount, payment_type):
    sales_invoice_id = reference
    
    if not sales_invoice_id:
        frappe.errprint(f"No Sales Invoice ID provided for {payment_type} payment.")
        return
    
    invoice = frappe.get_doc("Sales Invoice", sales_invoice_id)

    frappe.errprint(f"This is the Sales Invoice Outstanding Amount: {invoice.outstanding_amount}")
    
    # frappe.throw("STOP HERE!")

    # Get the correct field to update
    amount_field = "patient_paid" if payment_type == "patient_paid" else "insurance_paid"

    # Update the outstanding amount and status based on new payment
    update_outstanding_and_status(invoice, allocated_amount, amount_field)
    # invoice.reload()
    # frappe.msgprint(f"Sales Invoice {invoice.name} updated. Outstanding: {invoice.outstanding_amount}")
    
def update_sales_invoice_via_journal_entry(reference, allocated_amount):
    # Fetch the Journal Entry document using the reference name
    journal_entry = frappe.get_doc("Journal Entry", reference)
    # Get the Sales Invoice linked to this Journal Entry
    sales_invoice_id = journal_entry.reference_invoice
    
    frappe.errprint(f"This is the Sales Invoice in the Journal Entry: {sales_invoice_id}")
    
    if not sales_invoice_id:
        frappe.errprint(f"No Sales Invoice linked to Journal Entry {reference}")
        return
    
    # Update the allocated amount for insurance payments in the Sales Invoice
    update_sales_invoice(sales_invoice_id, allocated_amount, "insurance_paid")
    
def update_outstanding_and_status(invoice, allocated_amount, amount_field):
    insurance_paid = invoice.get("insurance_paid") or 0
    patient_paid = invoice.get("patient_paid") or 0
    grand_total = invoice.get("grand_total") or 0
    paid_amount = invoice.get("paid_amount") or 0
    # Update the paid amount for patient or insurance
    current_paid_amount = invoice.get(amount_field) or 0
    new_paid_amount = current_paid_amount + allocated_amount
    
    if (amount_field == "insurance_paid"):
        # Calculate new outstanding amount based on grand total
        outstanding_amount = invoice.outstanding_amount - allocated_amount
        frappe.db.set_value("Sales Invoice", invoice.name, "outstanding_amount", max(0, outstanding_amount))
    
    if (amount_field == "patient_paid"):
        outstanding_amount = grand_total - (insurance_paid + patient_paid + allocated_amount)
        frappe.db.set_value("Sales Invoice", invoice.name, "outstanding_amount", max(0, outstanding_amount))
    
    frappe.db.set_value("Sales Invoice", invoice.name, amount_field, new_paid_amount)
    
    # Update the status based on the outstanding amount
    if outstanding_amount == 0:
        new_status = "Paid"
        frappe.db.set_value("Sales Invoice", invoice.name, "status", new_status)
        frappe.errprint(f"Updated Sales Invoice {invoice.name}. New status: {new_status}, Outstanding: {outstanding_amount}") 
        
    if not paid_amount and outstanding_amount > 0:
        new_status = "Partly Paid"
        frappe.db.set_value("Sales Invoice", invoice.name, "status", new_status)
        frappe.errprint(f"Updated Sales Invoice {invoice.name}. New status: {new_status}, Outstanding: {outstanding_amount}")    
    
    if paid_amount and outstanding_amount > 0: 
        new_status = "Partly Paid"
        frappe.db.set_value("Sales Invoice", invoice.name, "status", new_status)
        frappe.errprint(f"Updated Sales Invoice {invoice.name}. New status: {new_status}, Outstanding: {outstanding_amount}")

@frappe.whitelist()
def reverse_sales_invoice_on_cancel(doc, method=None):
    try:
        frappe.errprint(f"Processing Payment Entry Cancellation: {doc.name}")
        payment = frappe.get_doc("Payment Entry", doc.name)
        
        # Loop through references in the Payment Entry to undo the allocated amounts
        for reference in payment.references:
            allocated_amount = reference.allocated_amount  # Get the allocated amount from Payment Entry Reference

            if reference.reference_doctype == "Sales Invoice":
                # Reverse the patient paid amount
                reverse_sales_invoice(reference.reference_name, allocated_amount, "patient_paid")
            elif reference.reference_doctype == "Journal Entry":
                # Reverse the insurance paid amount via Journal Entry
                reverse_sales_invoice_via_journal_entry(reference.reference_name, allocated_amount)
                
    except Exception as e:
        frappe.errprint(f"Error in reversing Sales Invoice: {str(e)}")
        frappe.throw(f"Error in reversing Sales Invoice: {str(e)}")

def reverse_sales_invoice(reference, allocated_amount, payment_type):
    sales_invoice_id = reference
    
    if not sales_invoice_id:
        frappe.errprint(f"No Sales Invoice ID provided for {payment_type} reversal.")
        return
    
    invoice = frappe.get_doc("Sales Invoice", sales_invoice_id)

    # Get the correct field to update
    amount_field = "patient_paid" if payment_type == "patient_paid" else "insurance_paid"

    # Undo the outstanding amount and status based on canceled payment
    undo_outstanding_and_status(invoice, allocated_amount, amount_field)

def reverse_sales_invoice_via_journal_entry(reference, allocated_amount):
    # Fetch the Journal Entry document using the reference name
    journal_entry = frappe.get_doc("Journal Entry", reference)
    # Get the Sales Invoice linked to this Journal Entry
    sales_invoice_id = journal_entry.reference_invoice
    
    if not sales_invoice_id:
        frappe.errprint(f"No Sales Invoice linked to Journal Entry {reference}")
        return
    
    # Reverse the allocated amount for insurance payments in the Sales Invoice
    reverse_sales_invoice(sales_invoice_id, allocated_amount, "insurance_paid")

def undo_outstanding_and_status(invoice, allocated_amount, amount_field):
    insurance_paid = invoice.get("insurance_paid") or 0
    patient_paid = invoice.get("patient_paid") or 0
    grand_total = invoice.get("grand_total") or 0
    paid_amount = invoice.get("paid_amount") or 0

    # Undo the paid amount for patient or insurance
    current_paid_amount = invoice.get(amount_field) or 0
    new_paid_amount = current_paid_amount - allocated_amount
    
    if (amount_field == "insurance_paid"):
        # Calculate new outstanding amount based on grand total
        outstanding_amount = invoice.outstanding_amount + allocated_amount
        frappe.db.set_value("Sales Invoice", invoice.name, "outstanding_amount", outstanding_amount)
    
    if (amount_field == "patient_paid"):
        outstanding_amount = grand_total - (insurance_paid + patient_paid - allocated_amount)
        frappe.db.set_value("Sales Invoice", invoice.name, "outstanding_amount", outstanding_amount)
    
    frappe.db.set_value("Sales Invoice", invoice.name, amount_field, new_paid_amount)
    
    # Update the status based on the outstanding amount
    if paid_amount and outstanding_amount > 0:
        new_status = "Partly Paid"
        # frappe.throw(new_status)
        frappe.db.set_value("Sales Invoice", invoice.name, "status", new_status)
        frappe.errprint(f"Reversed Sales Invoice {invoice.name}. New status: {new_status}, Outstanding: {outstanding_amount}")
        
    if not paid_amount and outstanding_amount > 0:
        new_status = "Unpaid"
        # frappe.throw(new_status)
        frappe.db.set_value("Sales Invoice", invoice.name, "status", new_status)
        frappe.errprint(f"Reversed Sales Invoice {invoice.name}. New status: {new_status}, Outstanding: {outstanding_amount}")
