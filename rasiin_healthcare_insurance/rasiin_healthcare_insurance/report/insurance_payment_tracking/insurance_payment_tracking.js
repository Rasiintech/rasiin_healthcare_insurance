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
	],
	onload: function(report) {
        report.page.add_inner_button(__("Print Invoices"), function() {
            // Get report data
            frappe.call({
                method: "frappe.desk.query_report.run",
                args: {
                    report_name: "Insurance Payment Tracking",
                    filters: frappe.query_report.get_filter_values()
                },
                callback: function(response) {
                    let report_data = response.message.result;

					// console.log(report_data);
                    
                    if (!report_data || report_data.length === 0) {
                        frappe.msgprint(__('No data found to print.'));
                        return;
                    }

                    // Extract all invoice numbers from the report
                    let invoice_numbers = report_data
                        .map(row => row.reference_invoice) // Adjust the key based on your report's data structure
                        .filter(Boolean);
						// .slice(0, 10); // Remove any null or undefined values

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
