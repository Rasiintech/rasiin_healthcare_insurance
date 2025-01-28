frappe.ui.form.on('Patient', {
    refresh(frm) {
        // alert("Hello")
        // 		if (frappe.user_roles.includes('Cashier')) {   
        // 			frm.set_df_property("is_employee" , "hidden" , 1)
        // 			frm.set_df_property("is_insurance" , "hidden" , 1)
        // 			frm.set_df_property("ref_insturance" , "hidden" , 1)
        // 			frm.set_df_property("insurance_number" , "hidden" , 1)
        // 		}

        // // 		    frm.set_query('ref_insturance', () => {
        // //     return {
        // //         filters: {
        // //             customer_group: 'INSURANCE'
        // //         }
        // //     }
        // // })
    },

    add_insurance_policy: function (frm) {
        console.log("Hello");
        if (frm.is_new()) {
            frappe.throw("Please save the patient information first")
        } else {
            frappe.new_doc('Insurance Policy', {
                policyholder: frm.doc.name,
                "policyholder_name": frm.doc.patient_name,
            }, true); // 'true' enables quick entry
        }
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


