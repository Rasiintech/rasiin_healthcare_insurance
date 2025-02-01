frappe.listview_settings['Lab Result'] = {
    onload: function(listview) {
        frappe.db.get_value("Healthcare Practitioner", {"user_id": frappe.session.user}, "name").then(r => {
            if (r.message && r.message.name) {
                let doctor = r.message.name;
                console.log("Logged-in Doctor:", doctor); // Debugging

                // ✅ Clear existing filters before adding new ones
                listview.filter_area.filter_list.clear_filters();

                // ✅ Apply multiple filters correctly
                var filters = [
                    ["Lab Result", "practitioner", "=", doctor],
                    ["Lab Result", "docstatus", "!=", 0],  // 0 = Draft
                    ["Lab Result", "docstatus", "!=", 2]   // 2 = Cancelled
                ];
                listview.filter_area.add(filters);

                // ✅ Add Volunteer Checkbox
                let checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.id = "volunteerCheckbox";
                checkbox.style.marginLeft = "10px";
                let label = document.createElement("label");
                label.innerHTML = " Volunteer";
                label.htmlFor = "volunteerCheckbox";

                listview.page.set_secondary_action(__("Toggle Practitioner Filter"), function() {
                    let isChecked = document.getElementById("volunteerCheckbox").checked;

                    // ✅ Clear existing filters before applying new ones
                    listview.filter_area.filter_list.clear_filters();

                    if (!isChecked) {
                        // ✅ Add practitioner filter if unchecked
                        listview.filter_area.add([
                            ["Lab Result", "practitioner", "=", doctor],
                            ["Lab Result", "docstatus", "!=", 0],  // 0 = Draft
                            ["Lab Result", "docstatus", "!=", 2]   // 2 = Cancelled
                        ]);
                    } else {
                        // ✅ Remove practitioner filter if checked (show all results except Draft & Cancelled)
                        listview.filter_area.add([
                            ["Lab Result", "docstatus", "!=", 0],
                            ["Lab Result", "docstatus", "!=", 2]
                        ]);
                    }
                });

                // ✅ Append checkbox to header
                listview.page.wrapper.querySelector(".page-actions").appendChild(checkbox);
                listview.page.wrapper.querySelector(".page-actions").appendChild(label);
            }
        });
    }
};
