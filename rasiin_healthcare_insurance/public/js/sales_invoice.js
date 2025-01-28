frappe.ui.form.on('Sales Invoice', {

    refresh: function (frm) {
        calculate_sales_invoice_billing_amounts(frm)
        if (frm.doc.coverage_limits == 100) {
            frm.set_value("is_pos", 0)
        }
    },

    additional_discount_percentage: function (frm) {
        calculate_sales_invoice_billing_amounts(frm);
    },

    discount_amount: function (frm) {
        calculate_sales_invoice_billing_amounts(frm);
    },

    is_pos: function (frm) {
        frm.set_value("bill_to_employee", 0)
        frm.set_value("employee", "")
        frm.set_value("is_inpatient", 0)
        frm.set_value("bill_to_patient", "")
    },

});

frappe.ui.form.on('Sales Invoice Item', {
    item_code: function (frm, cdt, cdn) {
        frappe.utils.debounce(() => {
            calculate_sales_invoice_billing_amounts(frm);
        }, 300)();
    },

    qty: function (frm) {
        frappe.utils.debounce(() => {
            calculate_sales_invoice_billing_amounts(frm);
        }, 300)();
    },

    rate: function (frm) {
        frappe.utils.debounce(() => {
            calculate_sales_invoice_billing_amounts(frm);
        }, 300)();
    },

    items_remove: function (frm) {
        frappe.utils.debounce(() => {
            calculate_sales_invoice_billing_amounts(frm);
        }, 300)();
    },
});

// Function specific to Sales Invoice for calculating billing amounts
function calculate_sales_invoice_billing_amounts(frm) {
    let total = frm.doc.total || 0;
    let grand_total = frm.doc.grand_total || 0
    let discount_amount = frm.doc.discount_amount || 0;
    let coverage_limits = frm.doc.coverage_limits || 0;
    let insurance_coverage_amount = 0;
    let paid_amount = frm.doc.payments[0]?.amount || 0;

    // Validate discount
    if (total > 0 && discount_amount > 0 && total < discount_amount) {
        frappe.msgprint(__('Discount amount is greater than Grand Total.'));
        frm.set_value("discount_amount", 0);
        discount_amount = 0;
    }

    let effective_amount = total - discount_amount;
    effective_amount = Math.max(effective_amount, 0);

    insurance_coverage_amount = (effective_amount * coverage_limits) / 100;
    let patient_paid_amount = effective_amount - insurance_coverage_amount;

    // Set calculated values
    frm.set_value("insurance_coverage_amount", insurance_coverage_amount);
    frm.set_value("payable_amount", patient_paid_amount);
}






































// frappe.require("/assets/rasiin_healthcare_insurance/js/insurance_utils.js", function () {

//     frappe.ui.form.on('Sales Invoice', {
//         onload: function (frm) {
//             // Perform insurance validation and calculation on load if needed
//         },

//         patient: function (frm) {
//             handleInsuranceDebounce(frm, false);
//         },

//         additional_discount_percentage: function (frm) {
//             handleInsuranceDebounce(frm, false);
//         },

//         discount_amount: function (frm) {
//             handleInsuranceDebounce(frm, false);
//         },

//         validate: function (frm) {
//             if (has_insurance(frm)) {
//                 check_policy_expiry(frm, true);
//             }
//         },
//     });

//     frappe.ui.form.on('Sales Invoice Item', {
//         item_code: function (frm, cdt, cdn) {
//             handleInsuranceDebounce(frm, false);
//         },

//         qty: function (frm) {
//             frappe.utils.debounce(() => {
//                 handleInsuranceDebounce(frm, false);
//             }, 300)();
//         },

//         rate: function (frm) {
//             frappe.utils.debounce(() => {
//                 handleInsuranceDebounce(frm, false);
//             }, 300)();
//         },

//         items_remove: function (frm) {
//             frappe.utils.debounce(() => {
//                 handleInsuranceDebounce(frm, false);
//             }, 300)();
//         },
//     });

//     frappe.ui.form.on('Sales Invoice Payment', {
//         amount: function (frm, cdt, cdn) {
//             frappe.utils.debounce(() => {
//                 handleInsuranceDebounce(frm, false);
//             }, 300)();
//         },

//         payments_remove: function (frm, cdt, cdn) {
//             frappe.utils.debounce(() => {
//                 handleInsuranceDebounce(frm, false);
//             }, 300)();
//         }
//     });

//     function handleInsuranceDebounce(frm, show_message) {
//         frappe.utils.debounce(() => {
//             if (has_insurance(frm)) {
//                 validate_and_calculate_invoice(frm, show_message);
//             }
//         }, 300)();
//     }

//     function has_insurance(frm) {
//         return frm.doc.insurance_company && frm.doc.coverage_limits > 0;
//     }

//     // Wrapper function for Sales Invoice
//     function validate_and_calculate_invoice(frm, show_message) {
//         if (check_policy_expiry(frm, show_message)) {
//             calculate_sales_invoice_billing_amounts(frm);
//         } else {
//             frm.set_value("insurance_coverage_amount", 0);
//             frm.set_value("payable_amount", frm.doc.total);
//         }
//     }

// });
// // Load the shared utility functions
// // frappe.require("/rasiin_healthcare_insurance/public/js/insurance_utils.js");
// // frappe.require("/assets/rasiin_healthcare_insurance/js/insurance_utils.js");
