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
	],
	onload: function(report) {
        report.page.add_inner_button(__("Print Invoices"), function() {
            // Get report data
            frappe.call({
                method: "frappe.desk.query_report.run",
                args: {
                    report_name: "Insurance Claims Report",
                    filters: frappe.query_report.get_filter_values()
                },
                callback: function(response) {
                    let report_data = response.message.result;
                    
                    if (!report_data || report_data.length === 0) {
                        frappe.msgprint(__('No data found to print.'));
                        return;
                    }

                    // Extract all invoice numbers from the report
                    let invoice_numbers = report_data
                        .map(row => row.sales_invoice)
                        .filter(Boolean); // Remove any null or undefined values

                    if (invoice_numbers.length === 0) {
                        frappe.msgprint(__('No valid invoices found to print.'));
                        return;
                    }

                    // Build the URL for bulk printing
                    const url = `/api/method/frappe.utils.print_format.download_multi_pdf?doctype=Sales Invoice`
                        + `&name=${encodeURIComponent(JSON.stringify(invoice_numbers))}`
                        + `&format=Insurance Print Format` // Change to your print format name
                        + `&no_letterhead=0`
                        + `&options=${encodeURIComponent(JSON.stringify({ "page-size": "A4" }))}`;

                    // Open the generated PDF in a new tab
                    window.open(url, "_blank");
                }
            });
        });
    }
};
