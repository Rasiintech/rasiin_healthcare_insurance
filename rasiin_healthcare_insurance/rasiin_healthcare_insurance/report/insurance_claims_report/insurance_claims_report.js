// Copyright (c) 2024, Ahmed Ibar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Insurance Claims Report"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "insurance_company",
			label: __("Insurance Company"),
			fieldtype: "Link",
			options: "Insurance Company"
		},
		{
			fieldname: "patient",
			label: __("Patient"),
			fieldtype: "Link",
			options: "Patient"
		},
		{
			fieldname: "detailed",
			label: __("Detailed View"),
			fieldtype: "Check",
			default: 0
		}
	]
};
