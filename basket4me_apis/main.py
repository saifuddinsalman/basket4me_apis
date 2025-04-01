import frappe

@frappe.whitelist()
def get_counts(doctype):
    Count=0
    if doctype:
        Count = frappe.db.count(doctype)
    frappe.local.response["data"] = Count
