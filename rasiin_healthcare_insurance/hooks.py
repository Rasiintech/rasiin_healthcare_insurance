from . import __version__ as app_version

app_name = "rasiin_healthcare_insurance"
app_title = "Rasiin Healthcare Insurance"
app_publisher = "Ahmed Ibar"
app_description = "Healthcare Insurance App for Somalia."
app_email = "rasiintech@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
# include js in doctype views
doctype_js = {
    # "Sales Invoice" : "public/js/sales_invoice.js" , 
    "Patient" : "public/js/patient.js" ,  
    "Que" : "public/js/que.js" ,  
    "Sales Invoice" : "public/js/sales_invoice.js" ,  
    "Payment Entry" : "public/js/payment_entry.js" ,  
    # "Patient Appointment" : "public/js/patient_encounter.js" , 
    # "Patient Encounter" : "public/js/encounter_steps.js",
    # "Sample Collection": "public/js/sample.js",
    # "Inpatient Record": "public/js/inpatient_record.js"  
    }
doctype_list_js = {
        "Lab Result" : "public/js/lab_result_list.js" ,  
}
# include js, css files in header of desk.html
# app_include_css = "/assets/rasiin_healthcare_insurance/css/rasiin_healthcare_insurance.css"
# app_include_js = "/assets/rasiin_healthcare_insurance/js/rasiin_healthcare_insurance.js"

# include js, css files in header of web template
# web_include_css = "/assets/rasiin_healthcare_insurance/css/rasiin_healthcare_insurance.css"
# web_include_js = "/assets/rasiin_healthcare_insurance/js/rasiin_healthcare_insurance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "rasiin_healthcare_insurance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "rasiin_healthcare_insurance.utils.jinja_methods",
#	"filters": "rasiin_healthcare_insurance.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "rasiin_healthcare_insurance.install.before_install"
# after_install = "rasiin_healthcare_insurance.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "rasiin_healthcare_insurance.uninstall.before_uninstall"
# after_uninstall = "rasiin_healthcare_insurance.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "rasiin_healthcare_insurance.utils.before_app_install"
# after_app_install = "rasiin_healthcare_insurance.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "rasiin_healthcare_insurance.utils.before_app_uninstall"
# after_app_uninstall = "rasiin_healthcare_insurance.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rasiin_healthcare_insurance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    "Que": {
        # "after_insert": "rasiin_healthcare_insurance.api.que.create_que_order_bill",
        # "before_cancel": "rasiin_healthcare_insurance.api.cancel_que.cancel_linked_documents",
    },
    "Sales Invoice": {
        "on_submit": [
            # "rasiin_healthcare_insurance.api.patient_insurance_billing.update_payment_and_outstanding",
            "rasiin_healthcare_insurance.api.patient_insurance_billing.create_journal_entry_for_insurance",
            # "rasiin_healthcare_insurance.api.create_invoice_refund.handle_journal_entry_refund_invoice",
            "rasiin_healthcare_insurance.api.patient_insurance_billing.update_patient_amount",
            ],
        "before_cancel": [
          "rasiin_healthcare_insurance.api.make_cancel_queue.cancel_journal",  
        ],
    },
    "Payment Entry": {
        "on_submit": [
            "rasiin_healthcare_insurance.api.insurance_payment.update_sales_invoice_on_payment",
            "rasiin_healthcare_insurance.api.get_journal_entries_for_insurance_claim.update_insurance_claim_status",
            ],
        # "before_insert": "rasiin_healthcare_insurance.api.insurance_payment.update_sales_invoice_on_payment",
        "on_cancel": [
            "rasiin_healthcare_insurance.api.insurance_payment.reverse_sales_invoice_on_cancel",
            "rasiin_healthcare_insurance.api.get_journal_entries_for_insurance_claim.update_insurance_claim_status",
            
            ]
        
        # "before_save": "rasiin_healthcare_insurance.api.insurance_payment.update_sales_invoice_on_payment",
    },
    "Journal Entry": {
        # "on_submit": [
        #     "rasiin_healthcare_insurance.api.insurance_payment.update_sales_invoice_on_payment",
        #     "rasiin_healthcare_insurance.api.get_journal_entries_for_insurance_claim.update_insurance_claim_status",
        #     ],
        # "before_insert": "rasiin_healthcare_insurance.api.insurance_payment.update_sales_invoice_on_payment",
        # "on_cancel": "rasiin_healthcare_insurance.api.insurance_payment.reverse_sales_invoice_on_cancel"
        # "before_save": "rasiin_healthcare_insurance.api.insurance_payment.update_sales_invoice_on_payment",
    },
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"rasiin_healthcare_insurance.tasks.all",
    #     "rasiin_healthcare_insurance.rasiin_healthcare_insurance.doctype.insurance_policy.insurance_policy.auto_disable_expired_policies"
	# ],
    # "cron": {
    #     "* * * * *": [
    #         "rasiin_healthcare_insurance.rasiin_healthcare_insurance.doctype.insurance_policy.insurance_policy.auto_disable_expired_policies"
    #     ]
    # },
	"daily": [
		"rasiin_healthcare_insurance.rasiin_healthcare_insurance.doctype.insurance_policy.insurance_policy.auto_disable_expired_policies"
	],
	"hourly": [
		"rasiin_healthcare_insurance.rasiin_healthcare_insurance.doctype.insurance_policy.insurance_policy.auto_disable_expired_policies"
	],
#	"weekly": [
#		"rasiin_healthcare_insurance.tasks.weekly"
#	],
#	"monthly": [
#		"rasiin_healthcare_insurance.tasks.monthly"
#	],
}

# Testing
# -------

# before_tests = "rasiin_healthcare_insurance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "rasiin_healthcare_insurance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "rasiin_healthcare_insurance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["rasiin_healthcare_insurance.utils.before_request"]
# after_request = ["rasiin_healthcare_insurance.utils.after_request"]

# Job Events
# ----------
# before_job = ["rasiin_healthcare_insurance.utils.before_job"]
# after_job = ["rasiin_healthcare_insurance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"rasiin_healthcare_insurance.auth.validate"
# ]

fixtures = [
    {
        "doctype": doctype,
        "filters": [["module", "=", "Rasiin Healthcare Insurance"]]
    }
    for doctype in [
        "Client Script",
        "Server Script",
        "Custom Field",
        "Property Setter",
        "Print Format",
        # "Home Page"  # Uncomment if needed
    ]
] + [
    {"doctype": "Role Profile"}

]