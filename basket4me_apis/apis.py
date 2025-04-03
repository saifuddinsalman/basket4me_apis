import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_customer_balance(customer=None):
    conds = ""
    if customer:
        conds += f" and party='{customer}' "
    data = frappe.db.sql(f"""Select
    party as customer, (SUM(debit)-SUM(credit)) as balance
    from `tabGL Entry` where docstatus=1 and is_cancelled = 0
    and party_type = 'Customer' {conds}
    group by customer""", as_dict=True)
    frappe.local.response["data"] = data

@frappe.whitelist()
def get_stock_balance(item=None, warehouse=None):
    data = []
    mapped_data = {}
    conds = ""
    if item:
        conds += f" and item_code='{item}' "
    if warehouse:
        conds += f" and warehouse='{warehouse}' "
    query_data = frappe.db.sql(f"""Select item_code, warehouse, actual_qty as qty
    from `tabBin` where 1=1 {conds} """, as_dict=True)
    for qd in query_data:
        if qd.item_code not in mapped_data:
            mapped_data[qd.item_code] = {}
        if qd.warehouse not in mapped_data[qd.item_code]:
            mapped_data[qd.item_code][qd.warehouse] = 0
        mapped_data[qd.item_code][qd.warehouse] += flt(qd.qty)
    for item_code, warehouses_wise_data in mapped_data.items():
        # total_qty = 0
        # for w, qty in warehouses_wise_data.items():
        #     total_qty += qty
        data.append({
            "item_code": item_code,
            # "total_qty": total_qty,
            "qty": warehouses_wise_data,
        })
    frappe.local.response["data"] = data
