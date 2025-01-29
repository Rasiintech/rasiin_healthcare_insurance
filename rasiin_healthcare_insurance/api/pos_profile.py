import frappe
from frappe import _

@frappe.whitelist()
def get_user_pos_profile():
    """Fetch the POS Profile and Mode of Payment for the logged-in user."""
    user = frappe.session.user

    # Fetch POS Profile assigned to the user
    pos_profile = frappe.db.get_value("POS Profile User", {"user": user}, "parent")
    if not pos_profile:
        frappe.throw(_("No POS Profile assigned to this user."))

    # Fetch the first mode of payment from POS Payment Method child table
    payment_mode = frappe.db.get_value("POS Payment Method", {"parent": pos_profile}, "mode_of_payment")

    return {
        "pos_profile": pos_profile,
        "mode_of_payment": payment_mode
    }
