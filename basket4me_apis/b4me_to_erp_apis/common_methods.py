import frappe
from frappe.utils import flt, cstr

def get_defaults():
    company = frappe.db.get_single_value('Global Defaults', 'default_company')
    currency = frappe.db.get_single_value('Global Defaults', 'default_currency')
    return frappe._dict({"company": company, "currency": currency})

def validate_item(item_code, item_name):
    if not item_code: frappe.throw(f"Item not Found in the Api Result.")
    found = frappe.db.get_value('Item', cstr(item_code).strip(), 'name')
    if not found:
        frappe.throw(f"Item '{item_code}:{item_name}' not Found in the System. Please Create and try again.")
        # doc = frappe.new_doc("Item")
        # doc.item_code = item_code or item_name
        # doc.item_name = item_name or item_code
        # doc.item_group = "All Item Groups"
        # doc.is_stock_item = 0
        # doc.flags.ignore_mandatory=True
        # doc.flags.ignore_permissions=True
        # doc.save()

def validate_uom(uom_name):
    if not uom_name: frappe.throw(f"UOM not Found in the Api Result.")
    found = frappe.db.get_value('UOM', cstr(uom_name).strip(), 'name')
    if not found:
        frappe.throw(f"UOM '{uom_name}' not Found in the System. Please Create and try again.")
        # doc = frappe.new_doc("UOM")
        # doc.uom_name = uom_name
        # doc.enabled = 1
        # doc.flags.ignore_mandatory=True
        # doc.flags.ignore_permissions=True
        # doc.save()

def validate_customer(customer):
    if not customer: frappe.throw(f"Customer not Found in the Api Result.")
    found = frappe.db.get_value('Customer', cstr(customer).strip(), 'name')
    if not found:
        frappe.throw(f"Customer '{customer}' not Found in the System. Please Create and try again.")
        # doc = frappe.new_doc("Customer")
        # doc.customer_name = customer
        # doc.customer_type = "Individual"
        # doc.flags.ignore_mandatory=True
        # doc.flags.ignore_permissions=True
        # doc.save()

def validate_mode_of_payment(mop):
    if not mop: frappe.throw(f"Mode of Payment not Found in the Api Result.")
    found = frappe.db.get_value('Mode of Payment', mop, 'name')
    if not found:
        frappe.throw(f"Mode of Payment '{mop}' not Found in the System. Please Create and try again.")
