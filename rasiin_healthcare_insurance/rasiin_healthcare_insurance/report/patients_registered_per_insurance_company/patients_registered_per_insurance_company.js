// Copyright (c) 2024, Ahmed Ibar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Patients Registered per Insurance Company"] = {
	"filters": [
		{
			"fieldname": "insurance_company",
			"label": __("Insurance Company"),
			"fieldtype": "Link",
			"options": "Insurance Company",
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "detailed",
			"label": "Detailed Report",
			"fieldtype": "Check",
			"default": 0
		},
	]
};