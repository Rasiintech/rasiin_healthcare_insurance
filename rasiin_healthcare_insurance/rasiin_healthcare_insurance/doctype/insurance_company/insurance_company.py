# Copyright (c) 2024, Ahmed Ibar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class InsuranceCompany(Document):
    def after_insert(self):
        customer = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": self.company_name,
			"customer_group": "Insurance",
			"customer_type": "Company",
			"mobile_no": self.mobile,
			"territory": "Somalia",
		})
        customer.insert()
        frappe.db.set_value("Insurance Company", self.name, "customer", customer.name)

