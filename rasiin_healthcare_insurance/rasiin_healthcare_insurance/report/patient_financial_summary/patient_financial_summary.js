// Copyright (c) 2024, Ahmed Ibar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Patient Financial Summary"] = {
	"filters": [
		{
			"fieldname": "insurance_company",
			"label": "Insurance Company",
			"fieldtype": "Link",
			"options": "Insurance Company"
		},
		{
			"fieldname": "patient",
			"label": "Patient",
			"fieldtype": "Link",
			"options": "Patient"
		},
		// {
		// 	"fieldname": "coverage_limits",
		// 	"label": "Coverage Limit",
		// 	"fieldtype": "Data"
		// },
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date"
		},
		{
			"fieldname": "detailed",
			"label": "Detailed View",
			"fieldtype": "Check",
			default: 0
		},
	]
};
