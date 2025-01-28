import frappe 
from frappe import _
from frappe.utils import flt, cint, getdate
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.contacts.doctype.address.address import get_company_address
from erpnext.stock.get_item_details import get_pos_profile


def create_sales_order(doc, customer, amount, order_type):
    items = [{
        "item_code": "OPD Consultation",  # Replace with the correct item code
        "rate": amount,  # Use the amount directly
        "qty": 1,
    }]

    sales_order = frappe.get_doc({
        "doctype": "Sales Order",
        "transaction_date": doc.date,
        "customer": customer,
        "discount_amount": doc.discount if order_type == "Patient" else 0,
        "voucher_no": doc.name,
        "delivery_date": frappe.utils.getdate(),
        "source_order": "OPD",
        "ref_practitioner": doc.practitioner,
        "items": items,
    })

    sales_order.insert()
    sales_order.submit()
    
    frappe.msgprint(_('{} Sales Order created: {}').format(order_type, sales_order.name))
    
    return sales_order.name


@frappe.whitelist()
def make_sales_invoice_direct(source_name, amount, mode_of_payment=None, target_doc=None, ignore_permissions=True):
    def postprocess(source, target):
        set_missing_values(source, target)
        if target.get("allocate_advances_automatically"):
            target.set_advances()

    def set_missing_values(source, target):
        target.is_pos = 1
        target.append("payments", {
            "mode_of_payment": mode_of_payment,
            "amount": amount
        })
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
        # Custom logic for mapping each Sales Order item to a Sales Invoice item
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
                "payment_terms_template": "payment_terms_template"
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
            "postprocess": update_item,  # Use update_item to process each item
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
    }, target_doc, postprocess, ignore_permissions=ignore_permissions)

    doclist.save()
    doclist.submit()
    return doclist.name


@frappe.whitelist()
def make_credit_invoice(source_name, target_doc=None, ignore_permissions=False):
    def postprocess(source, target):
        set_missing_values(source, target)
        if target.get("allocate_advances_automatically"):
            target.set_advances()

    def set_missing_values(source, target):
        target.is_pos = 0
        target.update_stock = 1
        target.is_cash = 0
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
        # Custom logic for mapping each Sales Order item to a Sales Invoice item
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
                "payment_terms_template": "payment_terms_template"
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
            "postprocess": update_item,  # Use update_item to process each item
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
    }, target_doc, postprocess, ignore_permissions=ignore_permissions)

    doclist.save()
    doclist.submit()
    return doclist.name


@frappe.whitelist()
def create_que_order_bill(doc, method=None):
    company = frappe.defaults.get_user_default("company")
    pos_profile = get_pos_profile(company)
    mode_of_payment = frappe.db.get_value('POS Payment Method', {"parent": pos_profile.name}, 'mode_of_payment')

    # Get the patient and insurance company details
    patient_customer = frappe.db.get_value("Patient", doc.patient, "customer")
    insurance_company = frappe.db.get_value("Insurance Policy", doc.insurance_policy, "insurance_company_name")

    # Create Sales Order and Invoice for the Patient
    if doc.payable_amount > 0:
        patient_sales_order = create_sales_order(doc, doc.patient_name, doc.payable_amount, "All Customer Groups")
        patient_invoice = make_sales_invoice_direct(patient_sales_order, doc.payable_amount, mode_of_payment)
        doc.db_set('patient_sales_order', patient_sales_order)
        doc.db_set('patient_sales_invoice', patient_invoice)

    # Create Sales Order and Invoice for the Insurance Company
    if doc.insurance_coverage_amount > 0:
        insurance_sales_order = create_sales_order(doc, doc.insurance_company, doc.insurance_coverage_amount, "Insurance")
        insurance_invoice = make_credit_invoice(insurance_sales_order)
        doc.db_set('insurance_sales_order', insurance_sales_order)
        doc.db_set('insurance_sales_invoice', insurance_invoice)

    return {"patient_sales_order": doc.patient_sales_order, "insurance_sales_order": doc.insurance_sales_order}


# @frappe.whitelist()
# def create_que_order_bill(doc, method=None):
#     company = frappe.defaults.get_user_default("company")
#     pos_profile = get_pos_profile(company)
#     mode_of_payment = frappe.db.get_value('POS Payment Method', {"parent": pos_profile.name}, 'mode_of_payment')

#     # Get the patient and insurance company details
#     customer = frappe.db.get_value("Patient", doc.patient, "customer")
#     insurance_company = frappe.db.get_value("Insurance Policy", doc.insurance_policy, "insurance_company_name")

#     # Create Sales Order and Invoice for the Patient
#     if doc.payable_amount > 0:
#         patient_sales_order = create_sales_order(doc, customer, doc.payable_amount, "Patient")
#         patient_invoice = make_sales_invoice_direct(patient_sales_order, doc.payable_amount, mode_of_payment)
#         doc.db_set('patient_sales_order', patient_sales_order)
#         doc.db_set('patient_sales_invoice', patient_invoice)

#     # Create Sales Order and Invoice for the Insurance Company
#     if doc.insurance_coverage_amount > 0:
#         insurance_sales_order = create_sales_order(doc, insurance_company, doc.insurance_coverage_amount, "Insurance")
#         insurance_invoice = make_credit_invoice(insurance_sales_order)
#         doc.db_set('insurance_sales_order', insurance_sales_order)
#         doc.db_set('insurance_sales_invoice', insurance_invoice)

#     return {"patient_sales_order": doc.patient_sales_order, "insurance_sales_order": doc.insurance_sales_order}
