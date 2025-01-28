import frappe
from frappe.model.document import Document

class InsuranceClaim(Document):
    def on_submit(self):
        # frappe.throw(self.get("name"))
        # Assuming there is a child table in Insurance Claim with Sales Invoice references
        for invoice in self.get("detailed_claim_invoices"):
            # Update the is_claimed field in each Sales Invoice
            frappe.db.set_value('Sales Invoice', invoice.invoice_number, 'is_claimed', True)
            # frappe.db.set_value('Insurance Claim', self.name, 'last_view', 'Detailed')
            
    def on_cancel(self):
        # Assuming there is a child table in Insurance Claim with Sales Invoice references
        for invoice in self.get("detailed_claim_invoices"):
            # Update the is_claimed field in each Sales Invoice
            frappe.db.set_value('Sales Invoice', invoice.invoice_number, 'is_claimed', False)
    
    # def before_save(self):
    #     # frappe.throw("STOP")
    #     last_view = self.get("last_view")
    #     # frappe.throw(last_view)
    #     if last_view== "Detailed":
    #         frappe.db.set_value("Insurance Claim", "last_view", "Detailed")
        # if last_view == "Summary":
        #     frappe.db.set_value("Insurance Claim", last_view, "Summary")

@frappe.whitelist()
def get_claims_summary(insurance_company, patient=None, from_date=None, to_date=None):
    # Define base filters for the query
    filters = {
        'insurance_company': insurance_company,
        'docstatus': 1,  # Only consider submitted invoices
        'is_return': 0,  # Exclude return invoices
        "is_claimed": 0,
    }

    # Only add patient filter if patient is provided
    if patient:
        filters['patient'] = patient

    # Add date filters if both from_date and to_date are provided
    if from_date and to_date:
        filters['posting_date'] = ['between', [from_date, to_date]]
    elif from_date:
        filters['posting_date'] = ['>=', from_date]
    elif to_date:
        filters['posting_date'] = ['<=', to_date]

    # Fetch all invoices matching the filters
    invoices = frappe.get_all(
        'Sales Invoice', 
        filters=filters, 
        fields=[
            'name', 'patient', 'patient_name', 
            'insurance_policy', 'total', 
            'insurance_coverage_amount', 'payable_amount', 'coverage_limits', 'expiry_date', 
            'insurance_paid', 'patient_paid', 'posting_date'
        ], 
        order_by='patient_name asc'
    )
    
    if not invoices:
        frappe.throw("No invoices found for this insurance company within the specified date range")
    
    summary_data = {}
    total_patient_amount = 0
    total_insurance_amount = 0
    total_invoiced_amount = 0
    
    for invoice in invoices:        
        # Calculate insurance outstanding
        insurance_outstanding = invoice['insurance_coverage_amount'] - invoice['insurance_paid']
        patient_outstanding = invoice['payable_amount'] - invoice['patient_paid']
        
        # Only process invoices where insurance_outstanding is not zero
        if insurance_outstanding == 0:
            continue

        patient = invoice.patient
        if patient not in summary_data:
            summary_data[patient] = {
                "patient_name": invoice['patient_name'],
                "insurance_policy": invoice['insurance_policy'],
                "coverage_limit": invoice.get('coverage_limits'),  # Use .get() to avoid KeyError
                "expiry_date": invoice.get('expiry_date'),  # Use .get() to avoid KeyError
                'total_patient_amount': 0,
                'total_invoiced_amount': 0,
                'total_insurance_amount': 0,
                'total_invoices': 0,
            }
        
        summary_data[patient]['total_patient_amount'] += invoice['payable_amount'] 
        summary_data[patient]['total_insurance_amount'] += insurance_outstanding
        summary_data[patient]['total_invoiced_amount'] += invoice['total']
        summary_data[patient]['total_invoices'] += 1
        
        # Increment totals for all invoices
        total_patient_amount += invoice['payable_amount']
        total_insurance_amount += insurance_outstanding
        total_invoiced_amount += invoice['total']
    
    return {
        'summary_data': summary_data,
        'total_patient_amount': total_patient_amount,
        'total_insurance_amount': total_insurance_amount,
        'total_invoiced_amount': total_invoiced_amount,
    }

@frappe.whitelist()
def get_claims_detailed(insurance_company, patient=None, from_date=None, to_date=None):
    # Get all invoices where insurance company is linked
    filters = {
        'insurance_company': insurance_company,
        'docstatus': 1,  # Only consider submitted invoices
        'is_return': 0,  # Exclude return invoices
        "is_claimed": 0,
    }
    
    # Only add patient filter if patient is provided
    if patient:
        filters['patient'] = patient
        
    # Add date filters if both from_date and to_date are provided
    if from_date and to_date:
        filters['posting_date'] = ['between', [from_date, to_date]]
    elif from_date:
        filters['posting_date'] = ['>=', from_date]
    elif to_date:
        filters['posting_date'] = ['<=', to_date]
        
    invoices = frappe.get_all(
        'Sales Invoice', 
        filters=filters, 
        fields=[
            'name', 'patient', 'patient_name', 'insurance_policy', 
            'total', 'insurance_coverage_amount', 'payable_amount', 'posting_date', 
            'coverage_limits', 'policy_number', 'expiry_date', 
            'insurance_paid', 'patient_paid'
        ], 
        order_by='patient_name asc'
    )
    
    if not invoices:
        frappe.throw("No invoices found for this insurance company within the specified date range")
    
    detailed_data = []
    total_patient_amount = 0
    total_insurance_amount = 0
    total_invoiced_amount = 0
    
    # Process each invoice to include in detailed data
    for invoice in invoices:
        # Calculate insurance outstanding
        insurance_outstanding = invoice['insurance_coverage_amount'] - invoice['insurance_paid']
        patient_outstanding = invoice['payable_amount'] - invoice['patient_paid']
        
        # Only process invoices where insurance_outstanding is not zero
        if insurance_outstanding == 0:
            continue

        detailed_data.append({
            "patient": invoice['patient'],
            "patient_name": invoice['patient_name'],
            "insurance_policy": invoice['insurance_policy'],
            "policy_number": invoice.policy_number,  # Use .get() to handle missing keys
            "invoice_date": invoice['posting_date'],
            "invoice_number": invoice['name'],
            "invoice_amount": invoice['total'],
            "insurance_amount": insurance_outstanding,
            "patient_amount": invoice['payable_amount'],
            "coverage_limit": invoice.coverage_limits,  # Use .get() to handle missing keys
            "expiry_date": invoice.expiry_date,  # Use .get() to handle missing keys
        })
        
        # Increment totals for all invoices
        total_patient_amount += invoice['payable_amount']
        total_insurance_amount += insurance_outstanding
        total_invoiced_amount += invoice['total']

    return {
        'detailed_data': detailed_data,
        'total_insurance_amount': total_insurance_amount,
        'total_invoiced_amount': total_invoiced_amount,
        'total_patient_amount': total_patient_amount
    }


@frappe.whitelist()
def get_patients_by_insurance_company(insurance_company):
    # Fetch patients whose insurance_policy is linked to the given insurance_company
    return frappe.get_all(
        "Patient",
        filters={"insurance_policy": ["in", frappe.get_all("Insurance Policy", filters={"insurance_company": insurance_company}, pluck="name")]},
        fields=["name", "patient_name"]
    )