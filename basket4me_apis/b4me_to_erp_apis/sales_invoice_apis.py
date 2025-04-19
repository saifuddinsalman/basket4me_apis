import json
import frappe
import requests
from frappe.utils import flt, cstr, get_datetime, getdate
from basket4me_apis.b4me_to_erp_apis.common_methods import validate_customer, validate_item, validate_uom, get_defaults

def make_sales_invoice(api_data):
    try:
        products = json.loads(api_data["products"])
        validate_customer(api_data["customerId"], api_data, "Sales Invoice", api_data["tranRefNo"])
        defaults = get_defaults()
        si = frappe.new_doc("Sales Invoice")
        si.company = defaults.company
        si.custom_tranrefno = api_data["tranRefNo"]
        si.custom_basket4me_user = api_data["userName"]
        si.title = api_data["tranRefNo"]
        si.posting_date = get_datetime(api_data["tranDate"]).date()
        si.due_date = get_datetime(api_data["tranDate"]).date()
        si.customer = cstr(api_data["customerId"]).strip()
        si.remarks = api_data.get("remarks", "")
        si.po_no = api_data["tranRefNo"]
        si.po_date = get_datetime(api_data["tranDate"]).date()
        si.items = []
        for item in products:
            validate_item(item["productCode"], item["prodName"], "Sales Invoice", api_data["tranRefNo"])
            validate_uom(item["unit"], "Sales Invoice", api_data["tranRefNo"])
            si.append("items", {
                "item_code": item["productCode"],
                "item_name": item["prodName"],
                "description": item["prodName"],
                "qty": item["quantity"],
                "uom": item["unit"],
                "conversion_factor": item["unitFactor"],
                "rate": item["tranSPPrice"],
                "amount": item["amount"],
            })
        si.run_method("set_missing_values")
        si.run_method("calculate_taxes_and_totals")
        si.flags.ignore_permissions=True
        si.save()
        # si.submit()
    except Exception as e:
        frappe.log_error("Basket4Me APIs Integration: Sales Invoice Creation Error", f"{cstr(e)}\n\n{frappe.get_traceback()}")
    frappe.db.commit()


def get_n_make_sales_invoices(url, headers, params, page):
    total_count = 0
    try:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            total_count = response.json().get("totalCount", 0) or 0
            data = response.json().get("data", [])
            for invoice in data:
                make_sales_invoice(invoice)
        else:
            frappe.throw(f"Error fetching sales invoices: {response.status_code} - {response.text}")
    except Exception as e:
        frappe.log_error("Basket4Me APIs Integration: Sales Invoice Error", f"{cstr(e)}\n\n{frappe.get_traceback()}")
    return total_count
