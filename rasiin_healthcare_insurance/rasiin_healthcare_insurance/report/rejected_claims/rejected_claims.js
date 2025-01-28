// Copyright (c) 2024, Ahmed Ibar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rejected Claims"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
		},
		{
			"fieldname": "insurance_company",
			"label": "Insurance Company",
			"fieldtype": "Link",
			"options": "Insurance Company",
		},
	]
};
