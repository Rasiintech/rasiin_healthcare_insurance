import frappe
from frappe import _
from frappe.utils import nowdate

@frappe.whitelist()
def create_payment_entry_for_claim(insurance_claim_name):
    
    company = frappe.defaults.get_user_default("company")
    company_doc = frappe.get_doc("Company", company)
    
    abbr = company_doc.abbr
    
    # Accounts to be used in the Journal Entry
    paid_from = f"1320 - Insurance Receivable - {abbr}"
    paid_to = f"1110 - Cash - {abbr}"
    
    # frappe.throw("create_payment_entry_for_claim")
    
    # Fetch the Insurance Claim document
    insurance_claim = frappe.get_doc("Insurance Claim", insurance_claim_name)

    # Check if there are pending amounts
    if insurance_claim.total_insurance_amount <= insurance_claim.total_payment_amount:
        frappe.throw(_("No outstanding amount to be paid."))

    # Extract the Sales Invoices from the detailed_claim_invoices table
    sales_invoices = [d.invoice_number for d in insurance_claim.detailed_claim_invoices if not d.is_rejected]
    if not sales_invoices:
        frappe.throw("No sales invoices found in detailed_claim_invoices.")

    # Fetch Journal Entries related to these Sales Invoices, ordered by posting_date (FIFO)
    journal_entries = frappe.db.get_all(
        'Journal Entry',
        filters={
            'insurance_company': insurance_claim.insurance_company,
            'reference_invoice': ['in', sales_invoices],
            'docstatus': 1  # Only submitted Journal Entries
        },
        fields=[
            'name as journal_entry',
            'total_debit',
            'total_credit',
            'reference_invoice as sales_invoice',
            'patient',
            'patient_name',
            'posting_date'  # Fetch the posting date to use in sorting
        ],
        order_by="posting_date asc"
    )
    
    if not journal_entries:
        frappe.throw(_("No related Journal Entries found for the selected Sales Invoices."))

    # Calculate pending amount
    pending_amount = insurance_claim.total_insurance_amount - insurance_claim.total_payment_amount
    insurance_company = frappe.db.get_value("Insurance Company", insurance_claim.insurance_company, "customer")
    # Create a new Payment Entry document
    payment_entry = frappe.get_doc({
        'doctype': 'Payment Entry',
        'payment_type': 'Receive',
        'party_type': 'Customer',  # Adjust according to your needs (e.g., 'Patient')
        'party': insurance_company,
        'paid_from': paid_from,  # Adjust according to your account setup
        'paid_from_account_currency': "USD",
        'paid_to':paid_to,  # Adjust according to your account setup
        'paid_to_account_currency': "USD",
        'claim_reference': insurance_claim.name,
        'reference_date': nowdate(),
        'paid_amount': pending_amount,
        'received_amount': pending_amount,
        'cost_center': company_doc.cost_center  # Adjust according to your setup
    })

    # Add references to the Payment Entry with calculated outstanding amounts
    for journal in journal_entries:
        frappe.errprint(f"Processing Journal Entry: {journal['journal_entry']}")

        # Calculate the outstanding amount manually by subtracting payments made
        total_amount = journal['total_debit'] or journal['total_credit']
        
        allocated_amount = frappe.db.sql("""
                                            SELECT SUM(per.allocated_amount) 
                                            FROM `tabPayment Entry Reference` per
                                            JOIN `tabPayment Entry` pe ON per.parent = pe.name
                                            WHERE per.reference_doctype = 'Journal Entry' 
                                            AND per.reference_name = %s
                                            AND pe.docstatus = 1
                                        """, journal['journal_entry'])[0][0] or 0

        
        # Calculate outstanding amount
        outstanding_amount = total_amount - allocated_amount

        # If there's no outstanding amount left, skip this journal entry
        if outstanding_amount <= 0:
            frappe.errprint(f"Journal Entry {journal['journal_entry']} has no outstanding amount.")
            continue

        payment_entry.append('references', {
            'reference_doctype': 'Journal Entry',
            'reference_name': journal['journal_entry'],
            'sales_invoice': journal['sales_invoice'],
            'patient': journal['patient'],
            'patient_name': journal['patient_name'],
            'total_amount': total_amount,
            'outstanding_amount': outstanding_amount,
            'allocated_amount': min(outstanding_amount, pending_amount)  # Allocate only the remaining pending or outstanding amount
        })

        # Decrease the pending amount by the allocated amount
        pending_amount -= outstanding_amount
        if pending_amount <= 0:
            break  # Stop if all pending amounts are allocated

    # Save the Payment Entry document
    if payment_entry.get('references'):
        payment_entry.insert(ignore_permissions=True)
        frappe.errprint(f"Payment Entry {payment_entry.name} created successfully.")
    else:
        frappe.throw(_("No outstanding amounts to allocate in the Journal Entries."))

    # Optionally submit the payment entry
    # payment_entry.submit()

    return payment_entry.name  # Return the name of the created Payment Entry


# import frappe

@frappe.whitelist()
def update_insurance_claim_status(doc, method=None):
    if doc.claim_reference:
        insurance_claim = frappe.get_doc("Insurance Claim", doc.claim_reference)

        # Calculate the new paid amount
        if method == "on_cancel":
            # Reverse the payment if the Payment Entry is being canceled
            paid_amount = insurance_claim.total_payment_amount - doc.paid_amount
        else:
            # Add the payment if the Payment Entry is being submitted
            paid_amount = insurance_claim.total_payment_amount + doc.paid_amount

        # Ensure the paid amount doesn't go below zero
        if paid_amount < 0:
            paid_amount = 0

        # # Determine the new status of the Insurance Claim
        if paid_amount == 0:
            new_status = 'Under Review'
        elif paid_amount < insurance_claim.total_insurance_amount:
            new_status = 'Partly Paid'
        elif paid_amount == insurance_claim.total_insurance_amount:
            new_status = 'Paid'
        else:
            frappe.throw(_("Invalid payment state. Check the payment amounts."))

        # Update the Insurance Claim document fields
        frappe.db.set_value('Insurance Claim', doc.claim_reference, {
            'claim_status': new_status,
            'total_payment_amount': paid_amount
        })

        # Return the updated claim status
        return new_status

