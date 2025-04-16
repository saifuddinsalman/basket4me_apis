import frappe
import requests
from frappe.utils import flt, cstr, get_datetime, getdate
from basket4me_apis.b4me_to_erp_apis.common_methods import validate_customer, validate_mode_of_payment, get_defaults
from erpnext.accounts.doctype.payment_entry.payment_entry import get_party_details
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.setup.utils import get_exchange_rate

def get_customer_details(company, customer, date):
    return frappe._dict(get_party_details(
        company=company,
        party_type="Customer",
        party=customer,
        date=date
    ))
def get_n_make_payment_entries(url, headers, params, page):
    total_count = 0
    try:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            total_count = response.json().get("totalCount", 0) or 0
            data = response.json().get("data", [])
            for order in data:
                make_payment_entry(order)
        else:
            frappe.throw(f"Error fetching payment entries: {response.status_code} - {response.text}")
    except Exception as e:
        frappe.log_error("Basket4Me APIs Integration: Payment Entry Error", f"{cstr(e)}\n\n{frappe.get_traceback()}")
    return total_count


def make_payment_entry(api_data):
    try:
        validate_mode_of_payment(api_data["paymentType"])
        validate_customer(api_data["customerId"])
        defaults = get_defaults()
        date = get_datetime(api_data["tranDate"]).date()
        cus_det = get_customer_details(defaults.company, cstr(api_data["customerId"]).strip(), date)
        cash_bank = get_bank_cash_account(company=defaults.company, mode_of_payment=api_data["paymentType"]).get("account")
        pe = frappe.new_doc("Payment Entry")
        pe.company = defaults.company
        pe.payment_type = "Receive"
        pe.party_type = "Customer"
        pe.custom_tranrefno = api_data["tranRefNo"]
        pe.mode_of_payment = api_data["paymentType"]
        pe.party = cstr(api_data["customerId"]).strip()
        pe.party_account = cus_det.party_account
        pe.paid_from = cus_det.party_account
        pe.paid_to = cash_bank
        pe.posting_date = date
        pe.paid_amount = flt(api_data["amountPaid"])
        pe.received_amount = flt(api_data["amountPaid"])
        pe.reference_no = api_data["tranRefNo"]
        pe.reference_date = date
        pe.remarks = api_data.get("remark", "")
        pe.title = api_data["tranRefNo"]
        pe.target_exchange_rate = get_exchange_rate(transaction_date=date, from_currency=cus_det.party_account_currency, to_currency=defaults.currency)
        pe.source_exchange_rate = get_exchange_rate(transaction_date=date, from_currency=defaults.currency, to_currency=cus_det.party_account_currency)
        pe.flags.ignore_permissions=True
        pe.run_method("set_missing_values")
        pe.save()
        # payment_entry.submit()
    except Exception as e:
        frappe.log_error("Basket4Me APIs Integration: Payment Entry Creation Error", f"{cstr(e)}\n\n{frappe.get_traceback()}")
    frappe.db.commit()
