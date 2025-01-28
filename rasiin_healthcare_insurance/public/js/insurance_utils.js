// // Shared function to check policy expiry and display messages
// function check_policy_expiry(frm, show_message) {
//     let expiry_date = frm.doc.expiry_date;
//     let current_date = frappe.datetime.get_today();
//     let grace_period_days = 7; // Example grace period

//     if (expiry_date && expiry_date < current_date) {
//         if (show_message && !frm.expiry_message_shown) {
//             frappe.msgprint({
//                 title: __('Policy Expired'),
//                 message: __('The insurance policy has expired. Coverage will not be applied.'),
//                 indicator: 'red'
//             });
//             frm.expiry_message_shown = true;
//         }
//         return false;
//     } else if (expiry_date && frappe.datetime.add_days(current_date, grace_period_days) >= expiry_date) {
//         if (show_message && !frm.expiry_message_shown) {
//             frappe.msgprint({
//                 title: __('Policy Near Expiry'),
//                 message: __('The insurance policy is near expiry. Please verify coverage.'),
//                 indicator: 'orange'
//             });
//             frm.expiry_message_shown = true;
//         }
//     }
//     return true;
// }

// // Function specific to Que for calculating billing amounts
// function calculate_que_billing_amounts(frm) {
//     let doctor_amount = frm.doc.doctor_amount || 0;
//     let discount = frm.doc.discount || 0;
//     let coverage_limits = frm.doc.coverage_limits || 0;
//     let insurance_coverage_amount = frm.doc.insurance_coverage_amount || 0;
//     let payable_amount = frm.doc.payable_amount || 0;
//     let patient_amount = frm.doc.patient_amount || 0;


//     // Validate discount
//     if (doctor_amount < discount) {
//         frappe.msgprint(__('Discount amount is greater than Consultation Charges'));
//         frm.set_value("discount", 0);
//         discount = 0;
//     }

//     let effective_amount = doctor_amount - discount;
//     if (effective_amount < 0) {
//         effective_amount = 0;
//     }
//     // if (frm.doc.practitioner) {
//     //     if (payable_amount > effective_amount) {
//     //         frappe.msgprint(__('The amount you want to pay is greater than the Total Amount Required for the Consultation Charges'));
//     //         frm.set_value("payable_amount", effective_amount);
//     //         payable_amount = effective_amount;
//     //     }
//     // }


//     // Calculate insurance coverage based on effective amount and coverage limits
//     insurance_coverage_amount = (doctor_amount * coverage_limits) / 100;
//     let patient_paid_amount = effective_amount - insurance_coverage_amount;

//     if (patient_paid_amount < 0) {
//         patient_paid_amount = 0;
//     }

//     // Set total amount
//     frm.set_value("total_amount", effective_amount);
//     frm.set_value("insurance_coverage_amount", insurance_coverage_amount);
//     frm.set_value("patient_amount", patient_paid_amount);

//     if (coverage_limits) {
//         // Check if the patient paid more than their payable amount
//         if (payable_amount > patient_paid_amount) {
//             let excess_payment = payable_amount - patient_paid_amount;
//             insurance_coverage_amount -= excess_payment;

//             if (insurance_coverage_amount < 0) {
//                 insurance_coverage_amount = 0;
//             }

//             if (patient_paid_amount - excess_payment < 0) {
//                 frm.set_value("patient_amount", 0);
//             } else {

//                 frm.set_value("patient_amount", patient_paid_amount - excess_payment);
//             }

//             // patient_paid_amount = effective_amount - insurance_coverage_amount;
//             frm.set_value("insurance_coverage_amount", insurance_coverage_amount);

//         }
//         // else if (discount && effective_amount - insurance_coverage_amount < 0) {
//         //     console.log("We need to update the insurance amount");

//         //     let excess_payment = (effective_amount - insurance_coverage_amount) * (-1);
//         //     insurance_coverage_amount -= excess_payment;

//         //     if (insurance_coverage_amount < 0) {
//         //         insurance_coverage_amount = 0;
//         //     }

//         //     patient_paid_amount = effective_amount - insurance_coverage_amount;
//         //     frm.set_value("insurance_coverage_amount", insurance_coverage_amount);
//         // }
//         else {
//             frm.set_value("insurance_coverage_amount", insurance_coverage_amount);
//         }
//     } else {
//         // No insurance case
//         frm.set_value("insurance_coverage_amount", 0);
//     }
// }

// // Function specific to Sales Invoice for calculating billing amounts
// function calculate_sales_invoice_billing_amounts(frm) {
//     let total = frm.doc.total || 0;
//     let discount_amount = frm.doc.discount_amount || 0;
//     let coverage_limits = frm.doc.coverage_limits || 0;
//     let insurance_coverage_amount = 0;
//     let paid_amount = frm.doc.payments[0]?.amount || 0;

//     // Validate discount
//     if (total > 0 && discount_amount > 0 && total < discount_amount) {
//         frappe.msgprint(__('Discount amount is greater than Grand Total.'));
//         frm.set_value("discount_amount", 0);
//         discount_amount = 0;
//     }

//     let effective_amount = total - discount_amount;
//     effective_amount = Math.max(effective_amount, 0);

//     // Calculate insurance coverage based on effective amount and coverage limits
//     insurance_coverage_amount = (total * coverage_limits) / 100;
//     let patient_paid_amount = effective_amount - insurance_coverage_amount;

//     // Ensure patient doesn't pay more than their payable amount
//     if (paid_amount > patient_paid_amount) {
//         let excess_payment = paid_amount - patient_paid_amount;
//         insurance_coverage_amount = Math.max(insurance_coverage_amount - excess_payment, 0);
//         patient_paid_amount = effective_amount - insurance_coverage_amount;
//     }

//     // Set calculated values
//     frm.set_value("insurance_coverage_amount", insurance_coverage_amount);
//     frm.set_value("payable_amount", patient_paid_amount);
// }
