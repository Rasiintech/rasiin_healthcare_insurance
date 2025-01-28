frappe.ui.form.on('Que', {
    refresh: function (frm) {
        if (!frm.is_new()) {
            // List of specific fields to make read-only
            const fields_to_readonly = ['payable_amount'];
            fields_to_readonly.forEach(fieldname => {
                frm.set_df_property(fieldname, 'read_only', 1);
            });
        }
    },
    patient: function (frm) {
        let doctor_amount = frm.doc.doctor_amount || 0;
        let discount = frm.doc.discount || 0;
        let effective_amount = doctor_amount - discount
        let insurance_amount = (effective_amount * frm.doc.coverage_limits) / 100;
        let patient_amount = effective_amount - insurance_amount;

        if (frm.doc.discount < 0) {
            frappe.msgprint(__('Discount amount can not be below zero'));
            frm.set_value("discount", 0);
        }
        if (frm.doc.insurance_policy) {
            if (frm.doc.discount > patient_amount) {
                frappe.msgprint(__('Discount amount is greater than Patient Amount'));
                frm.set_value("discount", patient_amount);
            }
            frm.set_value("patient_amount", patient_amount);
            frm.set_value("insurance_coverage_amount", insurance_amount);
            frm.set_value("total_amount", patient_amount + insurance_amount);
            frm.set_value("payable_amount", patient_amount);
            frm.refresh_field("payable_amount");
            console.log("Insurance Patient");
        } else {
            if (frm.doc.discount > frm.doc.doctor_amount) {
                frappe.msgprint(__('Discount amount is greater than Consultation Charges'));
                frm.set_value("discount", doctor_amount);
            }
            frm.set_value("payable_amount", doctor_amount - discount);
            frm.refresh_field("payable_amount");
            console.log("Not Insurance");
        }
    },

    practitioner: function (frm) {
        let doctor_amount = frm.doc.doctor_amount || 0;
        let discount = frm.doc.discount || 0;
        let effective_amount = doctor_amount - discount
        let insurance_amount = (effective_amount * frm.doc.coverage_limits) / 100;
        let patient_amount = effective_amount - insurance_amount;

        if (frm.doc.discount < 0) {
            frappe.msgprint(__('Discount amount can not be below zero'));
            frm.set_value("discount", 0);
        }
        if (frm.doc.insurance_policy) {
            if (frm.doc.discount > patient_amount) {
                frappe.msgprint(__('Discount amount is greater than Patient Amount'));
                frm.set_value("discount", patient_amount);
            }
            frm.set_value("patient_amount", patient_amount);
            frm.set_value("insurance_coverage_amount", insurance_amount);
            frm.set_value("total_amount", patient_amount + insurance_amount);
            frm.set_value("payable_amount", patient_amount);
            frm.refresh_field("payable_amount");
            console.log("Insurance Patient");
        } else {
            if (frm.doc.discount > frm.doc.doctor_amount) {
                frappe.msgprint(__('Discount amount is greater than Consultation Charges'));
                frm.set_value("discount", doctor_amount);
            }
            frm.set_value("payable_amount", doctor_amount - discount);
            frm.refresh_field("payable_amount");
            console.log("Not Insurance");
        }

    },
    is_free: function (frm) {
        frm.set_value("payable_amount", 0)
    },

    bill_to_employee: function (frm) {
        if (frm.doc.bill_to_employee) {
            frm.set_value("payable_amount", 0);
            // frm.set_df_property("payable_amount", 'hidden', 1);
        } else {
            frm.set_value("payable_amount", frm.doc.doctor_amount - frm.doc.discount);
        }
    },

    discount: function (frm) {
        let doctor_amount = frm.doc.doctor_amount || 0;
        let discount = frm.doc.discount || 0;
        let effective_amount = doctor_amount - discount
        let insurance_amount = (effective_amount * frm.doc.coverage_limits) / 100;
        let patient_amount = effective_amount - insurance_amount;

        if (frm.doc.discount < 0) {
            frappe.msgprint(__('Discount amount can not be below zero'));
            frm.set_value("discount", 0);
        }
        if (doctor_amount) {
            if (frm.doc.insurance_policy) {
                if (frm.doc.discount > patient_amount) {
                    frappe.msgprint(__('Discount amount is greater than Patient Amount'));
                    frm.set_value("discount", patient_amount);
                }
                frm.set_value("patient_amount", patient_amount);
                frm.set_value("insurance_coverage_amount", insurance_amount);
                frm.set_value("total_amount", patient_amount + insurance_amount);
                frm.set_value("payable_amount", patient_amount);
                frm.refresh_field("payable_amount");
                console.log("Insurance Patient");
            } else {
                if (frm.doc.discount > frm.doc.doctor_amount) {
                    frappe.msgprint(__('Discount amount is greater than Consultation Charges'));
                    frm.set_value("discount", doctor_amount);
                }
                frm.set_value("payable_amount", doctor_amount - discount);
                frm.refresh_field("payable_amount");
                console.log("Not Insurance");
            }
        }

    },

});






































// frappe.require("/assets/rasiin_healthcare_insurance/js/insurance_utils.js", function () {
//     // The utility functions are available here after the file is loaded

//     frappe.ui.form.on('Que', {
//         onload: function (frm) {
//             frm.set_value("payable_amount", 0);
//         },

//         patient: function (frm) {
//             frm.set_value("payable_amount", 0)
//             frm.set_value("total_amount", 0)
//             frm.set_value("patient_amount", 0)
//             frm.set_value("insurance_coverage_amount", 0)
//             frm.expiry_message_shown = false;
//             validate_and_calculate_que(frm, true);
//             if (frm.doc.doctor_amount && frm.doc.insurance_coverage_amount) {
//                 frm.set_value("payable_amount", frm.doc.doctor_amount - frm.doc.insurance_coverage_amount);

//             } else {
//                 frm.set_value("payable_amount", frm.doc.doctor_amount);
//             }
//         },

//         practitioner: function (frm) {
//             frm.set_value("payable_amount", 0)
//             frm.set_value("total_amount", 0)
//             frm.set_value("patient_amount", 0)
//             frm.set_value("insurance_coverage_amount", 0)
//             validate_and_calculate_que(frm, false);
//             if (frm.doc.doctor_amount && frm.doc.insurance_coverage_amount) {
//                 frm.set_value("payable_amount", frm.doc.doctor_amount - frm.doc.insurance_coverage_amount);

//             } else {
//                 frm.set_value("payable_amount", frm.doc.doctor_amount);
//             }
//         },

//         discount: function (frm) {
//             // frm.set_value("payable_amount", 0)
//             validate_and_calculate_que(frm, false);
//             // if (frm.doc.discount) {
//             //     frm.set_value("patient_amount", frm.doc.doctor_amount - frm.doc.discount - frm.doc.insurance_coverage_amount);
//             // }
//             // if (frm.doc.doctor_amount && frm.doc.insurance_coverage_amount && frm.doc.discount) {
//             //     frm.set_value("payable_amount", 5);

//             // }
//         },

//         payable_amount: function (frm) {
//             validate_and_calculate_que(frm, false);
//         },

//         validate: function (frm) {
//             check_policy_expiry(frm, true);  // Now this will work
//         }
//     });

//     function validate_and_calculate_que(frm, show_message) {
//         if (check_policy_expiry(frm, show_message)) {
//             calculate_que_billing_amounts(frm);  // Both functions should be available here
//         } else {
//             frm.set_value("insurance_coverage_amount", 0);
//             // frm.set_value("payable_amount", frm.doc.doctor_amount - frm.doc.discount);
//         }
//     }

// });
