import json
import frappe
import requests
from frappe.utils import flt, cstr, get_datetime, getdate
from basket4me_apis.b4me_to_erp_apis.common_methods import validate_customer, validate_item, validate_uom, get_defaults

def make_sales_order(api_data):
    try:
        products = json.loads(api_data["products"])
        validate_customer(api_data["customerId"])
        defaults = get_defaults()
        so = frappe.new_doc("Sales Order")
        so.company = defaults.company
        so.customer = cstr(api_data["customerId"]).strip()
        so.title = api_data["tranRefNo"]
        so.custom_tranrefno = api_data["tranRefNo"]
        so.transaction_date = get_datetime(api_data["tranDate"]).date()
        so.delivery_date = get_datetime(api_data["deliveryDate"]).date()
        so.po_no = api_data["tranRefNo"]
        so.po_date = get_datetime(api_data["tranDate"]).date()
        so.remarks = api_data.get("remarks", "")
        so.items = []
        for item in products:
            validate_item(item["productCode"], item["prodName"])
            validate_uom(item["unit"])
            so.append("items", {
                "item_code": item["productCode"],
                "item_name": item["prodName"],
                "description": item["prodName"],
                "qty": flt(item["quantity"]),
                "uom": item["unit"],
                "conversion_factor": flt(item["unitFactor"]),
                "rate": flt(item["tranSPPrice"]),
                "amount": flt(item["amount"]),
            })
        so.run_method("set_missing_values")
        so.run_method("calculate_taxes_and_totals")
        so.flags.ignore_permissions=True
        so.save()
        # so.submit()
    except Exception as e:
        frappe.log_error("Basket4Me APIs Integration: Sales Order Creation Error", f"{cstr(e)}\n\n{frappe.get_traceback()}")
    frappe.db.commit()


def get_n_make_sales_orders(url, headers, params, page):
    total_count = 0
    try:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            total_count = response.json().get("totalCount", 0) or 0
            data = response.json().get("data", [])
            for order in data:
                make_sales_order(order)
        else:
            frappe.throw(f"Error fetching sales orders: {response.status_code} - {response.text}")
    except Exception as e:
        frappe.log_error("Basket4Me APIs Integration: Sales Order Error", f"{cstr(e)}\n\n{frappe.get_traceback()}")
    return total_count
