frappe.query_reports["Insurance Payment Tracking"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			// "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"default": frappe.datetime.get_today().slice(0, 4) + "-01-01",
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
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
		
		{
			"fieldname": "detailed",
			"label": "Detailed View",
			"fieldtype": "Check",
			"default": 0
		}
	]
};
