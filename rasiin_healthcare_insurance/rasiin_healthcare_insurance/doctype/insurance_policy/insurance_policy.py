import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class InsurancePolicy(Document):
    # def on_(self):
    #     # Update the credit limit to unlimited or clear the child table entries
    #     if customer_doc.credit_limits:
    #         # Option 1: Set credit limit to 0 (unlimited)
    #         for credit_limit in customer_doc.credit_limits:
    #             credit_limit.credit_limit = 0  # Or another value to indicate unlimited
                
    #         # Option 2: Remove all entries from credit_limits child table
    #         # customer_doc.set("credit_limits", [])  # Clears the child table
            
    #         # # Save the changes to the Customer document
    #         # customer_doc.save()
    #         # frappe.db.commit()
    def after_insert(self):
        # Set the insurance policy field in the related Patient document when the Insurance Policy is created
        if self.expiration_date >= frappe.utils.nowdate():
            frappe.db.set_value("Patient", self.policyholder, "insurance_policy", self.name)

            patient_doc = frappe.get_doc("Patient", self.policyholder)
            customer_doc = frappe.get_doc("Customer", patient_doc.customer)
            
            if customer_doc.credit_limits:
                # Option 1: Set credit limit to 0 (unlimited)
                for credit_limit in customer_doc.credit_limits:
                    # frappe.errprint(credit_limit.credit_limit)
                    # frappe.throw("STOP")
                    credit_limit.credit_limit = 0  

                customer_doc.save()
                frappe.db.commit()
            

    def on_update(self):
        # Check if the policy is still enabled and the expiration date is valid
        if self.enabled == 1 and self.expiration_date >= frappe.utils.nowdate():
            # If the policy is valid and enabled, update the Patient's insurance policy field
            frappe.db.set_value("Patient", self.policyholder, "insurance_policy", self.name)
            patient_doc = frappe.get_doc("Patient", self.policyholder)
            customer_doc = frappe.get_doc("Customer", patient_doc.customer)
            
            if customer_doc.credit_limits:
                # Option 1: Set credit limit to 0 (unlimited)
                for credit_limit in customer_doc.credit_limits:
                    # frappe.errprint(credit_limit.credit_limit)
                    # frappe.throw("STOP")
                    credit_limit.credit_limit = 0  

                customer_doc.save()
                frappe.db.commit()
        else:
            # If the policy is expired or disabled, clear the insurance policy field in the Patient document
            frappe.db.set_value("Patient", self.policyholder, "insurance_policy", None)
            patient_doc = frappe.get_doc("Patient", self.policyholder)
            customer_doc = frappe.get_doc("Customer", patient_doc.customer)
            
            if customer_doc.credit_limits:
                # Option 1: Set credit limit to 0 (unlimited)
                for credit_limit in customer_doc.credit_limits:
                    # frappe.errprint(credit_limit.credit_limit)
                    # frappe.throw("STOP")
                    credit_limit.credit_limit = 0.01  

                customer_doc.save()
                frappe.db.commit()
            

def auto_disable_expired_policies():
    # Get the current date
    today = nowdate()
    
    # Fetch all active insurance policies that are expired
    expired_policies = frappe.get_all(
        "Insurance Policy",
        filters={
            "enabled": 1,  # Only active policies
            "expiration_date": ["<", today]  # Policies that have expired
        },
        fields=["name", "policyholder", "expiration_date"]  # Fetch the policyholder field too
    )
    
    if expired_policies:
        # Disable all expired policies
        for policy in expired_policies:
            # Disable the insurance policy
            frappe.db.set_value("Insurance Policy", policy["name"], "enabled", 0)

            # Clear the insurance_policy field in the related Patient document
            if policy["policyholder"]:
                frappe.db.set_value("Patient", policy["policyholder"], "insurance_policy", None)

            # Log the action
            frappe.logger().info(f"Disabled expired Insurance Policy: {policy['name']} (Expired on {policy['expiration_date']})")
        
        # Commit the changes
        frappe.db.commit()

        # Log the result for debugging
        frappe.errprint(f"{len(expired_policies)} insurance policies have been disabled and their policyholder fields have been cleared.")
    else:
        frappe.errprint("No expired policies found.")
