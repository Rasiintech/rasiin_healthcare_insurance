import frappe
from frappe import _
from erpnext.stock.get_item_details import get_pos_profile

@frappe.whitelist()
def cancel_linked_documents(**args):
    # Cancel the Que document
    frappe.db.set_value('Que', args.get("que"), 'status', 'Canceled')

    # Cancel the Patient Sales Invoice
    patient_sales_invoice_name = args.get("patient_sales_invoice")
    if patient_sales_invoice_name and frappe.db.exists("Sales Invoice", patient_sales_invoice_name):
        patient_sales_invoice = frappe.get_doc("Sales Invoice", patient_sales_invoice_name)
        if patient_sales_invoice.docstatus == 1:
            patient_sales_invoice.cancel()

    # Cancel the Patient Sales Order
    patient_sales_order_name = args.get("patient_sales_order")
    if patient_sales_order_name and frappe.db.exists("Sales Order", patient_sales_order_name):
        patient_sales_order = frappe.get_doc("Sales Order", patient_sales_order_name)
        if patient_sales_order.docstatus == 1:
            patient_sales_order.cancel()

    # Cancel the Insurance Sales Invoice
    insurance_sales_invoice_name = args.get("insurance_sales_invoice")
    if insurance_sales_invoice_name and frappe.db.exists("Sales Invoice", insurance_sales_invoice_name):
        insurance_sales_invoice = frappe.get_doc("Sales Invoice", insurance_sales_invoice_name)
        if insurance_sales_invoice.docstatus == 1:
            insurance_sales_invoice.cancel()

    # Cancel the Insurance Sales Order
    insurance_sales_order_name = args.get("insurance_sales_order")
    if insurance_sales_order_name and frappe.db.exists("Sales Order", insurance_sales_order_name):
        insurance_sales_order = frappe.get_doc("Sales Order", insurance_sales_order_name)
        if insurance_sales_order.docstatus == 1:
            insurance_sales_order.cancel()

    # Cancel the Fee Validity (if applicable)
    fee_name = args.get("fee")
    if fee_name and frappe.db.exists("Fee Validity", fee_name):
        fee_validity = frappe.get_doc("Fee Validity", fee_name)
        if fee_validity.docstatus == 1:
            fee_validity.cancel()

    frappe.msgprint(_("All linked orders and invoices have been canceled."))

@frappe.whitelist()
def process_refund(patient_sales_invoice=None, insurance_sales_invoice=None, que=None, is_sales_return=False):
    # Process Patient Sales Invoice Refund
    if patient_sales_invoice:
        refund_sales_invoice(patient_sales_invoice, que, is_sales_return)

    # Process Insurance Sales Invoice Refund (if applicable)
    if insurance_sales_invoice:
        refund_sales_invoice(insurance_sales_invoice, que, is_sales_return)

    frappe.msgprint('Refunded successfully')
    return True


def refund_sales_invoice(sales_invoice_name, que, is_sales_return):
    cash_sales = frappe.get_doc("Sales Invoice", sales_invoice_name)
    pos_profile = get_pos_profile(cash_sales.company)
    mode_of_payment = frappe.db.get_value('POS Payment Method', {"parent": pos_profile.name},  'mode_of_payment')

    items = []
    for item in cash_sales.items:
        qty = item.qty
        if is_sales_return:
            qty = float(item.qty) * (-1)
        items.append({
            "item_code": item.item_code,
            "rate": item.rate,
            "qty": qty
        })

    payments = []
    paid_amount = cash_sales.grand_total if not is_sales_return else cash_sales.grand_total * (-1)

    payments.append({
        "mode_of_payment": mode_of_payment,
        "amount": paid_amount
    })

    is_return = 1 if is_sales_return else 0
    sales_doc = frappe.get_doc({
        "doctype": "Sales Invoice",
        "is_return": is_return,
        "posting_date": cash_sales.posting_date,
        "customer": cash_sales.customer,
        "patient": cash_sales.patient,
        "is_pos": 1,
        "discount_amount": cash_sales.discount_amount,
        "payments": payments,
        "voucher_no": cash_sales.name,
        "items": items,
    })

    sales_doc.insert(ignore_permissions=True)
    sales_doc.submit()

    # Update the status of the Que
    if que:
        frappe.db.set_value('Que', que, 'status', 'Refunded')

    return sales_doc



