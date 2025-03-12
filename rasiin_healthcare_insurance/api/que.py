import frappe 
from frappe import _
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.model.utils import get_fetch_values
from frappe.contacts.doctype.address.address import get_company_address
from erpnext.stock.get_item_details import get_pos_profile

from rasiin_healthcare_insurance.api.patient_insurance_billing import create_journal_entry_for_insurance

@frappe.whitelist()
def create_que_order_bill(doc, method=None):
    
    company = frappe.defaults.get_user_default("company")
    pos_profile = get_pos_profile(company)
    # mode_of_payment = frappe.db.get_value('POS Payment Method', {"parent": pos_profile.name}, 'mode_of_payment')
    mode_of_payment = doc.mode_of_payment

    patient_customer = frappe.db.get_value("Patient", doc.patient, "customer")
    insurance_company = frappe.db.get_value("Insurance Policy", doc.insurance_policy, "insurance_company")

    # if not patient_customer:
    #     frappe.throw(_("Customer is required to create a Sales Order."))
    # if not insurance_company:
    #     frappe.throw(_("Insurance Company is required for insurance billing."))

    # Create a Sales Order for the full amount
    if doc.doctor_amount > 0:
        sales_order = create_sales_order(doc, patient_customer, doc.doctor_amount)

        # Create Sales Invoice and handle payments
        sales_invoice_name = make_sales_invoice_direct(sales_order, doc.payable_amount, mode_of_payment, doc)

        doc.db_set('sales_order', sales_order)
        doc.db_set('sales_invoice', sales_invoice_name)

    return {"sales_order": sales_order, "sales_invoice": sales_invoice_name}

    

def create_sales_order(doc, customer, amount):
    company = frappe.defaults.get_user_default("company")
    company_doc = frappe.get_doc("Company", company)
    items = [{
        "item_code": "OPD Consultation",
        "rate": amount,
        "qty": 1,
    }]

    sales_order = frappe.get_doc({
        "doctype": "Sales Order",
        "transaction_date": doc.date,
        "patient": doc.patient,
        "patient_name": doc.patient_name,
        "customer": customer,
        "discount_amount": doc.discount,
        "voucher_no": doc.name,
        "delivery_date": frappe.utils.getdate(),
        "source_order": "OPD",
        "ref_practitioner": doc.practitioner,
        "items": items,
        "so_type": "Cashiers",
        "cost_center": doc.cost_center
        
    })

    sales_order.insert()
    sales_order.submit()
    
    return sales_order.name

@frappe.whitelist()
def make_sales_invoice_direct(source_name, payable_amount, mode_of_payment=None, doc=None):

    def postprocess(source, target):
        set_missing_values(source, target)
        if target.get("allocate_advances_automatically"):
            target.set_advances()
        
        if doc and doc.cost_center:
            target.cost_center = doc.cost_center

        
        # Propagate cost center to items
        for item in target.items:
            if doc.cost_center:
                item.cost_center = doc.cost_center
                
                
    def set_missing_values(source, target):
        target.is_pos = 1 if payable_amount > 0 else 0
        if doc.bill_to_employee and payable_amount == 0:
            target.is_pos = 0
            target.bill_to_employee = 1
            target.employee = doc.employee
        elif doc.bill_to_employee and payable_amount > 0:
            target.is_pos = 1
            target.bill_to_employee = 1
            target.employee = doc.employee
        # Ensure `payable_amount` is not None before checking its value
        if payable_amount is not None:
            existing_payment = next((p for p in target.payments if p.mode_of_payment == mode_of_payment), None)
            if existing_payment:
                existing_payment.amount = round(payable_amount, 2)
            elif payable_amount > 0:
                target.append("payments", {
                    "mode_of_payment": mode_of_payment,
                    "amount": round(payable_amount, 2)
                })

        if doc:
            if target.patient != doc.patient:
                target.patient = doc.patient

            if target.insurance_coverage_amount != doc.insurance_coverage_amount:
                target.insurance_coverage_amount = doc.insurance_coverage_amount

            if target.payable_amount != doc.payable_amount:
                target.payable_amount = round(doc.payable_amount, 2)
                
            if target.que_reference != doc.name:
                target.que_reference = doc.name

        target.ignore_pricing_rule = 1
        target.flags.ignore_permissions = True
        target.run_method("set_missing_values")
        target.run_method("set_po_nos")
        target.run_method("calculate_taxes_and_totals")

        if source.company_address:
            target.update({'company_address': source.company_address})
        else:
            target.update(get_company_address(target.company))

        if target.company_address:
            target.update(get_fetch_values("Sales Invoice", 'company_address', target.company_address))


    def update_item(source, target, source_parent):
        target.amount = flt(source.amount) - flt(source.billed_amt)
        target.base_amount = target.amount * flt(source_parent.conversion_rate)
        target.qty = target.amount / flt(source.rate) if (source.rate and source.billed_amt) else source.qty - source.returned_qty

        if source_parent.project:
            target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center")
        if target.item_code:
            item = get_item_defaults(target.item_code, source_parent.company)
            item_group = get_item_group_defaults(target.item_code, source_parent.company)
            cost_center = item.get("selling_cost_center") or item_group.get("selling_cost_center")

            if cost_center:
                target.cost_center = cost_center

    doclist = get_mapped_doc("Sales Order", source_name, {
        "Sales Order": {
            "doctype": "Sales Invoice",
            "field_map": {
                "party_account_currency": "party_account_currency",
                "payment_terms_template": "payment_terms_template",
                "cost_center": "cost_center"
            },
            "field_no_map": ["payment_terms_template"],
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Sales Order Item": {
            "doctype": "Sales Invoice Item",
            "field_map": {
                "name": "so_detail",
                "parent": "sales_order",
            },
            "postprocess": update_item,
            "condition": lambda doc: doc.qty and (doc.base_amount == 0 or abs(doc.billed_amt) < abs(doc.amount))
        },
        "Sales Taxes and Charges": {
            "doctype": "Sales Taxes and Charges",
            "add_if_empty": True
        },
        "Sales Team": {
            "doctype": "Sales Team",
            "add_if_empty": True
        }
    }, target_doc=None, postprocess=postprocess, ignore_permissions=True)
    # frappe.errprint(doclist.name)
    # frappe.throw("STOP")
    doclist.save()
    doclist.submit()
    
    submitted_sales_invoice = frappe.get_doc("Sales Invoice", doclist.name)
    
    create_journal_entry_for_insurance(submitted_sales_invoice)

