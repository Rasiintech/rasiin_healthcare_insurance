frappe.ui.form.on('Payment Entry', {
    onload: function(frm) {
        if (frappe.session.user) {
            frappe.call({
                method: "rasiin_healthcare_insurance.api.pos_profile.get_user_pos_profile",
                callback: function(response) {
                    if (response.message && response.message.mode_of_payment) {
                        frm.set_value("mode_of_payment", response.message.mode_of_payment);
                    }
                }
            });
        }
    },
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Reconcile Payment'), function () {
                // Set route options BEFORE navigation
                frappe.route_options = {
                    party_type: frm.doc.party_type || 'Customer',
                    party: frm.doc.party
                };
                frappe.set_route('payment-reconciliation');
            }, __('Actions'));
        }
        // alert("Hello")
    },

    quick_entry: function (frm) {
        // alert("Hello")
        // if (frm.doc.customer) {
        //     frappe.call({
        //         method: "frappe.client.get",
        //         args: {
        //             doctype: "Customer",
        //             name: frm.doc.customer
        //         },
        //         callback: function(r) {
        //             if (r.message) {
        //                 // Assuming 'customer_name' is a field in the Customer DocType
        //                 frm.set_value('customer_name', r.message.customer_name);
        //             }
        //         }
        //     });
        // }
    }
})

frappe.ui.form.on('Payment Entry Reference', {
    reference_name: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // console.log(row);

        // Check if the reference_doctype is 'Journal Entry'
        if (row.reference_doctype === "Journal Entry") {
            console.log("This is executed if it is not a Journal Entry");
            // Fetch the 'reference_invoice' field from the 'Journal Entry'
            let sales_invoice = frappe.db.get_value('Journal Entry', row.reference_name, 'reference_invoice', function (value) {
                frappe.model.set_value(cdt, cdn, 'sales_invoice', value.reference_invoice);
            });
            let patient = frappe.db.get_value('Journal Entry', row.reference_name, 'patient', function (value) {
                frappe.model.set_value(cdt, cdn, 'patient', value.patient);
            });
            let patient_name = frappe.db.get_value('Journal Entry', row.reference_name, 'patient_name', function (value) {
                frappe.model.set_value(cdt, cdn, 'patient_name', value.patient_name);
            });
            // console.log(values);

        } else {


            // Clear the field if it's not a Journal Entry
            frappe.model.set_value(cdt, cdn, 'sales_invoice', null);
        }
    }
});


