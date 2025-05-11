import frappe
from frappe.utils import flt, cstr, getdate, now
from basket4me_apis.b4me_to_erp_apis.sales_order_apis import get_n_make_sales_orders
from basket4me_apis.b4me_to_erp_apis.sales_invoice_apis import get_n_make_sales_invoices
from basket4me_apis.b4me_to_erp_apis.payment_entry_apis import get_n_make_payment_entries

@frappe.whitelist()
def get_counts(doctype):
    Count=0
    if doctype:
        Count = frappe.db.count(doctype)
    frappe.local.response["data"] = Count

def get_b4me_settings():
    settings = frappe.get_single("Basket4Me APIs Integration Settings")
    if not settings.server_url: frappe.throw("Please set the Server URL in Basket4Me APIs Integration Settings")
    if not settings.api_key: frappe.throw("Please set the API Key in Basket4Me APIs Integration Settings")
    if not settings.store_code: frappe.throw("Please set the Store Code in Basket4Me APIs Integration Settings")
    return settings

def get_b4me_api_details(doctype, url_date=None):
    doc_wise_vars = {
        "Sales Order": {"path": "sales_order_api_path", "date": "sales_order_access_date"},
        "Sales Invoice": {"path": "sales_invoice_api_path", "date": "sales_invoice_access_date"},
        "Payment Entry": {"path": "receipts_api_path", "date": "receipts_access_date"},
    }
    if doctype not in doc_wise_vars: frappe.throw(f"Invalid doctype: {doctype}")
    sets = get_b4me_settings()
    url_path = sets.get(doc_wise_vars[doctype]["path"])
    if not url_path: frappe.throw(f"API path not set for {doctype} in Basket4Me APIs Integration Settings")
    # if not url_date: url_date = sets.get(doc_wise_vars[doctype]["date"])
    if not url_date: url_date = cstr(getdate())
    params = {
            "storeCode": sets.store_code,
            "accessDate": url_date,
            "page": 1
        }
    headers = {
        "accept": "application/json",
        "x-access-apikey": sets.api_key
    }
    return f"{sets.server_url}{url_path}", headers, params

def update_b4me_api_last_called(doctype):
    doc_wise_vars = {
        "Sales Order": "sales_order_last_called",
        "Sales Invoice": "sales_invoice_last_called",
        "Payment Entry": "receipts_last_called",
    }
    frappe.db.set_single_value("Basket4Me APIs Integration Settings", doc_wise_vars[doctype], now(), update_modified=False)
    frappe.db.commit()

@frappe.whitelist()
def make_payments_entry_api_call_background_job():
    frappe.enqueue(
        make_api_call,
        queue="long",
        timeout=5000,
        doctype="Payment Entry", date=getdate(),
    )

@frappe.whitelist()
def make_sales_order_api_call_background_job():
    frappe.enqueue(
        make_api_call,
        queue="long",
        timeout=5000,
        doctype="Sales Order", date=getdate(),
    )

@frappe.whitelist()
def make_sales_invoice_api_call_background_job():
    frappe.enqueue(
        make_api_call,
        queue="long",
        timeout=5000,
        doctype="Sales Invoice", date=getdate(),
    )

@frappe.whitelist()
def make_api_call_background_job(doctype, date):
    frappe.enqueue(
        make_api_call,
        queue="long",
        timeout=5000,
        doctype=doctype, date=date,
    )

@frappe.whitelist()
def make_api_call(doctype, date):
    doc_wise_funcs = {
        "Sales Order": get_n_make_sales_orders,
        "Sales Invoice": get_n_make_sales_invoices,
        "Payment Entry": get_n_make_payment_entries,
    }
    url, headers, params = get_b4me_api_details(doctype, date)
    get_n_make_func = doc_wise_funcs[doctype]
    total_count = get_n_make_func(url, headers, params, 1)
    api_call = 2
    while api_call <= total_count//10:
        get_n_make_func(url, headers, params, api_call)
        api_call += 1
    update_b4me_api_last_called(doctype)
    return
