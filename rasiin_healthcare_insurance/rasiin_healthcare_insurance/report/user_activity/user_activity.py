# Copyright (c) 2024, Ahmed Ibar and contributors
# For license information, please see license.txt

import frappe
import json

def execute(filters=None):
    report_type = filters.get("report_type", "Summary")
    
    if report_type == "Summary":
        columns = get_summary_columns()
        data = get_summary_data(filters)
    else:
        columns = get_detailed_columns()
        data = get_detailed_data(filters)
    
    return columns, data

def get_summary_columns():
    return [
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 150},
        {"label": "Count", "fieldname": "count", "fieldtype": "Int", "width": 100}
    ]

def get_detailed_columns():
    return [
        {"label": "Name", "fieldname": "name", "fieldtype": "Data", "width": 150},
        {"label": "Document Type", "fieldname": "ref_doctype", "fieldtype": "Data", "width": 150},
        {"label": "Document Name", "fieldname": "docname", "fieldtype": "Link", "options": "DocType", "width": 150},
        {"label": "Data", "fieldname": "data", "fieldtype": "Text", "width": 300},
        {"label": "Modified By", "fieldname": "modified_by", "fieldtype": "Data", "width": 150},
        {"label": "Modified", "fieldname": "modified", "fieldtype": "Datetime", "width": 150},
        {"label": "Docstatus", "fieldname": "docstatus", "fieldtype": "Data", "width": 100}
    ]
def get_summary_data(filters):
    conditions = ""

    # Date filter
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND v.modified BETWEEN %(from_date)s AND %(to_date)s"

    # Fetch logs
    query = f"""
        SELECT
            v.data
        FROM
            `tabVersion` v
        WHERE
            1=1 {conditions}
    """
    logs = frappe.db.sql(query, filters, as_dict=True)

    # Count statuses
    status_mapping = {
        0: "Draft",
        1: "Submitted",
        2: "Cancelled"
    }
    status_counts = {"Draft": 0, "Submitted": 0, "Cancelled": 0}

    for log in logs:
        try:
            # Parse JSON data
            data_json = json.loads(log["data"])
            changes = data_json.get("changed", [])
            
            # Extract the latest docstatus change if it exists
            docstatus = None
            for change in changes:
                if change[0] == "docstatus":  # Check if the field is `docstatus`
                    docstatus = change[2]  # Get the latest docstatus value
            
            # Map docstatus to a human-readable status and increment count
            if docstatus in status_mapping:
                status_counts[status_mapping[docstatus]] += 1
        except json.JSONDecodeError:
            continue

    # Convert to a list of dictionaries for the report
    summary_data = [{"status": status, "count": count} for status, count in status_counts.items()]
    return summary_data
def get_detailed_data(filters):
    conditions = ""

    # Date filter
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND v.modified BETWEEN %(from_date)s AND %(to_date)s"

    query = f"""
        SELECT
            v.name,
            v.ref_doctype,
            v.docname,
            v.data,
            v.modified_by,
            v.modified
        FROM
            `tabVersion` v
        WHERE
            1=1 {conditions}
        ORDER BY
            v.modified DESC
    """

    logs = frappe.db.sql(query, filters, as_dict=True)

    # Process detailed data
    detailed_data = []
    for log in logs:
        try:
            # Parse JSON data
            data_json = json.loads(log["data"])
            changes = data_json.get("changed", [])
            
            # Extract the latest docstatus change if it exists
            docstatus = None
            for change in changes:
                if change[0] == "docstatus":
                    docstatus = change[2]
            
            detailed_data.append({
                "name": log["name"],
                "ref_doctype": log["ref_doctype"],
                "docname": log["docname"],
                "data": log["data"],
                "modified_by": log["modified_by"],
                "modified": log["modified"],
                "docstatus": docstatus or "Unknown"
            })
        except json.JSONDecodeError:
            continue

    return detailed_data

# def get_columns():
#     return [
#         {"label": "Name", "fieldname": "name", "fieldtype": "Data", "width": 150},
#         {"label": "Document Type", "fieldname": "ref_doctype", "fieldtype": "Data", "width": 150},
#         {"label": "Document Name", "fieldname": "docname", "fieldtype": "Link", "options": "DocType", "width": 150},
#         {"label": "Data", "fieldname": "data", "fieldtype": "Text", "width": 300},
#         {"label": "Modified By", "fieldname": "modified_by", "fieldtype": "Data", "width": 150},
#         {"label": "Modified", "fieldname": "modified", "fieldtype": "Datetime", "width": 150},
#         {"label": "Docstatus", "fieldname": "docstatus", "fieldtype": "Data", "width": 100}
#     ]

# def get_user_activity(filters):
#     conditions = ""

#     # Date filter
#     if filters.get("from_date") and filters.get("to_date"):
#         conditions += " AND v.modified BETWEEN %(from_date)s AND %(to_date)s"

#     # Base query
#     query = f"""
#         SELECT
#             v.name,
#             v.ref_doctype,
#             v.docname,
#             v.data,
#             v.modified_by,
#             v.modified
#         FROM
#             `tabVersion` v
#         WHERE
#             1=1 {conditions}
#         ORDER BY
#             v.modified DESC
#     """

#     # Fetch logs
#     logs = frappe.db.sql(query, filters, as_dict=True)
    
#     # Process logs and apply status filter
#     parsed_logs = []
#     status_mapping = {
#         "Draft": 0,
#         "Submitted": 1,
#         "Cancelled": 2,
#         "Paid": 1,
#     }
#     required_docstatus = status_mapping.get(filters.get("status"))

#     for log in logs:
#         try:
#             # Parse JSON data
#             data_json = json.loads(log["data"])
#             changes = data_json.get("changed", [])
            
#             # Extract the latest docstatus change if it exists
#             docstatus = None
#             for change in changes:
#                 if change[0] == "docstatus":  # Check if the field is `docstatus`
#                     docstatus = change[2]  # Get the latest docstatus value
            
#             # Skip logs that do not match the selected status
#             if required_docstatus is not None and docstatus != required_docstatus:
#                 continue

#             # Append to parsed logs
#             parsed_log = {
#                 "name": log["name"],
#                 "ref_doctype": log["ref_doctype"],
#                 "docname": log["docname"],
#                 "data": log["data"],
#                 "modified_by": log["modified_by"],
#                 "modified": log["modified"],
#                 "docstatus": docstatus or "Unknown"  # Default to "Unknown" if not found
#             }
#             parsed_logs.append(parsed_log)
#         except json.JSONDecodeError:
#             # Skip if data is not valid JSON
#             continue

#     return parsed_logs
