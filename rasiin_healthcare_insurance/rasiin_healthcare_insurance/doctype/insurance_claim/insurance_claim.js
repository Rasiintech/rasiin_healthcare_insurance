frappe.ui.form.on('Insurance Claim', {
	onload: function (frm) {
		// Hide the claim invoices table on load
		frm.toggle_display('claim_invoices', false);
	},
	refresh: function (frm) {

		// If the document is new, hide both tables
		if (frm.is_new()) {
			frm.toggle_display('claim_invoices', false);
			frm.toggle_display('detailed_claim_invoices', false);
			frm.disable_save(); // Disable saving for new document until data is fetched
		} else {
			// Enable save and show tables if data is present
			frm.enable_save();
				if (frm.doc.detailed_claim_invoices && frm.doc.detailed_claim_invoices.length > 0) {
					frm.add_custom_button("Print Invoices", function () {
						// Collect invoice numbers from the child table
						const invoice_numbers = frm.doc.detailed_claim_invoices
							.map(row => row.invoice_number)
							.filter(invoice => !!invoice); // Ensure no empty values are included
				
						if (invoice_numbers.length === 0) {
							frappe.msgprint(__("No valid invoices found in the child table."));
							return;
						}
				
						// Build the URL for previewing the PDF
						const url = `/api/method/frappe.utils.print_format.download_multi_pdf?doctype=Sales Invoice`
							+ `&name=${encodeURIComponent(JSON.stringify(invoice_numbers))}` // Safely encode the names
							+ `&format=Insurance Print Format` // Replace with your print format name
							+ `&no_letterhead=0` // Set to 1 if you don't want the letterhead
							+ `&options=${encodeURIComponent(JSON.stringify({ "page-size": "A4" }))}`;
				
						// Open the PDF in a new tab
						window.open(url, "_blank");
					});
				}
			
			// Show or hide tables based on data availability
			// frm.toggle_display('claim_invoices', frm.doc.claim_invoices && frm.doc.claim_invoices.length > 0);
			frm.toggle_display('detailed_claim_invoices', frm.doc.detailed_claim_invoices && frm.doc.detailed_claim_invoices.length > 0);
		}

		// Add a button to make a payment
		// if (!frm.is_new() && frm.doc.docstatus === 1 && frm.doc.payment_status !== 'Paid') {
		// 	frm.add_custom_button(__('Make Payment'), function () {
		// 		open_payment_entry(frm);
		// 	}, __('Actions'));
		// }

		if (frm.doc.docstatus === 1) {  // Show the button only if the document is submitted
			frm.add_custom_button(__('Create Payment Entry'), function () {
				frappe.call({
					method: 'rasiin_healthcare_insurance.api.get_journal_entries_for_insurance_claim.create_payment_entry_for_claim',
					args: {
						insurance_claim_name: frm.doc.name
					},
					callback: function (r) {
						if (r.message) {
							frappe.set_route('Form', 'Payment Entry', r.message);
						}
					}
				});
			}, __('Actions'));
		}
		
		
		// Add Summary button
		frm.add_custom_button(__('Summary'), function () {
			// Clear detailed table and hide it
			frm.clear_table('detailed_claim_invoices');
			frm.toggle_display('detailed_claim_invoices', false);

			// Validate required fields before fetching summary data
			if (!frm.doc.insurance_company || !frm.doc.from_date || !frm.doc.to_date) {
				frappe.msgprint(__('Please select an Insurance Company, From Date, and To Date.'));
				return;
			}

			// Fetch summary data
			frappe.call({
				method: 'rasiin_healthcare_insurance.rasiin_healthcare_insurance.doctype.insurance_claim.insurance_claim.get_claims_summary',
				args: {
					insurance_company: frm.doc.insurance_company,
					patient: frm.doc.patient || null,
					from_date: frm.doc.from_date || null,
					to_date: frm.doc.to_date || null
				},
				callback: function (r) {
					if (r.message && r.message.summary_data) {
						// Clear the summary table before populating new data
						frm.clear_table('claim_invoices');

						// Populate the summary table with the data
						$.each(r.message.summary_data, function (patient, data) {
							let row = frm.add_child('claim_invoices');
							row.patient = patient;
							row.patient_name = data.patient_name;
							row.insurance_policy = data.insurance_policy;
							row.coverage_limit = data.coverage_limit;
							row.expiry_date = data.expiry_date;
							row.total_invoices = data.total_invoices;
							row.total_patient_amount = data.total_patient_amount;
							row.total_insurance_amount = data.total_insurance_amount;
							row.total_invoiced_amount = data.total_invoiced_amount;
						});

						frm.refresh_field('claim_invoices');

						// Show the summary table
						frm.toggle_display('claim_invoices', true);
						frm.disable_save();
						// Update the total fields for Summary
						frm.set_value('total_patient_amount', r.message.total_patient_amount);
						frm.set_value('total_insurance_amount', r.message.total_insurance_amount);
						frm.set_value('total_invoiced_amount', r.message.total_invoiced_amount);
					} else {
						frappe.msgprint(__('No summary data available for the selected criteria.'));
					}
				}
			});
		});

		// Add Detailed button
		frm.add_custom_button(__('Detailed'), function () {
			// Clear summary table and hide it
			frm.clear_table('claim_invoices');
			frm.toggle_display('claim_invoices', false);

			// Validate required fields before fetching detailed data
			if (!frm.doc.insurance_company || !frm.doc.from_date || !frm.doc.to_date) {
				frappe.msgprint(__('Please select an Insurance Company, From Date, and To Date.'));
				return;
			}

			// Fetch detailed data
			frappe.call({
				method: 'rasiin_healthcare_insurance.rasiin_healthcare_insurance.doctype.insurance_claim.insurance_claim.get_claims_detailed',
				args: {
					insurance_company: frm.doc.insurance_company,
					patient: frm.doc.patient || null,
					from_date: frm.doc.from_date || null,
					to_date: frm.doc.to_date || null
				},
				callback: function (r) {
					if (r.message && r.message.detailed_data) {
						// Clear the detailed table before populating
						frm.clear_table('detailed_claim_invoices');

						// Populate the detailed table with invoice data
						$.each(r.message.detailed_data, function (i, data) {
							let row = frm.add_child('detailed_claim_invoices');
							row.patient = data.patient;
							row.patient_name = data.patient_name;
							row.insurance_policy = data.insurance_policy;
							row.policy_number = data.policy_number;
							row.invoice_date = data.invoice_date;
							row.invoice_number = data.invoice_number;
							row.invoice_amount = data.invoice_amount;
							row.insurance_amount = data.insurance_amount;
							row.patient_amount = data.patient_amount;
							row.coverage_limit = data.coverage_limit;
							row.expiry_date = data.expiry_date;
						});

						frm.refresh_field('detailed_claim_invoices');

						// Show the detailed table
						frm.toggle_display('detailed_claim_invoices', true);

						// Update the total fields for Detailed
						frm.set_value('total_insurance_amount', r.message.total_insurance_amount);
						frm.set_value('total_invoiced_amount', r.message.total_invoiced_amount);
						frm.set_value('total_patient_amount', r.message.total_patient_amount);

						frm.enable_save();
					} else {
						frappe.msgprint(__('No detailed data available for the selected criteria.'));
					}
				}
			});
		});
	},

	insurance_company: function (frm) {
        if (!frm.doc.insurance_company) {
            frappe.msgprint(__('Please select an Insurance Company first.'));
            return;
        }

        // Fetch filtered patients from the server
        frappe.call({
            method: "rasiin_healthcare_insurance.rasiin_healthcare_insurance.doctype.insurance_claim.insurance_claim.get_patients_by_insurance_company",
            args: {
                insurance_company: frm.doc.insurance_company
            },
            callback: function (response) {
                const patient_list = response.message || [];

                // Dynamically set the query for the 'patient' field
                frm.set_query('patient', function () {
                    return {
                        filters: {
                            name: ["in", patient_list.map(patient => patient.name)]
                        }
                    };
                });

                // Optionally clear the patient field if the company changes
                frm.set_value('patient', null);
            }
        });
    },
});

// Function to recalculate total values when a row is removed
function update_totals(frm) {
	// Initialize total variables
	let total_invoiced_amount = 0;
	let total_insurance_amount = 0;

	// Iterate through claim_invoices to calculate totals
	frm.doc.claim_invoices.forEach(function (row) {
		if (!row.is_rejected) {

			total_invoiced_amount += row.total_invoiced_amount || 0;
			total_insurance_amount += row.total_insurance_amount || 0;
		}
	});

	// Iterate through detailed_claim_invoices to calculate totals
	frm.doc.detailed_claim_invoices.forEach(function (row) {
		if (!row.is_rejected) {
			total_invoiced_amount += row.invoice_amount || 0;
			total_insurance_amount += row.insurance_amount || 0;
		}
	});

	// Set the total values in the parent doc
	frm.set_value('total_invoiced_amount', total_invoiced_amount);
	frm.set_value('total_insurance_amount', total_insurance_amount);

	// Refresh fields
	frm.refresh_fields(['total_invoiced_amount', 'total_insurance_amount']);
}

frappe.ui.form.on('Claim Invoice', {
	claim_invoices_remove: function (frm) {
		// Update totals when a row is removed
		update_totals(frm);
	},

});

frappe.ui.form.on('Detailed Claim Invoices', {
	detailed_claim_invoices_remove: function (frm) {
		// Update totals when a row is removed
		update_totals(frm);
	},
	is_rejected(frm, cdt, cdn) {
		update_totals(frm);
		frm.save_or_update();
	}

});


// function open_payment_entry(frm) {
// 	// Check if there are pending amounts to be paid
// 	if (frm.doc.total_insurance_amount > frm.doc.total_payment_amount) {

// 		// Extract the sales invoice numbers from the detailed_claim_invoices table
// 		let sales_invoices = frm.doc.detailed_claim_invoices.map(inv => inv.invoice_number);

// 		// Fetch Journal Entries related to these Sales Invoices
// 		frappe.call({
// 			method: 'rasiin_healthcare_insurance.api.get_journal_entries_for_insurance_claim.create_payment_entry_for_claim',
// 			args: {
// 				insurance_company: frm.doc.insurance_company,
// 				sales_invoices: JSON.stringify(sales_invoices)
// 			},
// 			callback: function (response) {
// 				let journals = response.message;

// 				if (journals && journals.length > 0) {
// 					// Prepare the references table data
// 					let references = journals.map(journal => ({
// 						reference_doctype: 'Journal Entry',
// 						reference_name: journal.journal_entry,
// 						total_amount: journal.total_debit || journal.total_credit,
// 						outstanding_amount: journal.total_debit || journal.total_credit,
// 						allocated_amount: journal.total_debit || journal.total_credit
// 					}));

// 					// Create a new Payment Entry document
// 					frappe.new_doc('Payment Entry', {
// 						payment_type: 'Receive',
// 						party_type: 'Customer',
// 						paid_from: "1320 - Insurance Receivable - RD",
// 						paid_from_account_currency: "USD",
// 						paid_to: "1110 - Merchant - RD",
// 						paid_to_account_currency: "USD",
// 						company: frm.doc.company,
// 						reference_no: frm.doc.name,
// 						reference_date: frappe.datetime.now_date()
// 					}, function (new_doc) {
// 						frappe.set_route('Form', 'Payment Entry', new_doc.name).then(() => {
// 							let payment_entry = cur_frm;

// 							// Verify the form is loaded correctly
// 							if (!payment_entry.doc) {
// 								frappe.msgprint(__('Payment Entry form is not loaded properly.'));
// 								return;
// 							}

// 							// Set basic values
// 							payment_entry.set_value('party', frm.doc.insurance_company);
// 							let pending_amount = frm.doc.total_insurance_amount - frm.doc.total_payment_amount;
// 							payment_entry.set_value('paid_amount', pending_amount);
// 							payment_entry.set_value('received_amount', pending_amount);
// 							payment_entry.set_value('cost_center', 'Cashiers - RD');

// 							// Clear existing entries
// 							payment_entry.clear_table('references');

// 							// Check if references data is available
// 							if (references.length > 0) {
// 								references.forEach(reference => {
// 									console.log('Adding reference:', reference);
// 									let row = frappe.model.add_child(payment_entry, 'references');
// 									console.log('Row created:', row);
// 									frappe.model.set_value(row.doctype, row.name, 'reference_doctype', reference.reference_doctype);
// 									frappe.model.set_value(row.doctype, row.name, 'reference_name', reference.reference_name);
// 									frappe.model.set_value(row.doctype, row.name, 'total_amount', reference.total_amount);
// 									frappe.model.set_value(row.doctype, row.name, 'outstanding_amount', reference.outstanding_amount);
// 									frappe.model.set_value(row.doctype, row.name, 'allocated_amount', reference.allocated_amount);
// 									console.log('Updated row:', row);
// 								});

// 								// Refresh references table in UI
// 								payment_entry.refresh_field('references');

// 								// Save the Payment Entry
// 								payment_entry.save().then(() => {
// 									frappe.msgprint(__('Payment Entry created successfully with references.'));
// 								}).catch(error => {
// 									frappe.msgprint(__('An error occurred while saving the Payment Entry.'));
// 									console.error(error);
// 								});
// 							} else {
// 								frappe.msgprint(__('No references to add.'));
// 							}
// 						});
// 					});

// 				} else {
// 					frappe.msgprint(__('No related Journal Entries found for the selected Sales Invoices.'));
// 				}
// 			}
// 		});
// 	} else {
// 		frappe.msgprint(__('No outstanding amount to be paid.'));
// 	}
// }
